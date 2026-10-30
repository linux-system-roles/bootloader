# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: MIT
# Assisted by Claude Code using model(s) Claude Fable 5.1, Claude Opus 5.5
#
"""Unit tests for the pbl backend of the bootloader_settings module"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import binascii
import hashlib
import os
import re
import shutil
import tempfile
import time
import unittest

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch

import bootloader_settings
from ansible.module_utils.bootloader_lsr import pbl

SHARED = {
    name: getattr(bootloader_settings, name)
    for name in [
        "validate_kernels",
        "get_setting_name",
        "get_replaced_args",
        "get_duplicate_present_option_names",
        "escapeval",
    ]
}
PARAMS = {
    "bootloader_settings": [],
    "transactional": False,
    "timeout": None,
    "password": None,
    "password_hash": None,
    "remove_password": False,
}
SUSE_CMDLINE = "rw quiet console=ttyS0,115200 console=tty0 selinux=1"
SUSE_KERNELS = [
    {
        "id": "simple",
        "title": "SLES",
        "index": "0",
        "kernel": "/boot/vmlinuz-1",
        "initrd": "/boot/initrd-1",
    },
    {
        "id": "adv>1",
        "title": "SLES, 1",
        "index": "1",
        "kernel": "/boot/vmlinuz-1",
        "initrd": "/boot/initrd-1",
    },
    {
        "id": "adv>1r",
        "title": "SLES, 1 (recovery mode)",
        "index": "2",
        "kernel": "/boot/vmlinuz-1",
        "initrd": "/boot/initrd-1",
    },
]


class Backend(unittest.TestCase):
    """test how the module hands over to the pbl backend"""

    def test_shared_helpers(self):
        module = MagicMock()
        module.exit_json.side_effect = SystemExit
        module.params = dict(PARAMS, backend="pbl")
        with patch.object(bootloader_settings, "AnsibleModule", return_value=module):
            with patch.object(pbl, "run") as run:
                with self.assertRaises(SystemExit):
                    bootloader_settings.run_module()
        self.assertEqual(SHARED, run.call_args[0][2])


class EditCmdline(unittest.TestCase):
    """test editing the GRUB command line with the pbl backend"""

    def edit(self, options, cmdline_default=SUSE_CMDLINE, cmdline_linux=""):
        return pbl.edit_cmdline(cmdline_default, cmdline_linux, options, SHARED)

    def test_present(self):
        self.assertEqual(
            (SUSE_CMDLINE + " audit=1", ""), self.edit([{"name": "audit", "value": 1}])
        )
        self.assertEqual((SUSE_CMDLINE, ""), self.edit([{"name": "quiet"}]))
        self.assertEqual(
            ("rw quiet console=ttyS0,115200 console=tty0 selinux=0", ""),
            self.edit([{"name": "selinux", "value": 0}]),
        )

    def test_repeated_key(self):
        self.assertEqual(
            (SUSE_CMDLINE, ""), self.edit([{"name": "console", "value": "tty0"}])
        )
        with self.assertRaises(ValueError) as error:
            self.edit([{"name": "console", "value": "ttyS1"}])
        self.assertIn("console appears 2 times", str(error.exception))
        self.assertEqual(
            ("rw quiet selinux=1 console=ttyS1 console=tty0", ""),
            self.edit(
                [
                    {"name": "console", "value": "ttyS1"},
                    {"name": "console", "value": "tty0"},
                ]
            ),
        )
        consoles = [
            {"name": "console", "value": "ttyS0,115200"},
            {"name": "console", "value": "tty0"},
        ]
        self.assertEqual(
            ("rw quiet selinux=1 console=ttyS0,115200 console=tty0", ""),
            self.edit(consoles, cmdline_linux="console=ttyS1"),
        )
        self.assertEqual(
            ("rw console=tty0", "console=ttyS0,115200"),
            self.edit(
                consoles,
                cmdline_default="rw console=tty0",
                cmdline_linux="console=ttyS0,115200",
            ),
        )

    def test_absent(self):
        self.assertEqual(
            ("rw quiet selinux=1", ""),
            self.edit([{"name": "console", "state": "absent"}]),
        )
        self.assertEqual(
            ("rw quiet console=ttyS0,115200 selinux=1", ""),
            self.edit([{"name": "console", "value": "tty0", "state": "absent"}]),
        )
        self.assertEqual(
            ("rw quiet selinux=1", "audit=1"),
            self.edit(
                [{"name": "console", "state": "absent"}],
                cmdline_linux="audit=1 console=ttyS0",
            ),
        )
        absent = [{"name": "console", "state": "absent"}]
        consoles = [
            {"name": "console", "value": "ttyS1"},
            {"name": "console", "value": "tty1"},
        ]
        for options in [absent + consoles, consoles + absent]:
            cmdline = self.edit(options)
            self.assertEqual(
                ("rw quiet selinux=1 console=ttyS1 console=tty1", ""), cmdline
            )
            self.assertEqual(cmdline, self.edit(options, *cmdline))

    def test_absent_and_present(self):
        """A name that is removed and set in one list keeps its place on a second run"""
        absent_first = [
            {"name": "console", "state": "absent"},
            {"name": "console", "value": "ttyS1"},
            {"name": "audit", "value": 1},
        ]
        for options in [absent_first, absent_first[::-1]]:
            cmdline = self.edit(options)
            self.assertEqual(("rw quiet selinux=1 console=ttyS1 audit=1", ""), cmdline)
            self.assertEqual(cmdline, self.edit(options, *cmdline))

    def test_cmdline_linux(self):
        self.assertEqual(
            (SUSE_CMDLINE, "audit=1"),
            self.edit([{"name": "audit", "value": 1}], cmdline_linux="audit=1"),
        )
        self.assertEqual(
            (SUSE_CMDLINE + " audit=1", "quiet"),
            self.edit([{"name": "audit", "value": 1}], cmdline_linux="audit=0 quiet"),
        )

    def test_split_key(self):
        """A key with different values in the two variables is refused"""
        split = {
            "cmdline_default": SUSE_CMDLINE + " audit=0",
            "cmdline_linux": "audit=1",
        }
        for value in [1, 0]:
            with self.assertRaises(ValueError):
                self.edit([{"name": "audit", "value": value}], **split)
        options = [{"name": "audit", "state": "absent"}, {"name": "audit", "value": 1}]
        for options in [options, options[::-1]]:
            result = self.edit(options, **split)
            self.assertEqual((SUSE_CMDLINE + " audit=1", ""), result)
            self.assertEqual(result, self.edit(options, *result))
        self.assertEqual(
            (SUSE_CMDLINE + " audit=1", "audit=1"),
            self.edit(
                [{"name": "audit", "value": 1}],
                cmdline_default=SUSE_CMDLINE + " audit=1",
                cmdline_linux="audit=1",
            ),
        )

    def test_replaced(self):
        options = [{"previous": "replaced"}, {"name": "rw"}, {"name": "quiet"}]
        self.assertEqual(("rw quiet", ""), self.edit(options))
        self.assertEqual(
            ("quiet rw", ""), self.edit(options, cmdline_default="quiet rw")
        )

    def test_unsafe_options(self):
        module = MagicMock()
        module.fail_json.side_effect = SystemExit
        for value in ["a b", "a\nb", "$y", 'a"', "a|b", "a&b", "a<b", "a>b"]:
            with self.assertRaises(SystemExit):
                pbl.validate_options(module, [{"name": "x", "value": value}])
        for name in ["x;y", "x{", "x}", "#x"]:
            with self.assertRaises(SystemExit):
                pbl.validate_options(module, [{"name": name}])
        pbl.validate_options(
            module,
            [{"name": "console", "value": "ttyS0,115200"}, {"previous": "replaced"}],
        )

    def test_quoted_cmdline(self):
        module = MagicMock()
        module.fail_json.side_effect = SystemExit
        default_grub = "GRUB_CMDLINE_LINUX_DEFAULT='quiet dyndbg=\"file foo.c +p\"'\n"
        self.assertEqual(
            default_grub,
            pbl.edit_default_grub(module, default_grub, [{"name": "quiet"}], SHARED),
        )
        with self.assertRaises(SystemExit):
            pbl.edit_default_grub(
                module, default_grub, [{"name": "audit", "value": 1}], SHARED
            )
        self.assertEqual(
            'GRUB_CMDLINE_LINUX_DEFAULT="quiet audit=1"\n',
            pbl.edit_default_grub(
                module,
                'GRUB_CMDLINE_LINUX_DEFAULT="quiet"\n',
                [{"name": "audit", "value": 1}],
                SHARED,
            ),
        )

    def test_find_entry(self):
        module = MagicMock()
        module.fail_json.side_effect = SystemExit
        for selector, entry_id in [
            ({"path": "/boot/vmlinuz-1"}, "adv>1"),
            ({"index": 0}, "simple"),
            ({"path": "/boot/vmlinuz-1", "title": "SLES, 1"}, "adv>1"),
            (
                {
                    "path": "/boot/vmlinuz-1",
                    "title": "SLES, 1",
                    "initrd": "/boot/initrd-1",
                },
                "adv>1",
            ),
        ]:
            self.assertEqual(
                entry_id, pbl.find_entry(module, SUSE_KERNELS, selector)["id"]
            )
        with self.assertRaises(SystemExit):
            pbl.find_entry(module, SUSE_KERNELS, {"title": "nope"})

    def test_password(self):
        salt = bytes(bytearray([0, 1, 2, 3]))
        digest = hashlib.pbkdf2_hmac("sha512", b"test-pass", salt, 2, 4)
        password_hash = "grub.pbkdf2.sha512.2.00010203.%s" % (
            binascii.hexlify(digest).decode("ascii").upper()
        )
        self.assertTrue(pbl.password_matches("test-pass", password_hash))
        self.assertFalse(pbl.password_matches("other", password_hash))
        self.assertFalse(pbl.password_matches("test-pass", None))
        self.assertIn(
            "password_pbkdf2 root " + password_hash,
            pbl.get_password_script(password_hash),
        )


class PasswordScript(unittest.TestCase):
    """test the grub.d script that holds the password with the pbl backend"""

    password_hash = "grub.pbkdf2.sha512.10000.AB.CD"

    def setUp(self):
        self.grub_d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.grub_d)
        self.script = os.path.join(self.grub_d, "01_password")
        patcher = patch.object(pbl.grub, "PASSWORD_SCRIPT", self.script)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.module = MagicMock(check_mode=False)
        self.module.fail_json.side_effect = SystemExit
        self.module.params = dict(PARAMS)
        self.result = {"actions": []}
        self.default_grub = ""

    def write(self, path, content, mode):
        with open(path, "w") as f:
            f.write(content)
        os.chmod(path, mode)

    def edit(self):
        return pbl.edit_password_script(self.module, self.result, self.default_grub)

    def test_unset_leaves_script(self):
        script = "#!/bin/sh\necho 'set superusers=\"admin\"'\n"
        self.write(self.script, script, 0o755)
        self.assertFalse(self.edit())
        self.assertEqual([], self.result["actions"])
        with open(self.script) as f:
            self.assertEqual(script, f.read())

    def test_mode(self):
        self.module.params["password_hash"] = self.password_hash
        script = pbl.get_password_script(self.password_hash)
        self.write(self.script, script, 0o644)
        self.assertTrue(self.edit())
        self.assertEqual(["chmod 0700 " + self.script], self.result["actions"])
        self.assertEqual(0o700, os.stat(self.script).st_mode & 0o7777)
        self.assertFalse(self.edit())

    def test_other_password_script(self):
        other = os.path.join(self.grub_d, "42_password")
        self.write(other, "#!/bin/sh\necho 'set superusers=\"root\"'\n", 0o755)
        for params in [
            {"password_hash": self.password_hash},
            {"remove_password": True},
        ]:
            self.module.params.update(params)
            with self.assertRaises(SystemExit):
                self.edit()
            self.assertIn(
                "42_password also sets", self.module.fail_json.call_args[1]["msg"]
            )
        # grub2-mkconfig runs only executable scripts
        os.chmod(other, 0o644)
        self.assertFalse(self.edit())

    def test_grub_users(self):
        self.default_grub = 'GRUB_TIMEOUT=8\nGRUB_USERS="root;0;pbkdf2;%s"\n' % (
            self.password_hash
        )
        for params in [
            {"password_hash": self.password_hash},
            {"password_hash": None, "remove_password": True},
        ]:
            self.module.params.update(params)
            with self.assertRaises(SystemExit):
                self.edit()
            self.assertIn("GRUB_USERS in", self.module.fail_json.call_args[1]["msg"])
        self.default_grub = 'GRUB_USERS=""\n'
        self.module.params.update(
            {"password_hash": self.password_hash, "remove_password": False}
        )
        self.module.check_mode = True
        self.assertTrue(self.edit())


class RebootRequired(unittest.TestCase):
    """test what a run applies and when it asks for a reboot"""

    def setUp(self):
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root)
        self.paths = {}
        for name, path in [
            ("DEFAULT_GRUB", "etc/default/grub"),
            ("PASSWORD_SCRIPT", "etc/grub.d/01_password"),
            ("GRUB_CFG", "boot/grub2/grub.cfg"),
            ("GRUBENV", "boot/grub2/grubenv"),
        ]:
            self.paths[name] = os.path.join(root, path)
            if not os.path.isdir(os.path.dirname(self.paths[name])):
                os.makedirs(os.path.dirname(self.paths[name]))
        now = time.time()
        self.write(
            "DEFAULT_GRUB",
            "GRUB_DEFAULT=0\nGRUB_TIMEOUT=8\n"
            'GRUB_CMDLINE_LINUX_DEFAULT="%s"\n' % SUSE_CMDLINE,
            now - 100,
        )
        self.write("GRUB_CFG", self.menu(), now - 50)
        patcher = patch.multiple(
            pbl.grub,
            check_loader=MagicMock(),
            get_next_boot_root=MagicMock(return_value="/"),
            get_kernels=MagicMock(return_value=SUSE_KERNELS),
            **self.paths
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.module = MagicMock(check_mode=False)
        self.module.fail_json.side_effect = SystemExit
        self.module.atomic_move.side_effect = os.rename
        self.module.run_command.side_effect = self.run_command
        self.module.params = dict(PARAMS)

    def write(self, name, content, mtime):
        with open(self.paths[name], "w") as f:
            f.write(content)
        os.utime(self.paths[name], (mtime, mtime))

    def menu(self):
        """Get what grub2-mkconfig would write to grub.cfg, in short"""
        with open(self.paths["DEFAULT_GRUB"]) as f:
            default_grub = f.read()
        grub_default, timeout, cmdline = [
            pbl.grub.get_shell_var(default_grub, name)
            for name in ["GRUB_DEFAULT", "GRUB_TIMEOUT", "GRUB_CMDLINE_LINUX_DEFAULT"]
        ]
        if grub_default == "saved":
            grub_default = "${saved_entry}"
        menu = (
            'set default="%s"\nset timeout=%s\n'
            "menuentry 'SLES' $menuentry_id_option 'simple' {\n"
            "\tlinux /boot/vmlinuz-1 root=UUID=1 %s\n}\n"
            % (grub_default, timeout, cmdline)
        )
        script = self.paths["PASSWORD_SCRIPT"]
        if os.path.isfile(script) and os.access(script, os.X_OK):
            with open(script) as f:
                password = re.search(r"password_pbkdf2 root [^\s\"]+", f.read())
            menu += "### BEGIN %s ###\n%s\n### END %s ###\n" % (
                script,
                password.group(0) if password else "",
                script,
            )
        return menu

    def run_command(self, cmd, **kwargs):
        if cmd[0] == "grub2-set-default":
            with open(self.paths["GRUBENV"], "w") as f:
                f.write("saved_entry=%s\n" % cmd[1])
        elif cmd[-1] in ["--config", "grub.cfg"]:
            with open(self.paths["GRUB_CFG"], "w") as f:
                f.write(self.menu())
        return 0, "", ""

    def run_pbl(self, **params):
        self.module.params.update(params)
        result = {"actions": []}
        pbl.run(self.module, result, SHARED)
        return result

    def test_timeout(self):
        result = self.run_pbl(timeout=7)
        self.assertEqual(
            ["update " + self.paths["DEFAULT_GRUB"], "pbl --config"],
            result["actions"],
        )
        self.assertFalse(result["reboot_required"])
        result = self.run_pbl(timeout=9, transactional=True)
        self.assertEqual(
            [
                "update " + self.paths["DEFAULT_GRUB"],
                "transactional-update --continue --non-interactive grub.cfg",
            ],
            result["actions"],
        )
        self.assertTrue(result["reboot_required"])

    def test_password(self):
        script = self.paths["PASSWORD_SCRIPT"]
        result = self.run_pbl(password_hash=PasswordScript.password_hash)
        self.assertEqual(["update " + script, "pbl --config"], result["actions"])
        self.assertFalse(result["reboot_required"])
        result = self.run_pbl(password_hash=None, remove_password=True)
        self.assertEqual(["remove " + script, "pbl --config"], result["actions"])
        self.assertFalse(result["reboot_required"])

    def test_default(self):
        by_path = [{"kernel": {"path": "/boot/vmlinuz-1"}, "default": True}]
        result = self.run_pbl(bootloader_settings=by_path)
        self.assertIn("grub2-set-default 'adv>1'", result["actions"])
        self.assertTrue(result["reboot_required"])
        # a selector with several keys names one of the entries of a kernel
        by_keys = [
            {
                "kernel": {
                    "path": "/boot/vmlinuz-1",
                    "title": "SLES, 1",
                    "initrd": "/boot/initrd-1",
                },
                "default": True,
            }
        ]
        result = self.run_pbl(bootloader_settings=by_keys)
        self.assertEqual([], result["actions"])
        self.assertFalse(result["reboot_required"])

    def test_refused_settings(self):
        """Boot entries cannot be added or removed, or get arguments of their own"""
        new_entry = {
            "path": "/boot/vmlinuz-2",
            "title": "SLES, 2",
            "initrd": "/boot/initrd-2",
        }
        for setting, message in [
            ({"kernel": {"title": "SLES, 1"}, "state": "absent"}, "Adding or removing"),
            ({"kernel": new_entry}, "Adding or removing"),
            (
                {"kernel": {"title": "SLES, 1"}, "options": [{"name": "audit"}]},
                "Per-entry kernel arguments",
            ),
        ]:
            with self.assertRaises(SystemExit):
                self.run_pbl(bootloader_settings=[setting])
            self.assertIn(message, self.module.fail_json.call_args[1]["msg"])

    def test_stale(self):
        """A menu older than its sources is regenerated, without a reboot"""
        now = time.time()
        os.utime(self.paths["DEFAULT_GRUB"], (now - 10, now - 10))
        result = self.run_pbl(timeout=8)
        self.assertEqual(["pbl --config"], result["actions"])
        self.assertFalse(result["reboot_required"])

    def test_future_mtime(self):
        """A source dated ahead of the clock regenerates once, not on every run"""
        future = time.time() + 3600
        os.utime(self.paths["DEFAULT_GRUB"], (future, future))
        # check mode reports the regeneration and leaves the date as it is
        self.module.check_mode = True
        self.assertEqual(["pbl --config"], self.run_pbl(timeout=8)["actions"])
        self.assertGreater(os.path.getmtime(self.paths["DEFAULT_GRUB"]), time.time())
        self.module.check_mode = False
        result = self.run_pbl(timeout=8)
        self.assertEqual(["pbl --config"], result["actions"])
        self.assertFalse(result["reboot_required"])
        self.assertLess(os.path.getmtime(self.paths["DEFAULT_GRUB"]), future)
        self.assertEqual([], self.run_pbl(timeout=8)["actions"])

    def test_other_form_of_password_script(self):
        """A script that prints the same hash in another form leaves the menu as it is"""
        self.write(
            "PASSWORD_SCRIPT",
            '#!/bin/sh\necho "password_pbkdf2 root %s"\n'
            % PasswordScript.password_hash,
            time.time() - 200,
        )
        os.chmod(self.paths["PASSWORD_SCRIPT"], 0o700)
        self.write("GRUB_CFG", self.menu(), time.time() - 50)
        self.assertEqual([], self.run_pbl(timeout=8)["actions"])

    def test_missing_default_grub(self):
        """Without /etc/default/grub the role refuses to apply anything"""
        os.unlink(self.paths["DEFAULT_GRUB"])
        with self.assertRaises(SystemExit):
            self.run_pbl(timeout=7)
        self.assertIn("does not exist", self.module.fail_json.call_args[1]["msg"])
        self.assertEqual([], self.run_pbl(timeout=None)["actions"])

    def test_check_mode(self):
        self.module.check_mode = True
        with open(self.paths["DEFAULT_GRUB"]) as f:
            default_grub = f.read()
        result = self.run_pbl(
            timeout=7,
            bootloader_settings=[
                {"kernel": "ALL", "options": [{"name": "audit", "value": 1}]}
            ],
        )
        self.assertEqual(
            ["update " + self.paths["DEFAULT_GRUB"], "pbl --config"],
            result["actions"],
        )
        self.assertTrue(result["reboot_required"])
        # a new default entry is recorded, and not read back from grubenv
        by_path = [{"kernel": {"path": "/boot/vmlinuz-1"}, "default": True}]
        result = self.run_pbl(bootloader_settings=by_path)
        self.assertIn("grub2-set-default 'adv>1'", result["actions"])
        self.module.run_command.assert_not_called()
        with open(self.paths["DEFAULT_GRUB"]) as f:
            self.assertEqual(default_grub, f.read())
