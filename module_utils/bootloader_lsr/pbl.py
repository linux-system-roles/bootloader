# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: MIT
#
"""Apply boot loader settings where pbl manages a grub2-mkconfig configuration, as on SUSE"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import binascii
import hashlib
import os
import re
import time

from ansible.module_utils.bootloader_lsr import grub

UNSAFE_ARG = re.compile(r"[\s\"'$`;\\{}|&<>#]")
PASSWORD_HASH = re.compile(
    r"^grub\.pbkdf2\.sha512\.(\d+)\.([0-9A-Fa-f]+)\.([0-9A-Fa-f]+)$"
)
# a literal user list or hash; grub2 2.16's 00_header echoes both from variables
PASSWORD_SOURCE = re.compile(
    r"superusers\s*=\s*\\?[\"']?[^$\"'\s\\]|password_pbkdf2\s+\S+\s+[^$\s]"
)


def arg_key(token):
    """Get the name of a kernel argument token"""
    return token.split("=", 1)[0]


def validate_options(module, bootloader_setting_options):
    """Refuse kernel arguments that GRUB's script parser would interpret"""
    for kernel_setting in bootloader_setting_options:
        for key in ["name", "value"]:
            if key in kernel_setting and UNSAFE_ARG.search(str(kernel_setting[key])):
                module.fail_json(
                    msg="Kernel argument %s '%s' must not contain whitespace, quotes "
                    "or any of $ ` ; \\ { } | & < > #" % (key, kernel_setting[key])
                )


def get_absent_and_present_option_names(bootloader_setting_options, shared):
    """Return option names removed without a value and also set in the same list"""
    removed = set()
    present = set()
    for kernel_setting in bootloader_setting_options:
        if not shared["get_setting_name"](kernel_setting):
            continue
        if kernel_setting.get("state", "present") != "absent":
            present.add(kernel_setting["name"])
        elif "value" not in kernel_setting:
            removed.add(kernel_setting["name"])
    return removed & present


def edit_cmdline(cmdline_default, cmdline_linux, bootloader_setting_options, shared):
    """Apply options to the GRUB_CMDLINE_LINUX_DEFAULT and GRUB_CMDLINE_LINUX arguments"""
    tokens = cmdline_default.split()
    linux_tokens = cmdline_linux.split()
    if {"previous": "replaced"} in bootloader_setting_options and sorted(
        tokens
    ) != shared["get_replaced_args"](bootloader_setting_options):
        tokens = []
    duplicate_names = shared["get_duplicate_present_option_names"](
        bootloader_setting_options
    )
    duplicate_names |= get_absent_and_present_option_names(
        bootloader_setting_options, shared
    )
    for name in duplicate_names:
        expected_tokens = []
        for kernel_setting in bootloader_setting_options:
            if (
                kernel_setting.get("name") == name
                and kernel_setting.get("state", "present") != "absent"
            ):
                arg = shared["get_setting_name"](kernel_setting)
                if arg not in expected_tokens:
                    expected_tokens.append(arg)
        # normal entries boot with GRUB_CMDLINE_LINUX, then GRUB_CMDLINE_LINUX_DEFAULT
        if [t for t in linux_tokens + tokens if arg_key(t) == name] != expected_tokens:
            linux_tokens = [t for t in linux_tokens if arg_key(t) != name]
            tokens = [t for t in tokens if arg_key(t) != name] + expected_tokens

    for kernel_setting in bootloader_setting_options:
        setting_name = shared["get_setting_name"](kernel_setting)
        if not setting_name:
            continue
        name = kernel_setting["name"]
        if kernel_setting.get("state", "present") == "absent":
            if "value" in kernel_setting:
                tokens = [t for t in tokens if t != setting_name]
                linux_tokens = [t for t in linux_tokens if t != setting_name]
            # the values listed for a repeated or re-set name already replace every value
            elif name not in duplicate_names:
                tokens = [t for t in tokens if arg_key(t) != name]
                linux_tokens = [t for t in linux_tokens if arg_key(t) != name]
        elif name in duplicate_names:
            continue
        elif setting_name in tokens + linux_tokens:
            # the last value wins at boot, and it may come from the other line
            values = [
                {t for t in line if arg_key(t) == name}
                for line in [linux_tokens, tokens]
            ]
            if all(values) and values[0] != values[1]:
                raise ValueError(
                    "%s has different values in GRUB_CMDLINE_LINUX and "
                    "GRUB_CMDLINE_LINUX_DEFAULT; remove it with state: absent first, "
                    "or list every value if it should have several" % name
                )
            continue
        else:
            same_key = [t for t in tokens + linux_tokens if arg_key(t) == name]
            if len(same_key) > 1:
                raise ValueError(
                    "%s appears %d times on the kernel command line; list every "
                    "value it should have, or remove it with state: absent first"
                    % (name, len(same_key))
                )
            linux_tokens = [t for t in linux_tokens if arg_key(t) != name]
            if same_key and same_key[0] in tokens:
                tokens[tokens.index(same_key[0])] = setting_name
            else:
                tokens.append(setting_name)
    return " ".join(tokens), " ".join(linux_tokens)


