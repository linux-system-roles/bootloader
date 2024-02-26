# bootloader

[![ansible-lint.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/ansible-lint.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/ansible-lint.yml) [![ansible-test.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/ansible-test.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/ansible-test.yml) [![codeql.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/codeql.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/codeql.yml) [![markdownlint.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/markdownlint.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/markdownlint.yml) [![python-unit-test.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/python-unit-test.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/python-unit-test.yml) [![woke.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/woke.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/woke.yml)

An Ansible role for bootloader and kernel command line management.

## Supported architectures

This role currently supports configuring `grub2` boot loader which runs on the following architectures:

* AMD and Intel 64-bit architectures (x86-64)
* The 64-bit ARM architecture (ARMv8.0)
* IBM Power Systems, Little Endian (POWER9)

## Requirements

See below

### Collection requirements

If you don't want to manage `ostree` systems, the role has no requirements.

If you want to manage `ostree` systems, the role requires additional modules
from external collections.  Please use the following command to install them:

```bash
ansible-galaxy collection install -vv -r meta/collection-requirements.yml
```

## Role Variables

### bootloader_gather_facts

Whether to gather [bootloader_facts](#bootloader_facts) that contain boot information for all kernels.

Default: `false`

Type: `bool`

### bootloader_settings

With this variable, list kernels and their command line parameters that you want to set.

Required keys:

1. `kernel` - with this, specify the kernel to update settings for.
Each list should specify the same kernel using one or multiple keys.

    If you want to you add a kernel, you must specify three keys - `path`, `title`, `initrd`.

    If you want to modify or remove a kerne, you can specify one or more key.

    You can also specify `DEFAULT` or `ALL` to update the default or all kernels.

    Available keys:
    * `path` - kernel path
    * `index` - kernel index
    * `title` - kernel title
    * `initrd` - kernel initrd image

    Available strings:
    * `DEFAULT` - to update the default entry
    * `ALL` - to update all of the entries

2. `state` - state of the kernel.

    Available values: `present`, `absent`

    Default: `present`

3. `options` - with this, specify settings to update

    * `name` - The name of the setting. `name` is omitted when using `replaced`.
    * `value` - The value for the setting. You must omit `value` if the setting has no value, e.g. `quiet`.
    * `state` - `present` (default) or `absent`. The value `absent` means to remove a setting with `name` name - name must be provided.
    * `previous` - Optional - the only value is `replaced` - this is used to specify that the previous settings should be replaced with the given settings.
    * `copy_default` - Optional - when you create a kernel, you can specify `copy_default: true` to copy the default arguments to the created kernel

For an example, see [Example Playbook](#example-playbook).

Default: `{}`

Type: `dict`

### bootloader_timeout

With this variable, you can customize the loading time of the GRUB bootloader.

Default: `5`

Type: `int`

### bootloader_password

With this variable, you can protect boot parameters with a password.

__WARNING__: Changing bootloader password is not idempotent.

Boot loader username is always `root`.

This should come from vault.

If unset, current configuration is not touched.

Default: `null`

Type: `string`

### bootloader_remove_password

By setting this variable to `true`, you can remove bootloader password.

Default: `false`

Type: `bool`

### bootloader_reboot_ok

If `true`, if the role detects that something was changed that requires a reboot to take effect, the role will reboot the managed host.

If `false`, it is up to you to determine when to reboot the managed host.

The role will returns the variable `bootloader_reboot_required` (see below) with a value of `true` to indicate that some change has occurred which needs a reboot to take effect.

Default: `false`

Type: `bool`

## Variables Exported by the Role

The role exports the following variables:

### bootloader_reboot_needed

Default `false` - if `true`, this means a reboot is needed to apply the changes made by the role

### bootloader_facts

Contains boot information for all kernels.

The role returns this variable when you set `bootloader_gather_facts: true`.

For example:

```yaml
"bootloader_facts": [
    {
        "args": "ro rootflags=subvol=root rd.luks.uuid=luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet",
        "id": "luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet",
        "index": "3",
        "initrd": "/boot/initramfs-0-rescue-c44543d15b2c4e898912c2497f734e67.img",
        "kernel": "/boot/vmlinuz-0-rescue-c44543d15b2c4e898912c2497f734e67",
        "root": "UUID=65c70529-e9ad-4778-9001-18fe8c525285",
        "title": "Fedora Linux (0-rescue-c44543d15b2c4e898912c2497f734e67) 36 (Workstation Edition)",
        "default": True
    },
    {
        "args": "ro rootflags=subvol=root rd.luks.uuid=luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet $tuned_params",
        "id": "luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet $tuned_params",
        "index": "2",
        "initrd": "/boot/initramfs-6.3.12-100.fc37.x86_64.img $tuned_initrd",
        "kernel": "/boot/vmlinuz-6.3.12-100.fc37.x86_64",
        "root": "UUID=65c70529-e9ad-4778-9001-18fe8c525285",
        "title": "Fedora Linux (6.3.12-100.fc37.x86_64) 37 (Workstation Edition)",
        "default": False
    },
    {
        "args": "ro rootflags=subvol=root rd.luks.uuid=luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet $tuned_params",
        "id": "luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet $tuned_params",
        "index": "1",
        "initrd": "/boot/initramfs-6.4.15-100.fc37.x86_64.img $tuned_initrd",
        "kernel": "/boot/vmlinuz-6.4.15-100.fc37.x86_64",
        "root": "UUID=65c70529-e9ad-4778-9001-18fe8c525285",
        "title": "Fedora Linux (6.4.15-100.fc37.x86_64) 37 (Workstation Edition)",
        "default": False
    },
    {
        "args": "ro rootflags=subvol=root rd.luks.uuid=luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet $tuned_params",
        "id": "luks-9da1fdf5-14ac-49fd-a388-8b1ee48f3df1 rhgb quiet $tuned_params",
        "index": "0",
        "initrd": "/boot/initramfs-6.5.7-100.fc37.x86_64.img $tuned_initrd",
        "kernel": "/boot/vmlinuz-6.5.7-100.fc37.x86_64",
        "root": "UUID=65c70529-e9ad-4778-9001-18fe8c525285",
        "title": "Fedora Linux (6.5.7-100.fc37.x86_64) 37 (Workstation Edition)",
        "default": False
    }
]
```

## Example Playbook

```yaml
- hosts: all
  vars:
    bootloader_settings:
      # Update an existing kernel using path and replacing previous settings
      - kernel:
          path: /boot/vmlinuz-6.5.7-100.fc37.x86_64
        options:
          - name: console
            value: tty0
            state: present
          - previous: replaced
      # Update an existing kernel using index
      - kernel:
          index: 1
        options:
          - name: print-fatal-signals
            value: 1
      # Update an existing kernel using title
      - kernel:
          title: Red Hat Enterprise Linux (4.1.1.1.el8.x86_64) 8
        options:
          - name: no_timer_check
        state: present
      # Add a kernel with arguments
      - kernel:
          path: /boot/vmlinuz-6.5.7-100.fc37.x86_64
          initrd: /boot/initramfs-6.5.7-100.fc37.x86_64.img
          title: My kernel
        options:
          - name: console
            value: tty0
          - name: print-fatal-signals
            value: 1
          - name: no_timer_check
            state: present
        state: present
      # Add a kernel with arguments and copying default arguments
      - kernel:
          path: /boot/vmlinuz-6.5.7-100.fc37.x86_64
          initrd: /boot/initramfs-6.5.7-100.fc37.x86_64.img
          title: My kernel
        options:
          - name: console
            value: tty0
          - copy_default: true
        state: present
      # Remove a kernel
      - kernel:
          title: My kernel
        state: absent
      # Update all kernels
      - kernel: ALL
        options:
          - name: debug
            state: present
      # Update the default kernel
      - kernel: DEFAULT
        options:
          - name: quiet
            state: present
    bootloader_timeout: 5
    bootloader_password: null
    bootloader_remove_password: false
    bootloader_reboot_ok: true
  roles:
    - linux-system-roles.bootloader
```

## rpm-ostree

See README-ostree.md

## License

MIT
