# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Sergei Petrosian <spetrosi@redhat.com>
# SPDX-License-Identifier: GPL-2.0-or-later
#
""" Unit tests for the bootloader_settings module """

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import unittest

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

import bootloader_settings

OPTIONS = [
    {"name": "arg_with_str_value", "value": "test_value"},
    {"name": "arg_with_int_value", "value": 1, "state": "present"},
    {"name": "arg_without_val", "state": "present"},
    {"name": "arg_with_str_value_absent", "value": "test_value", "state": "absent"},
    {"name": "arg_with_int_value_absent", "value": 1, "state": "absent"},
    {"name": "arg_without_val_absent", "state": "absent"},
    {"previous": "replaced"},
    {"copy_default": True},
]

SETTINGS = [
    {"kernel": "DEFAULT", "options": OPTIONS},
    {"kernel": "ALL", "options": OPTIONS},
    {"kernel": "INCORRECT_STRING", "options": OPTIONS},
    {"kernel": {"index": 1}, "options": OPTIONS},
    {"kernel": {"index": [0, 1]}, "options": OPTIONS},
    {"kernel": {"kernel_index": [0, 1]}, "options": OPTIONS},
    {
        "kernel": {
            "title": "Fedora Linux",
            "path": "/boot/vmlinuz-6.5.12-100.fc37.x86_64",
        },
        "options": OPTIONS,
    },
    {
        "kernel": {"title": "Fedora Linux", "path": "/boot/vmlinuz-6"},
        "options": OPTIONS,
    },
    {
        "kernel": {
            "title": "Fedora Linux",
            "path": "/boot/vmlinuz-6",
            "initrd": "/boot/initramfs-6.6.img",
        },
        "options": OPTIONS,
    },
    {"kernel": {"initrd": "/boot/initramfs-6.6.img"}, "options": OPTIONS},
    {
        "kernel": {"initrd": "/boot/initramfs-6.6.img"},
        "options": OPTIONS,
        "state": "test_state",
    },
    {"kernel": [{"initrd": "/boot/initramfs-6.6.img"}], "options": OPTIONS},
    {
        "kernel": {
            "title": "Fedora Linux (6.5.12-100.fc37.x86_64) 37 (Workstation Edition)",
            "path": "/boot/vmlinuz-6.5.12-100.fc37.x86_64",
            "initrd": "/boot/initramfs-6.5.12-100.fc37.x86_64.img $tuned_initrd",
        },
        "options": OPTIONS,
    },
]

FACTS = [
    {
        "args": "$tuned_params ro rootflags=subvol=root rd.luks.uuid=luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet",
        "id": "c44543d15b2c4e898912c2497f734e67-6.5.12-100.fc37.x86_64",
        "index": "0",
        "initrd": "/boot/initramfs-6.5.12-100.fc37.x86_64.img $tuned_initrd",
        "kernel": "/boot/vmlinuz-6.5.12-100.fc37.x86_64",
        "root": "UUID=65c70529-e9ad-4778-9001-18fe8c525285",
        "title": "Fedora Linux (6.5.12-100.fc37.x86_64) 37 (Workstation Edition)",
        "default": False,
    },
    {
        "args": "ro rootflags=subvol=root rd.luks.uuid=luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet $tuned_params",
        "id": "c44543d15b2c4e898912c2497f734e67-6.5.10-100.fc37.x86_64",
        "index": "1",
        "initrd": "/boot/initramfs-6.5.10-100.fc37.x86_64.img $tuned_initrd",
        "kernel": "/boot/vmlinuz-6.5.10-100.fc37.x86_64",
        "root": "UUID=65c70529-e9ad-4778-9001-18fe8c525285",
        "title": "Fedora Linux (6.5.10-100.fc37.x86_64) 37 (Workstation Edition)",
        "default": False,
    },
    {
        "args": "ro rootflags=subvol=root rd.luks.uuid=luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet $tuned_params",
        "id": "c44543d15b2c4e898912c2497f734e67-6.5.7-100.fc37.x86_64",
        "index": "2",
        "initrd": "/boot/initramfs-6.5.7-100.fc37.x86_64.img $tuned_initrd",
        "kernel": "/boot/vmlinuz-6.5.7-100.fc37.x86_64",
        "root": "UUID=65c70529-e9ad-4778-9001-18fe8c525285",
        "title": "Fedora Linux (6.5.7-100.fc37.x86_64) 37 (Workstation Edition)",
        "default": True,
    },
    {
        "args": "ro rootflags=subvol=root rd.luks.uuid=luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet",
        "id": "c44543d15b2c4e898912c2497f734e67-0-rescue",
        "index": "3",
        "initrd": "/boot/initramfs-0-rescue-c44543d15b2c4e898912c2497f734e67.img",
        "kernel": "/boot/vmlinuz-0-rescue-c44543d15b2c4e898912c2497f734e67",
        "root": "UUID=65c70529-e9ad-4778-9001-18fe8c525285",
        "title": "Fedora Linux (0-rescue-c44543d15b2c4e898912c2497f734e67) 36 (Workstation Edition)",
        "default": False,
    },
    {"index": "4", "kernel": "non linux entry", "default": False},
]