def entry_matches(kernel, bootloader_setting_kernel):
    """Whether a menu entry matches every key of a kernel selector"""
    fields = {
        "path": kernel.get("path", kernel.get("kernel")),
        "title": kernel["title"],
        "index": kernel["index"],
        "initrd": kernel.get("initrd"),
    }
    return all(
        str(value) == fields.get(key)
        for key, value in bootloader_setting_kernel.items()
    )


def find_entry(module, kernels, bootloader_setting_kernel):
    """Find the menu entry a kernel selector refers to, preferring a kernel's own entry"""
    matches = [k for k in kernels if entry_matches(k, bootloader_setting_kernel)]
    if not matches:
        module.fail_json(
            msg="No boot entry matches kernel %s" % bootloader_setting_kernel
        )
    matches.sort(key=lambda k: (">" not in k["id"], "(recovery mode)" in k["title"]))
    return matches[0]


def set_default_entry(entry, default_grub, grubenv, grubenv_exists, commands):
    """Make a menu entry the saved default, switching GRUB_DEFAULT to saved if needed"""
    if grub.get_shell_var(default_grub, "GRUB_DEFAULT") != "saved":
        default_grub = grub.set_shell_var(default_grub, "GRUB_DEFAULT", "saved")
    if not grubenv_exists:
        commands.append(["grub2-editenv", grub.GRUBENV, "create"])
    if grubenv.get("saved_entry") != entry["id"]:
        commands.append(["grub2-set-default", entry["id"]])
        grubenv["saved_entry"] = entry["id"]
    return default_grub


def password_matches(password, password_hash):
    """Check a password against a GRUB PBKDF2 SHA512 hash"""
    match = PASSWORD_HASH.match(password_hash or "")
    if not match:
        return False
    iterations, salt, digest = match.groups()
    computed = hashlib.pbkdf2_hmac(
        "sha512",
        password.encode("utf-8"),
        binascii.unhexlify(salt),
        int(iterations),
        len(digest) // 2,
    )
    return binascii.hexlify(computed).decode("ascii").upper() == digest.upper()


def get_password_script(password_hash):
    """Get the grub.d script that protects the boot loader with a password"""
    return (
        "#!/bin/sh\n"
        "cat <<'EOF'\n"
        'set superusers="root"\n'
        "export superusers\n"
        "password_pbkdf2 root %s\n"
        # entries boot without the password, as with --unrestricted elsewhere
        'set unrestricted_menu="y"\n'
        "export unrestricted_menu\n"
        "EOF\n" % password_hash
    )


def get_password_hash(module, current_hash):
    """Get the password hash to configure, or None to remove the password"""
    if module.params["remove_password"]:
        return None
    if module.params["password_hash"] is not None:
        if not PASSWORD_HASH.match(module.params["password_hash"]):
            module.fail_json(msg="password_hash must be a GRUB PBKDF2 SHA512 hash")
        return module.params["password_hash"]
    password = module.params["password"]
    if password_matches(password, current_hash):
        return current_hash
    if module.check_mode:
        return "grub.pbkdf2.sha512.0.00.00"
    _unused, stdout, _unused = module.run_command(
        ["grub2-mkpasswd-pbkdf2"],
        data="%s\n%s" % (password, password),
        environ_update={"LC_ALL": "C"},
        check_rc=True,
    )
    new_hash = re.search(r"(grub\.pbkdf2\.sha512\.\S+)", stdout)
    if not new_hash:
        module.fail_json(msg="Cannot generate a boot loader password hash")
    return new_hash.group(1)


def is_stale(root):
    """Whether the GRUB configuration is behind the files it is generated from"""
    grub_cfg = grub.next_boot_path(root, grub.GRUB_CFG)
    if not os.path.exists(grub_cfg):
        return True
    generated = os.path.getmtime(grub_cfg)
    if any(
        os.path.exists(path) and os.path.getmtime(path) > generated
        for path in [grub.DEFAULT_GRUB, grub.PASSWORD_SCRIPT]
    ):
        return True
    # a chmod, a removal or an older copy leaves no newer modification time
    menu = grub.read_file(grub_cfg)
    script = grub.PASSWORD_SCRIPT
    runs = os.path.isfile(script) and os.access(script, os.X_OK)
    if runs != ("### BEGIN %s ###" % script in menu):
        return True
    password = re.search(
        r"password_pbkdf2 root grub\.pbkdf2\.sha512\.[0-9A-Fa-f.]+",
        grub.read_file(script),
    )
    lines = [line.strip() for line in menu.splitlines()]
    return bool(runs and password) and password.group(0) not in lines


