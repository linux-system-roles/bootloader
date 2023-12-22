# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Sergei Petrosian <spetrosi@redhat.com>
# SPDX-License-Identifier: GPL-2.0-or-later
#
""" Unit tests for the bootloader_settings module """

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import unittest

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

INFO = """
index=0
kernel="/boot/vmlinuz-6.5.12-100.fc37.x86_64"
args="arg_with_str_value_absent=test_value arg_with_int_value_absent=1 arg_without_val_absent"
root="UUID=65c70529-e9ad-4778-9001-18fe8c525285"
initrd="/boot/initramfs-6.5.12-100.fc37.x86_64.img $tuned_initrd"
title="Fedora Linux (6.5.12-100.fc37.x86_64) 37 (Workstation Edition)"
id="c44543d15b2c4e898912c2497f734e67-6.5.12-100.fc37.x86_64"
"""

INFO_RHEL7 = """
index=0
kernel=/boot/vmlinuz-6.5.12-100.fc37.x86_64
args="arg_with_str_value_absent=test_value arg_with_int_value_absent=1 arg_without_val_absent"
root=UUID=65c70529-e9ad-4778-9001-18fe8c525285
initrd=/boot/initramfs-6.5.12-100.fc37.x86_64.img $tuned_initrd
title=Fedora Linux (6.5.12-100.fc37.x86_64) 37 (Workstation Edition)
id=c44543d15b2c4e898912c2497f734e67-6.5.12-100.fc37.x86_64
"""

kernels_keys = ["kernel_index", "kernel_path", "kernel_title", "DEFAULT", "ALL"]


