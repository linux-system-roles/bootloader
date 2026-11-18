# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: MIT
# Assisted by goose using model glm-5-3
#
"""Unit tests for the code shared by the bootloader modules"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import unittest

from ansible.module_utils.bootloader_lsr import bootloader_common

# non linux entry: RHEL 7 might print such a message
INFO = """
index=0
kernel="/boot/vmlinuz-6.5.12-100.fc37.x86_64"
args="$tuned_params ro rootflags=subvol=root rd.luks.uuid=luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet"
root="UUID=65c70529-e9ad-4778-9001-18fe8c525285"
initrd="/boot/initramfs-6.5.12-100.fc37.x86_64.img $tuned_initrd"
title="Fedora Linux (6.5.12-100.fc37.x86_64) 37 (Workstation Edition)"
id="c44543d15b2c4e898912c2497f734e67-6.5.12-100.fc37.x86_64"
index=1
kernel="/boot/vmlinuz-6.5.10-100.fc37.x86_64"
args="ro rootflags=subvol=root rd.luks.uuid=luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet $tuned_params"
root="UUID=65c70529-e9ad-4778-9001-18fe8c525285"
initrd="/boot/initramfs-6.5.10-100.fc37.x86_64.img $tuned_initrd"
title="Fedora Linux (6.5.10-100.fc37.x86_64) 37 (Workstation Edition)"
id="c44543d15b2c4e898912c2497f734e67-6.5.10-100.fc37.x86_64"
index=2
kernel="/boot/vmlinuz-6.5.7-100.fc37.x86_64"
args="ro rootflags=subvol=root rd.luks.uuid=luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet $tuned_params"
root="UUID=65c70529-e9ad-4778-9001-18fe8c525285"
initrd="/boot/initramfs-6.5.7-100.fc37.x86_64.img $tuned_initrd"
title="Fedora Linux (6.5.7-100.fc37.x86_64) 37 (Workstation Edition)"
id="c44543d15b2c4e898912c2497f734e67-6.5.7-100.fc37.x86_64"
index=3
kernel="/boot/vmlinuz-0-rescue-c44543d15b2c4e898912c2497f734e67"
args="ro rootflags=subvol=root rd.luks.uuid=luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet"
root="UUID=65c70529-e9ad-4778-9001-18fe8c525285"
initrd="/boot/initramfs-0-rescue-c44543d15b2c4e898912c2497f734e67.img"
title="Fedora Linux (0-rescue-c44543d15b2c4e898912c2497f734e67) 36 (Workstation Edition)"
id="c44543d15b2c4e898912c2497f734e67-0-rescue"
index=4
non linux entry
"""

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

# some versions of grubby report the kernel and initrd paths with an extra
# /boot prefix
INFO_EXTRA_BOOT_PREFIX = """
index=0
kernel="/boot/boot/vmlinuz-7.2.10-200.fc44.x86_64"
args="ro rootflags=subvol=root rhgb quiet"
root="UUID=65c70529-e9ad-4778-9001-18fe8c525285"
initrd="/boot/boot/initramfs-7.2.10-200.fc44.x86_64.img $tuned_initrd"
title="Fedora Linux (7.2.10-200.fc44.x86_64) 44 (Cloud Edition)"
id="c44543d15b2c4e898912c2497f734e67-7.2.10-200.fc44.x86_64"
index=1
kernel="/boot/boot/vmlinuz-7.2.8-200.fc44.x86_64"
args="ro rootflags=subvol=root rhgb quiet"
root="UUID=65c70529-e9ad-4778-9001-18fe8c525285"
initrd="/boot/boot/initramfs-7.2.8-200.fc44.x86_64.img $tuned_initrd"
title="Fedora Linux (7.2.8-200.fc44.x86_64) 44 (Cloud Edition)"
id="c44543d15b2c4e898912c2497f734e67-7.2.8-200.fc44.x86_64"
"""

INFO_EXTRA_BOOT_PREFIX_RHEL7 = """
index=0
kernel=/boot/boot/vmlinuz-6.5.12-100.fc37.x86_64
args="ro rootflags=subvol=root rhgb quiet"
root=UUID=65c70529-e9ad-4778-9001-18fe8c525285
initrd=/boot/boot/initramfs-6.5.12-100.fc37.x86_64.img $tuned_initrd
title=Fedora Linux (6.5.12-100.fc37.x86_64) 37 (Workstation Edition)
id=c44543d15b2c4e898912c2497f734e67-6.5.12-100.fc37.x86_64
"""

FACTS_EXTRA_BOOT_PREFIX = [
    {
        "args": "ro rootflags=subvol=root rhgb quiet",
        "id": "c44543d15b2c4e898912c2497f734e67-7.2.10-200.fc44.x86_64",
        "index": "0",
        "initrd": "/boot/initramfs-7.2.10-200.fc44.x86_64.img $tuned_initrd",
        "kernel": "/boot/vmlinuz-7.2.10-200.fc44.x86_64",
        "root": "UUID=65c70529-e9ad-4778-9001-18fe8c525285",
        "title": "Fedora Linux (7.2.10-200.fc44.x86_64) 44 (Cloud Edition)",
        "default": True,
    },
    {
        "args": "ro rootflags=subvol=root rhgb quiet",
        "id": "c44543d15b2c4e898912c2497f734e67-7.2.8-200.fc44.x86_64",
        "index": "1",
        "initrd": "/boot/initramfs-7.2.8-200.fc44.x86_64.img $tuned_initrd",
        "kernel": "/boot/vmlinuz-7.2.8-200.fc44.x86_64",
        "root": "UUID=65c70529-e9ad-4778-9001-18fe8c525285",
        "title": "Fedora Linux (7.2.8-200.fc44.x86_64) 44 (Cloud Edition)",
        "default": False,
    },
]


class GetFacts(unittest.TestCase):
    """test get_facts"""

    def test_get_facts(self):
        kernels = bootloader_common.get_facts(INFO, "2")
        self.assertEqual(
            FACTS,
            kernels,
        )

    def test_get_facts_strips_extra_boot_prefix(self):
        # the facts report the real paths, without the extra prefix
        kernels = bootloader_common.get_facts(INFO_EXTRA_BOOT_PREFIX, "0")
        self.assertEqual(
            FACTS_EXTRA_BOOT_PREFIX,
            kernels,
        )


class ExtraBootPrefix(unittest.TestCase):
    """test handling of the extra /boot prefix that some versions of grubby add"""

    def test_strip_extra_boot_prefix(self):
        # the extra prefix is stripped from kernel paths
        self.assertEqual(
            bootloader_common.strip_extra_boot_prefix(
                "/boot/boot/vmlinuz-7.2.10-200.fc44.x86_64"
            ),
            "/boot/vmlinuz-7.2.10-200.fc44.x86_64",
        )
        # the extra prefix is stripped from every path of the initrd value,
        # other values are kept as is
        self.assertEqual(
            bootloader_common.strip_extra_boot_prefix(
                "/boot/boot/initramfs-7.2.10-200.fc44.x86_64.img $tuned_initrd"
            ),
            "/boot/initramfs-7.2.10-200.fc44.x86_64.img $tuned_initrd",
        )
        # paths without the extra prefix, and values without paths, are
        # unchanged
        self.assertEqual(
            bootloader_common.strip_extra_boot_prefix(
                "/boot/vmlinuz-7.2.10-200.fc44.x86_64"
            ),
            "/boot/vmlinuz-7.2.10-200.fc44.x86_64",
        )
        self.assertEqual(
            bootloader_common.strip_extra_boot_prefix("non linux entry"),
            "non linux entry",
        )
        self.assertEqual(bootloader_common.strip_extra_boot_prefix(""), "")

    def test_has_extra_boot_prefix(self):
        self.assertTrue(bootloader_common.has_extra_boot_prefix(INFO_EXTRA_BOOT_PREFIX))
        # unquoted kernel paths, as RHEL 7 grubby reports them, are detected too
        self.assertTrue(
            bootloader_common.has_extra_boot_prefix(INFO_EXTRA_BOOT_PREFIX_RHEL7)
        )
        self.assertFalse(bootloader_common.has_extra_boot_prefix(INFO))
        self.assertFalse(bootloader_common.has_extra_boot_prefix(""))
        # kernel paths without the extra prefix are not detected, whether
        # grubby reports them quoted or not
        self.assertFalse(
            bootloader_common.has_extra_boot_prefix(
                'kernel="/boot/vmlinuz-6.5.12-100.fc37.x86_64"\n'
            )
        )
        self.assertFalse(
            bootloader_common.has_extra_boot_prefix(
                "kernel=/boot/vmlinuz-6.5.12-100.fc37.x86_64\n"
            )
        )

    def test_add_extra_boot_prefix(self):
        # without the grubby issue the paths are used as is
        self.assertEqual(
            bootloader_common.add_extra_boot_prefix(
                "/boot/vmlinuz-7.2.10-200.fc44.x86_64", False
            ),
            "/boot/vmlinuz-7.2.10-200.fc44.x86_64",
        )
        # with the grubby issue the extra prefix is added to kernel paths
        self.assertEqual(
            bootloader_common.add_extra_boot_prefix(
                "/boot/vmlinuz-7.2.10-200.fc44.x86_64", True
            ),
            "/boot/boot/vmlinuz-7.2.10-200.fc44.x86_64",
        )
        # the extra prefix is added to every /boot path of the initrd value,
        # other values are kept as is
        self.assertEqual(
            bootloader_common.add_extra_boot_prefix(
                "/boot/initramfs-7.2.10-200.fc44.x86_64.img $tuned_initrd", True
            ),
            "/boot/boot/initramfs-7.2.10-200.fc44.x86_64.img $tuned_initrd",
        )
        # paths without the /boot prefix, and paths that already have the
        # extra prefix, are unchanged
        self.assertEqual(
            bootloader_common.add_extra_boot_prefix(
                "/vmlinuz-7.2.10-200.fc44.x86_64", True
            ),
            "/vmlinuz-7.2.10-200.fc44.x86_64",
        )
        self.assertEqual(
            bootloader_common.add_extra_boot_prefix(
                "/boot/boot/vmlinuz-7.2.10-200.fc44.x86_64", True
            ),
            "/boot/boot/vmlinuz-7.2.10-200.fc44.x86_64",
        )