def get_boot_menu(root):
    """Get the kernel command lines and the default entry setting of the GRUB menu"""
    grub_cfg = grub.read_file(grub.next_boot_path(root, grub.GRUB_CFG))
    cmdlines = {k["args"] for k in grub.get_grub_cfg_facts(grub_cfg, None, None)}
    defaults = [
        line.strip()
        for line in grub_cfg.splitlines()
        if line.strip().startswith("set default=")
    ]
    return cmdlines, defaults


def apply_command(module, result, cmd, shared):
    """Run a write command, or only record it in check mode"""
    result["actions"].append(" ".join(shared["escapeval"](c) for c in cmd))
    if not module.check_mode:
        module.run_command(cmd, check_rc=True)


def edit_default_grub(module, default_grub, bootloader_setting_options, shared):
    """Apply options to the kernel command line in /etc/default/grub"""
    validate_options(module, bootloader_setting_options)
    try:
        cmdline_default = (
            grub.get_shell_var(default_grub, "GRUB_CMDLINE_LINUX_DEFAULT") or ""
        )
        cmdline_linux = grub.get_shell_var(default_grub, "GRUB_CMDLINE_LINUX") or ""
        new_cmdline_default, new_cmdline_linux = edit_cmdline(
            cmdline_default, cmdline_linux, bootloader_setting_options, shared
        )
    except ValueError as e:
        module.fail_json(msg=str(e))
    for name, value, new_value in [
        ("GRUB_CMDLINE_LINUX_DEFAULT", cmdline_default, new_cmdline_default),
        ("GRUB_CMDLINE_LINUX", cmdline_linux, new_cmdline_linux),
    ]:
        if new_value == value:
            continue
        # arguments are split at whitespace, which breaks a quoted value apart
        if re.search("[\"']", value):
            module.fail_json(
                msg="%s in %s holds a quoted kernel argument, which the role "
                "cannot edit" % (name, grub.DEFAULT_GRUB)
            )
        default_grub = grub.set_shell_var(default_grub, name, new_value)
    return default_grub


def manages_password(module):
    """Whether the boot loader password is to be set or removed"""
    return (
        module.params["password"] is not None
        or module.params["password_hash"] is not None
        or module.params["remove_password"]
    )


def check_password_scripts(module, default_grub):
    """Fail when another grub.d script or GRUB_USERS sets a password GRUB would apply"""
    try:
        grub_users = grub.get_shell_var(default_grub, "GRUB_USERS")
    except ValueError as e:
        module.fail_json(msg="Cannot parse %s: %s" % (grub.DEFAULT_GRUB, e))
    if grub_users:
        module.fail_json(
            msg="GRUB_USERS in %s also sets a boot loader password. Remove it to "
            "manage the password with this role" % grub.DEFAULT_GRUB
        )
    grub_d = os.path.dirname(grub.PASSWORD_SCRIPT)
    for name in sorted(os.listdir(grub_d)):
        path = os.path.join(grub_d, name)
        if path == grub.PASSWORD_SCRIPT or not (
            os.path.isfile(path) and os.access(path, os.X_OK)
        ):
            continue
        with open(path, "rb") as f:
            lines = f.read().decode("utf-8", "replace").splitlines()
        if any(
            PASSWORD_SOURCE.search(line)
            for line in lines
            if not line.lstrip().startswith("#")
        ):
            module.fail_json(
                msg="%s also sets a boot loader password. Remove it to manage "
                "the password with this role" % path
            )


def edit_password_script(module, result, default_grub):
    """Write or remove the grub.d script that holds the boot loader password"""
    if not manages_password(module):
        return False
    check_password_scripts(module, default_grub)
    current_script = grub.read_file(grub.PASSWORD_SCRIPT)
    current_hash = re.search(r"password_pbkdf2 root (\S+)", current_script)
    password_hash = get_password_hash(
        module, current_hash.group(1) if current_hash else None
    )
    new_script = get_password_script(password_hash) if password_hash else ""
    if new_script == current_script:
        # grub2-mkconfig skips a script that is not executable
        if not password_hash or os.stat(grub.PASSWORD_SCRIPT).st_mode & 0o7777 == 0o700:
            return False
        result["actions"].append("chmod 0700 " + grub.PASSWORD_SCRIPT)
        if not module.check_mode:
            os.chmod(grub.PASSWORD_SCRIPT, 0o700)
        return True
    if password_hash:
        result["actions"].append("update " + grub.PASSWORD_SCRIPT)
        if not module.check_mode:
            grub.write_file(module, grub.PASSWORD_SCRIPT, new_script, 0o700)
    else:
        result["actions"].append("remove " + grub.PASSWORD_SCRIPT)
        if not module.check_mode:
            os.unlink(grub.PASSWORD_SCRIPT)
    return True


