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

    def test_get_kernels(self):
        kernels = bootloader_settings.get_kernels(KERNELS[0]["kernel"], kernels_keys)
        self.assertEqual(["0", "1"], kernels)
        kernels = bootloader_settings.get_kernels(KERNELS[1]["kernel"], kernels_keys)
        self.assertEqual(["2"], kernels)
        kernels = bootloader_settings.get_kernels(KERNELS[2]["kernel"], kernels_keys)
        self.assertEqual(["/path/1", "/path/2"], kernels)
        kernels = bootloader_settings.get_kernels(KERNELS[3]["kernel"], kernels_keys)
        self.assertEqual(["/path/3"], kernels)
        kernels = bootloader_settings.get_kernels(KERNELS[4]["kernel"], kernels_keys)
        self.assertEqual(
            [
                "TITLE=Fedora Linux (1.1.11-100.fc37.x86_64) 37 (Workstation Edition)",
                "TITLE=Fedora Linux (1.1.11-200.fc37.x86_64) 37 (Workstation Edition)",
            ],
            kernels,
        )
        kernels = bootloader_settings.get_kernels(KERNELS[5]["kernel"], kernels_keys)
        self.assertEqual(
            ["TITLE=Fedora Linux (1.1.11-300.fc37.x86_64) 37 (Workstation Edition)"],
            kernels,
        )
        kernels = bootloader_settings.get_kernels(KERNELS[6]["kernel"], kernels_keys)
        self.assertEqual(["DEFAULT"], kernels)
        kernels = bootloader_settings.get_kernels(KERNELS[7]["kernel"], kernels_keys)
        self.assertEqual(["ALL"], kernels)

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
