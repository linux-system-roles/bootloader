# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: MIT
# Assisted by goose using model glm-5-3
#
"""Code shared by the bootloader_facts and bootloader_settings modules"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

# Some versions of grubby, on platforms where /boot is a separate mount point
# and the BootLoaderSpec entries store the kernel and initrd paths with the
# /boot prefix, report the paths with an extra /boot prefix; for example
# /boot/boot/vmlinuz-7.2.10-200.fc44.x86_64. Strip the extra prefix from the
# grubby output, and add it back to the kernel and initrd paths of the grubby
# commands, so that the modules work on the platforms affected by the issue.
GRUBBY_BOOT_PREFIX = "/boot"
GRUBBY_EXTRA_BOOT_PREFIX = "/boot/boot/"


def strip_extra_boot_prefix(value):
    """Strip the extra /boot prefix that some versions of grubby add to paths

    The value can be a space separated list of paths, as the initrd value
    reported by grubby can be, so the extra prefix is stripped from every
    path of the list; for example /boot/boot/vmlinuz-7.2.10-200.fc44.x86_64
    becomes /boot/vmlinuz-7.2.10-200.fc44.x86_64.
    """
    tokens = value.split()
    if not any(token.startswith(GRUBBY_EXTRA_BOOT_PREFIX) for token in tokens):
        # keep values without the extra prefix, and their whitespace, as is
        return value
    # strip the leading /boot of every path that has the extra prefix
    boot_prefix_len = len(GRUBBY_BOOT_PREFIX)
    return " ".join(
        (
            token[boot_prefix_len:]
            if token.startswith(GRUBBY_EXTRA_BOOT_PREFIX)
            else token
        )
        for token in tokens
    )


def has_extra_boot_prefix(kernels_info):
    """Check whether grubby reports kernel paths with an extra /boot prefix

    Detect the platforms affected by the grubby issue by looking at the
    kernel paths of the output of 'grubby --info=ALL', so that the extra
    prefix can be added back to the kernel and initrd paths of the grubby
    commands.
    """
    return (
        re.search(
            r'^kernel="?' + re.escape(GRUBBY_EXTRA_BOOT_PREFIX),
            kernels_info,
            re.MULTILINE,
        )
        is not None
    )


def add_extra_boot_prefix(value, extra_boot_prefix):
    """Add the extra /boot prefix to the kernel and initrd paths of grubby
    commands

    On the platforms where grubby reports the paths with an extra /boot
    prefix, grubby also expects the extra prefix in the paths passed to its
    --add-kernel, --initrd, --info, --remove-kernel, --set-default and
    --update-kernel arguments. The value can be a space separated list of
    paths, as the initrd value can be, so the extra prefix is added to every
    /boot path of the list.
    """
    if not extra_boot_prefix:
        return value
    tokens = str(value).split()
    return " ".join(
        (
            GRUBBY_BOOT_PREFIX + token
            if token.startswith(GRUBBY_BOOT_PREFIX + "/")
            and not token.startswith(GRUBBY_EXTRA_BOOT_PREFIX)
            else token
        )
        for token in tokens
    )


def get_facts(kernels_info, default_kernel_index):
    """Get kernel facts"""
    kernels_info_lines = kernels_info.strip().split("\n")
    kernels = []
    index_count = 0

    for line in kernels_info_lines:
        index = re.search(r"index=(\d+)", line)
        if index:
            is_default = index.group(1) == default_kernel_index.strip()
            index_count += 1
            kernels.append({})
        search = re.search(r"(.*?)=(.*)", line)
        if search:
            key = search.group(1).strip('"')
            value = search.group(2).strip('"')
            if key in ["kernel", "initrd"]:
                value = strip_extra_boot_prefix(value)
            kernels[index_count - 1].update({key: value})
        else:
            kernels[index_count - 1].update({"kernel": line})
        kernels[index_count - 1].update({"default": is_default})
    return kernels
