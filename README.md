# bootloader

[![ansible-lint.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/ansible-lint.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/ansible-lint.yml) [![ansible-test.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/ansible-test.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/ansible-test.yml) [![codeql.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/codeql.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/codeql.yml) [![codespell.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/codespell.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/codespell.yml) [![markdownlint.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/markdownlint.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/markdownlint.yml) [![python-unit-test.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/python-unit-test.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/python-unit-test.yml) [![qemu-kvm-integration-tests.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/qemu-kvm-integration-tests.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/qemu-kvm-integration-tests.yml) [![tft.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/tft.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/tft.yml) [![tft_citest_bad.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/tft_citest_bad.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/tft_citest_bad.yml) [![woke.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/woke.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/woke.yml)

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

## Considerations

Since Fedora 42, or grubby-8.40-82.fc42.x86_64, there is a bug [BZ#2361624](https://bugzilla.redhat.com/show_bug.cgi?id=2361624) that causes the default kernel to change to a newly added kernel.
You can ensure that a particular kernel is booted by setting the `default: true` entry for the kernel within the [bootloader_settings](#bootloader_settings) variable.

## Role Variables

### bootloader_gather_facts

Whether to gather [bootloader_facts](#bootloader_facts) that contain boot information for all kernels.

Default: `false`

Type: `bool`

### bootloader_settings

Use this variable to list kernels and their command line parameters.

Available keys:

1. `kernel` - with this, specify the kernel to update settings for.
Each entry should specify a kernel using one or more keys.

    If you want to add a kernel, you must specify three keys: `path`, `title`, `initrd`.

    If you want to modify or remove a kernel, you can specify one or more keys.

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

3. `options` - use this to specify settings to update

    * `name` - The name of the setting. Omit `name` when using `replaced`.
    * `value` - The value for the setting. You must omit `value` if the setting has no value, e.g. `quiet`.
      **NOTE** - a value must not be [YAML bool type](https://yaml.org/type/bool.html).
      One situation where this might be a problem is using `value: on` or other
      YAML `bool` typed value.  You must quote these values, or otherwise pass
      them as a value of `str` type e.g.  `value: "on"`.  The same applies to `null` values.
      If you specify a value, it must not be `null` - values such as `value:` or `value: ~`
      or `value: null` are not allowed and will raise an error.
    * `state` - `present` (default) or `absent`. The value `absent` means to remove a setting with the given `name` - the name must be provided.
    * `previous` - Optional - the only supported value is `replaced` - use this to specify that the previous settings should be replaced with the given settings.
    * `copy_default` - Optional - when creating a kernel, you can specify `copy_default: true` to copy the default arguments to the created kernel.

4. `default` - boolean that identifies whether to make this kernel the default.
By default, the role does not change the default kernel.

For an example, see [Example Playbook](#example-playbook).

Default: `{}`

Type: `dict`

### bootloader_timeout

Use this variable to customize the loading time of the GRUB bootloader.

Default: `5`

Type: `int`

### bootloader_password

Use this variable to protect boot parameters with a password.

**WARNING**: Changing the bootloader password is not idempotent.

The bootloader username is always `root`.

This should come from vault.

If unset, current configuration is not touched.

Default: `null`

Type: `string`

### bootloader_remove_password

Set this variable to `true` to remove the bootloader password.

Default: `false`

Type: `bool`

### bootloader_reboot_ok

If `true`, the role will reboot the managed host when it detects that changes require a reboot to take effect.

If `false`, it is up to you to determine when to reboot the managed host.

The role will return the variable `bootloader_reboot_required` (see below) with a value of `true` to indicate that changes have occurred which need a reboot to take effect.

Default: `false`

Type: `bool`

## Variables Exported by the Role

The role exports the following variables:

### bootloader_reboot_needed

Default: `false` - if `true`, this means a reboot is needed to apply the changes made by the role.

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
        default: false
      # Update an existing kernel using index
      - kernel:
          index: 1
        options:
          - name: print-fatal-signals
            value: 1
        default: true
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