KERNELS = [
    {"kernel": {"kernel_index": [0, 1]}},
    {"kernel": {"kernel_index": 2}},
    {"kernel": {"kernel_path": ["/path/1", "/path/2"]}},
    {"kernel": {"kernel_path": "/path/3"}},
    {
        "kernel": {
            "kernel_title": [
                "Fedora Linux (1.1.11-100.fc37.x86_64) 37 (Workstation Edition)",
                "Fedora Linux (1.1.11-200.fc37.x86_64) 37 (Workstation Edition)",
            ]
        },
    },
    {
        "kernel": {
            "kernel_title": "Fedora Linux (1.1.11-300.fc37.x86_64) 37 (Workstation Edition)"
        },
    },
    {"kernel": "DEFAULT"},
    {"kernel": "ALL"},
]

changed_args = "arg_with_str_value_absent=test_value arg_with_int_value_absent=1 arg_without_val_absent"
INFO = (
    """
index=0
kernel="/boot/vmlinuz-6.5.12-100.fc37.x86_64"
args="%s"
root="UUID=65c70529-e9ad-4778-9001-18fe8c525285"
initrd="/boot/initramfs-6.5.12-100.fc37.x86_64.img $tuned_initrd"
title="Fedora Linux (6.5.12-100.fc37.x86_64) 37 (Workstation Edition)"
id="c44543d15b2c4e898912c2497f734e67-6.5.12-100.fc37.x86_64"
"""
    % changed_args
)

same_args = "arg_with_str_value=test_value arg_with_int_value=1 arg_without_val"
INFO_SAME_ARGS = (
    """
index=0
kernel="/boot/vmlinuz-6.5.12-100.fc37.x86_64"
args="%s"
root="UUID=65c70529-e9ad-4778-9001-18fe8c525285"
initrd="/boot/initramfs-6.5.12-100.fc37.x86_64.img $tuned_initrd"
title="Fedora Linux (6.5.12-100.fc37.x86_64) 37 (Workstation Edition)"
id="c44543d15b2c4e898912c2497f734e67-6.5.12-100.fc37.x86_64"
"""
    % same_args
)

INFO_RHEL7 = (
    """
index=0
kernel=/boot/vmlinuz-6.5.12-100.fc37.x86_64
args="%s"
root=UUID=65c70529-e9ad-4778-9001-18fe8c525285
initrd=/boot/initramfs-6.5.12-100.fc37.x86_64.img $tuned_initrd
title=Fedora Linux (6.5.12-100.fc37.x86_64) 37 (Workstation Edition)
id=c44543d15b2c4e898912c2497f734e67-6.5.12-100.fc37.x86_64
"""
    % changed_args
)

kernels_keys = ["kernel_index", "kernel_path", "kernel_title", "DEFAULT", "ALL"]