def run(module, result, shared):
    """Apply settings where pbl manages a grub2-mkconfig configuration.

    shared holds the helpers of the bootloader_settings module that both backends use.
    """
    grub.check_loader(module)
    timeout = module.params["timeout"]
    managed = (
        module.params["bootloader_settings"]
        or timeout is not None
        or manages_password(module)
    )
    # grub2-mkconfig would fall back to built-in defaults without it
    if managed and not os.path.exists(grub.DEFAULT_GRUB):
        module.fail_json(msg="%s does not exist" % grub.DEFAULT_GRUB)
    transactional = module.params["transactional"]
    root = grub.get_next_boot_root(module, transactional)
    default_grub = grub.read_file(grub.DEFAULT_GRUB)
    new_default_grub = default_grub
    grubenv_path = grub.next_boot_path(root, grub.GRUBENV)
    grubenv = grub.get_grubenv(grub.read_file(grubenv_path))
    kernels = grub.get_kernels(module, transactional)
    commands = []

    for bootloader_setting in module.params["bootloader_settings"]:
        selector = bootloader_setting["kernel"]
        facts = [dict(k) for k in kernels]
        if isinstance(selector, dict) and len(selector) > 1:
            # a kernel has several menu entries, compare only those the selector names
            facts = [f for f in facts if entry_matches(f, selector)] or facts
        kernel_action, _unused = shared["validate_kernels"](
            module, bootloader_setting, facts
        )
        if kernel_action in ["create", "remove"]:
            module.fail_json(
                msg="Adding or removing boot entries is not supported on this platform, "
                "boot entries come from the installed kernel packages"
            )
        options = bootloader_setting.get("options", [])
        if isinstance(bootloader_setting["kernel"], str):
            new_default_grub = edit_default_grub(
                module, new_default_grub, options, shared
            )
            continue
        if options:
            module.fail_json(
                msg="Per-entry kernel arguments are not supported on this platform, "
                "where all boot entries share one kernel command line. Use kernel: ALL"
            )
        if bootloader_setting.get("default", False):
            entry = find_entry(module, kernels, bootloader_setting["kernel"])
            new_default_grub = set_default_entry(
                entry,
                new_default_grub,
                grubenv,
                os.path.exists(grubenv_path),
                commands,
            )
    # only a new command line or default entry needs a reboot
    reboot_required = new_default_grub != default_grub or len(commands) > 0

    if timeout is not None:
        try:
            current_timeout = grub.get_shell_var(new_default_grub, "GRUB_TIMEOUT")
        except ValueError as e:
            module.fail_json(msg=str(e))
        if current_timeout != str(timeout):
            new_default_grub = grub.set_shell_var(
                new_default_grub, "GRUB_TIMEOUT", str(timeout)
            )

    changed = edit_password_script(module, result, default_grub)
    # /etc first: transactional-update copies it into the snapshot it works on
    if new_default_grub != default_grub:
        changed = True
        result["actions"].append("update " + grub.DEFAULT_GRUB)
        if not module.check_mode:
            grub.write_file(module, grub.DEFAULT_GRUB, new_default_grub)
    prefix = grub.TRANSACTIONAL_UPDATE + ["run"] if transactional else []
    for cmd in commands:
        apply_command(module, result, prefix + cmd, shared)
    # grub2-set-default exits 0 even when it cannot write grubenv
    if commands and not transactional and not module.check_mode:
        saved_entry = grub.get_grubenv(grub.read_file(grubenv_path)).get("saved_entry")
        if saved_entry != grubenv.get("saved_entry"):
            module.fail_json(msg="Cannot save the default entry in %s" % grub.GRUBENV)
    if changed or (managed and is_stale(root)):
        config_command = (
            grub.TRANSACTIONAL_UPDATE + ["grub.cfg"]
            if transactional
            else ["pbl", "--config"]
        )
        # a source dated ahead of the clock would stay newer than the new menu
        if not module.check_mode:
            now = time.time()
            for path in [grub.DEFAULT_GRUB, grub.PASSWORD_SCRIPT]:
                if os.path.exists(path) and os.path.getmtime(path) > now:
                    os.utime(path, None)
        menu = get_boot_menu(root)
        apply_command(module, result, config_command, shared)
        # the sources may hold a command line or default this run did not write
        if get_boot_menu(root) != menu:
            reboot_required = True
    # on a transactional system, every change is made in a new snapshot
    result["reboot_required"] = reboot_required or (
        transactional and len(result["actions"]) > 0
    )