class InputValidator(unittest.TestCase):
    """test functions that process bootloader_settings argument"""

    def test_validate_kernels(self):
        err, kernel_action, kernel = bootloader_settings.validate_kernels(
            SETTINGS[0], FACTS
        )
        self.assertEqual(
            err,
            "",
        )
        self.assertEqual(kernel_action, "modify")
        self.assertEqual(kernel, "DEFAULT")
        err, kernel_action, kernel = bootloader_settings.validate_kernels(
            SETTINGS[1], FACTS
        )
        self.assertEqual(err, "")
        self.assertEqual(kernel_action, "modify")
        self.assertEqual(kernel, "ALL")
        err, kernel_action, kernel = bootloader_settings.validate_kernels(
            SETTINGS[2], FACTS
        )
        self.assertEqual(
            err,
            "kernel INCORRECT_STRING is of type str, it must be one of 'DEFAULT, ALL'",
        )
        self.assertEqual(kernel_action, "")
        self.assertEqual(kernel, "")
        err, kernel_action, kernel = bootloader_settings.validate_kernels(
            SETTINGS[3], FACTS
        )
        self.assertEqual(err, "")
        self.assertEqual(kernel_action, "modify")
        self.assertEqual(kernel, "1")
        err, kernel_action, kernel = bootloader_settings.validate_kernels(
            SETTINGS[4], FACTS
        )
        self.assertEqual(
            err, "kernel value in 'index: [0, 1]' must be of type str or int"
        )
        self.assertEqual(kernel_action, "")
        self.assertEqual(kernel, "")
        err, kernel_action, kernel = bootloader_settings.validate_kernels(
            SETTINGS[5], FACTS
        )
        # initrd can be provided ONLY when creating a kernel
        self.assertEqual(
            err,
            "kernel key in 'kernel_index: [0, 1]' must be one of 'path, index, title, initrd'",
        )
        self.assertEqual(kernel_action, "")
        self.assertEqual(kernel, "")
        err, kernel_action, kernel = bootloader_settings.validate_kernels(
            SETTINGS[6], FACTS
        )
        self.assertEqual(
            err,
            "A kernel with provided {'path'} already exists and it's other fields are different "
            + "{'title': ('Fedora Linux', 'Fedora Linux (6.5.12-100.fc37.x86_64) 37 (Workstation Edition)')}",
        )
        self.assertEqual(kernel_action, "")
        self.assertEqual(kernel, "")
        err, kernel_action, kernel = bootloader_settings.validate_kernels(
            SETTINGS[7], FACTS
        )
        self.assertEqual(
            err,
            "To create a kernel, you must provide 3 kernel keys - 'path, title, initrd'",
        )
        self.assertEqual(kernel_action, "")
        self.assertEqual(kernel, "")
        err, kernel_action, kernel = bootloader_settings.validate_kernels(
            SETTINGS[8], FACTS
        )
        self.assertEqual(err, "")
        self.assertEqual(kernel_action, "create")
        self.assertEqual(
            kernel,
            "--title='Fedora Linux' --add-kernel=/boot/vmlinuz-6 --initrd=/boot/initramfs-6.6.img",
        )
        err, kernel_action, kernel = bootloader_settings.validate_kernels(
            SETTINGS[9], FACTS
        )
        self.assertEqual(
            err,
            "You can use 'initrd' as a kernel key only when you must create a kernel. To modify or remove an existing kernel, use one of path, title, index",
        )
        self.assertEqual(kernel_action, "")
        self.assertEqual(kernel, "")
        err, kernel_action, kernel = bootloader_settings.validate_kernels(
            SETTINGS[10], FACTS
        )
        self.assertEqual(err, "State must be one of 'present, absent'")
        self.assertEqual(kernel_action, "")
        self.assertEqual(kernel, "")
        err, kernel_action, kernel = bootloader_settings.validate_kernels(
            SETTINGS[11], FACTS
        )
        self.assertEqual(
            err,
            "kernel value in [{'initrd': '/boot/initramfs-6.6.img'}] must be of type str or dict",
        )
        self.assertEqual(kernel_action, "")
        self.assertEqual(kernel, "")
        err, kernel_action, kernel = bootloader_settings.validate_kernels(
            SETTINGS[12], FACTS
        )
        self.assertEqual(err, "")
        self.assertEqual(kernel_action, "modify")

    def test_get_add_kernel_cmd(self):
        kernel = bootloader_settings.get_create_kernel(SETTINGS[8]["kernel"])
        add_kernel_cmd = bootloader_settings.get_add_kernel_cmd(
            SETTINGS[8]["options"], kernel
        )
        self.assertEqual(
            add_kernel_cmd,
            "grubby --title='Fedora Linux' --add-kernel=/boot/vmlinuz-6 --initrd=/boot/initramfs-6.6.img "
            + "--args='arg_with_str_value=test_value arg_with_int_value=1 arg_without_val arg_with_str_value_absent=test_value "
            + "arg_with_int_value_absent=1 arg_without_val_absent' --copy-default",
        )

    def test_get_rm_kernel_cmd(self):
        kernel = bootloader_settings.get_single_kernel(SETTINGS[3]["kernel"])
        self.assertEqual(
            kernel,
            "1",
        )
        rm_kernel_cmd = bootloader_settings.get_rm_kernel_cmd(kernel)
        self.assertEqual(
            rm_kernel_cmd,
            "grubby --remove-kernel=1",
        )

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

    def test_get_rm_boot_args_cmd(self):
        rm_boot_args_cmd = bootloader_settings.get_rm_boot_args_cmd(INFO, "0")
        self.assertEqual(
            "grubby --update-kernel=0 --remove-args="
            + "'arg_with_str_value_absent=test_value arg_with_int_value_absent=1 arg_without_val_absent'",
            rm_boot_args_cmd,
        )

    def test_get_mod_boot_args_cmd(self):
        args = (
            "--remove-args='arg_with_str_value_absent=test_value arg_with_int_value_absent=1 arg_without_val_absent' "
            + "--args='arg_with_str_value=test_value arg_with_int_value=1 arg_without_val'"
        )
        mod_boot_args_cmd = bootloader_settings.get_mod_boot_args_cmd(
            OPTIONS, str(KERNELS[1]["kernel"]["kernel_index"]), INFO
        )
        self.assertEqual(
            "grubby --update-kernel=2 " + args,
            mod_boot_args_cmd,
        )
        mod_boot_args_cmd = bootloader_settings.get_mod_boot_args_cmd(
            OPTIONS, KERNELS[3]["kernel"]["kernel_path"], INFO
        )
        self.assertEqual(
            "grubby --update-kernel=/path/3 " + args,
            mod_boot_args_cmd,
        )
        mod_boot_args_cmd = bootloader_settings.get_mod_boot_args_cmd(
            OPTIONS,
            bootloader_settings.escapeval(
                "TITLE=" + KERNELS[5]["kernel"]["kernel_title"]
            ),
            INFO,
        )
        self.assertEqual(
            "grubby --update-kernel='TITLE=Fedora Linux (1.1.11-300.fc37.x86_64) 37 (Workstation Edition)' "
            + args,
            mod_boot_args_cmd,
        )
        mod_boot_args_cmd = bootloader_settings.get_mod_boot_args_cmd(
            OPTIONS, KERNELS[6]["kernel"], INFO
        )
        self.assertEqual(
            "grubby --update-kernel=DEFAULT " + args,
            mod_boot_args_cmd,
        )
        mod_boot_args_cmd = bootloader_settings.get_mod_boot_args_cmd(
            OPTIONS, KERNELS[7]["kernel"], INFO
        )
        self.assertEqual(
            "grubby --update-kernel=ALL " + args,
            mod_boot_args_cmd,
        )