class InputValidator(unittest.TestCase):
    """test functions that process bootloader_settings argument"""

    mock_module = MagicMock(
        run_command=MagicMock(return_value=("test_rc", "test_stdout", "test_err")),
        fail_json=MagicMock(side_effect=SystemExit),
    )
    result = dict(changed=False, actions=list())
    kernel = None
    kernel_action = None

    def reset_vars(self):
        self.mock_module.run_command.reset_mock()
        self.mock_module.fail_json.reset_mock()
        self.result = dict(changed=False, actions=list())
        try:
            del self.kernel
        except AttributeError:
            pass
        try:
            del self.kernel_action
        except AttributeError:
            pass

    def assert_error_msg(self, err, *cmd_args):
        try:
            self.kernel_action, self.kernel = bootloader_settings.validate_kernels(
                self.mock_module, *cmd_args
            )
        except SystemExit:
            self.mock_module.fail_json.assert_called_once_with(err)

    def test_validate_kernels(self):
        self.reset_vars()
        self.kernel_action, self.kernel = bootloader_settings.validate_kernels(
            self.mock_module, SETTINGS[0], FACTS
        )
        self.mock_module.fail_json.assert_not_called()
        self.assertEqual(self.kernel_action, "modify")
        self.assertEqual(self.kernel, "DEFAULT")
        self.reset_vars()

        self.kernel_action, self.kernel = bootloader_settings.validate_kernels(
            self.mock_module, SETTINGS[1], FACTS
        )
        self.mock_module.fail_json.assert_not_called()
        self.assertEqual(self.kernel_action, "modify")
        self.assertEqual(self.kernel, "ALL")
        self.reset_vars()

        err = "kernel INCORRECT_STRING is of type str, it must be one of 'DEFAULT, ALL'"
        cmd_args = SETTINGS[2], FACTS
        self.assert_error_msg(err, *cmd_args)
        self.assertIsNone(self.kernel_action)
        self.assertIsNone(self.kernel)
        self.reset_vars()

        self.kernel_action, self.kernel = bootloader_settings.validate_kernels(
            self.mock_module, SETTINGS[3], FACTS
        )
        self.mock_module.fail_json.assert_not_called()
        self.assertEqual(self.kernel_action, "modify")
        self.assertEqual(self.kernel, "1")
        self.reset_vars()

        err = "kernel value in 'index: [0, 1]' must be of type str or int"
        cmd_args = SETTINGS[4], FACTS
        self.assert_error_msg(err, *cmd_args)
        self.assertIsNone(self.kernel_action)
        self.assertIsNone(self.kernel)
        self.reset_vars()

        # initrd can be provided ONLY when creating a self.kernel
        err = "kernel key in 'kernel_index: [0, 1]' must be one of 'path, index, title, initrd'"
        cmd_args = SETTINGS[5], FACTS
        self.assert_error_msg(err, *cmd_args)
        self.assertIsNone(self.kernel_action)
        self.assertIsNone(self.kernel)
        self.reset_vars()

        err = (
            "A kernel with provided ['path'] already exists and its other fields are different "
            + "{'title': ('Fedora Linux', 'Fedora Linux (6.5.12-100.fc37.x86_64) 37 (Workstation Edition)')}"
        )
        cmd_args = SETTINGS[6], FACTS
        self.assert_error_msg(err, *cmd_args)
        self.assertIsNone(self.kernel_action)
        self.assertIsNone(self.kernel)
        self.reset_vars()

        err = (
            "To create a kernel, you must provide 3 kernel keys - 'path, title, initrd'"
        )
        cmd_args = SETTINGS[7], FACTS
        self.assert_error_msg(err, *cmd_args)
        self.assertIsNone(self.kernel_action)
        self.assertIsNone(self.kernel)
        self.reset_vars()

        self.kernel_action, self.kernel = bootloader_settings.validate_kernels(
            self.mock_module, SETTINGS[8], FACTS
        )
        self.mock_module.fail_json.assert_not_called()
        self.assertEqual(self.kernel_action, "create")
        self.assertEqual(
            self.kernel,
            "--initrd=/boot/initramfs-6.6.img --add-kernel=/boot/vmlinuz-6 --title='Fedora Linux'",
        )
        self.reset_vars()

        err = "You can use 'initrd' as a kernel key only when you must create a kernel. To modify or remove an existing kernel, use one of path, title, index"
        cmd_args = SETTINGS[9], FACTS
        self.assert_error_msg(err, *cmd_args)
        self.assertIsNone(self.kernel_action)
        self.assertIsNone(self.kernel)
        self.reset_vars()

        err = "State must be one of 'present, absent'"
        cmd_args = SETTINGS[10], FACTS
        self.assert_error_msg(err, *cmd_args)
        self.assertIsNone(self.kernel_action)
        self.assertIsNone(self.kernel)
        self.reset_vars()

        err = "kernel value in [{'initrd': '/boot/initramfs-6.6.img'}] must be of type str or dict"
        cmd_args = SETTINGS[11], FACTS
        self.assert_error_msg(err, *cmd_args)
        self.assertIsNone(self.kernel_action)
        self.assertIsNone(self.kernel)
        self.reset_vars()

        self.kernel_action, self.kernel = bootloader_settings.validate_kernels(
            self.mock_module, SETTINGS[12], FACTS
        )
        self.mock_module.fail_json.assert_not_called()
        self.assertEqual(self.kernel_action, "modify")
        self.reset_vars()

    def test_add_kernel(self):
        self.reset_vars()
        self.kernel = bootloader_settings.get_create_kernel(SETTINGS[8]["kernel"])
        bootloader_settings.add_kernel(
            self.mock_module, self.result, SETTINGS[8]["options"], self.kernel
        )
        expected_cmd = (
            "grubby --initrd=/boot/initramfs-6.6.img --add-kernel=/boot/vmlinuz-6 --title='Fedora Linux' "
            + "--args='arg_with_str_value=test_value arg_with_int_value=1 arg_without_val arg_with_str_value_absent=test_value "
            + "arg_with_int_value_absent=1 arg_without_val_absent' --copy-default"
        )
        self.mock_module.run_command.assert_called_once_with(expected_cmd)
        self.assertEqual(self.result["changed"], True)
        self.assertEqual(self.result["actions"][0], expected_cmd)
        self.reset_vars()

    def test_rm_kernel(self):
        self.reset_vars()
        self.kernel = bootloader_settings.get_single_kernel(SETTINGS[3]["kernel"])
        self.assertEqual(
            self.kernel,
            "1",
        )

        bootloader_settings.rm_kernel(self.mock_module, self.result, self.kernel)
        expected_cmd = "grubby --remove-kernel=1"
        self.mock_module.run_command.assert_called_once_with(expected_cmd)
        self.assertEqual(self.result["changed"], True)
        self.assertEqual(self.result["actions"][0], expected_cmd)
        self.reset_vars()

    def test_get_boot_args(self):
        bootloader_args = bootloader_settings.get_boot_args(INFO)
        self.assertEqual(
            bootloader_args,
            "arg_with_str_value_absent=test_value arg_with_int_value_absent=1 arg_without_val_absent",
        )
        bootloader_args = bootloader_settings.get_boot_args(INFO_RHEL7)
        self.assertEqual(
            bootloader_args,
            "arg_with_str_value_absent=test_value arg_with_int_value_absent=1 arg_without_val_absent",
        )
        bootloader_args = bootloader_settings.get_boot_args("")
        self.assertEqual(bootloader_args, "")

    def test_rm_boot_args(self):
        self.reset_vars()
        bootloader_settings.rm_boot_args(self.mock_module, self.result, INFO, "0")
        expected_cmd = (
            "grubby --update-kernel=0 --remove-args="
            + "'arg_with_str_value_absent=test_value arg_with_int_value_absent=1 arg_without_val_absent'"
        )
        self.mock_module.run_command.assert_called_once_with(expected_cmd)
        self.assertEqual(self.result["changed"], True)
        self.assertEqual(self.result["actions"][0], expected_cmd)
        self.reset_vars()

    def test_mod_boot_args(self):
        self.reset_vars()
        args = (
            "--remove-args='arg_with_str_value_absent=test_value arg_with_int_value_absent=1 arg_without_val_absent' "
            + "--args='arg_with_str_value=test_value arg_with_int_value=1 arg_without_val'"
        )

        bootloader_settings.mod_boot_args(
            self.mock_module,
            self.result,
            OPTIONS,
            str(KERNELS[1]["kernel"]["kernel_index"]),
            INFO,
        )
        expected_cmd = "grubby --update-kernel=2 " + args
        self.mock_module.run_command.assert_called_once_with(expected_cmd)
        self.assertEqual(self.result["changed"], True)
        self.assertEqual(self.result["actions"][0], expected_cmd)
        self.reset_vars()

        bootloader_settings.mod_boot_args(
            self.mock_module,
            self.result,
            OPTIONS,
            KERNELS[3]["kernel"]["kernel_path"],
            INFO,
        )
        expected_cmd = "grubby --update-kernel=/path/3 " + args
        self.mock_module.run_command.assert_called_once_with(expected_cmd)
        self.assertEqual(self.result["changed"], True)
        self.assertEqual(self.result["actions"][0], expected_cmd)
        self.reset_vars()

        bootloader_settings.mod_boot_args(
            self.mock_module,
            self.result,
            OPTIONS,
            bootloader_settings.escapeval(
                "TITLE=" + KERNELS[5]["kernel"]["kernel_title"]
            ),
            INFO,
        )
        expected_cmd = (
            "grubby --update-kernel='TITLE=Fedora Linux (1.1.11-300.fc37.x86_64) 37 (Workstation Edition)' "
            + args
        )
        self.mock_module.run_command.assert_called_once_with(expected_cmd)
        self.assertEqual(self.result["changed"], True)
        self.assertEqual(self.result["actions"][0], expected_cmd)
        self.reset_vars()

        bootloader_settings.mod_boot_args(
            self.mock_module,
            self.result,
            OPTIONS,
            KERNELS[6]["kernel"],
            INFO,
        )
        expected_cmd = "grubby --update-kernel=DEFAULT " + args
        self.mock_module.run_command.assert_called_once_with(expected_cmd)
        self.assertEqual(self.result["changed"], True)
        self.assertEqual(self.result["actions"][0], expected_cmd)
        self.reset_vars()

        bootloader_settings.mod_boot_args(
            self.mock_module,
            self.result,
            OPTIONS,
            KERNELS[7]["kernel"],
            INFO,
        )
        expected_cmd = "grubby --update-kernel=ALL " + args
        self.mock_module.run_command.assert_called_once_with(expected_cmd)
        self.assertEqual(self.result["changed"], True)
        self.assertEqual(self.result["actions"][0], expected_cmd)
        self.reset_vars()

        bootloader_settings.mod_boot_args(
            self.mock_module,
            self.result,
            OPTIONS,
            str(KERNELS[1]["kernel"]["kernel_index"]),
            INFO_SAME_ARGS,
        )
        self.mock_module.run_command.assert_not_called()
        self.assertEqual(self.result["changed"], False)
        self.assertEqual(self.result["actions"], [])
        self.reset_vars()
