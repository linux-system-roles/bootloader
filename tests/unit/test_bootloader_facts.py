# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Sergei Petrosian <spetrosi@redhat.com>
# SPDX-License-Identifier: GPL-2.0-or-later
#
"""Unit tests for the bootloader_settings module"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import unittest

import bootloader_facts
import bootloader_settings

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


class InputValidator(unittest.TestCase):
    """test functions that process bootloader_settings argument"""

    def test_get_facts(self):
        kernels = bootloader_facts.get_facts(INFO, "2")
        self.assertEqual(
            FACTS,
            kernels,
        )
        kernels = bootloader_settings.get_facts(INFO, "2")
        self.assertEqual(
            FACTS,
            kernels,
        )
