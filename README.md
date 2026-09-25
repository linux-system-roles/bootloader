# linux-system-roles.bootloader

[![citest.yml](https://github.com/linux-system-roles/bootloader/actions/workflows/citest.yml/badge.svg)](https://github.com/linux-system-roles/bootloader/actions/workflows/citest.yml)

The bootloader role allows you to manage GRUB2 boot loader settings, kernel command line parameters, boot loader timeout, and boot loader password.

## Supported Platforms

This role supports managed nodes running the following operating systems:
RHEL and CentOS 7, 8, 9, 10, Fedora.

This role requires Ansible version 2.9 or newer.

### Supported Architectures

This role currently supports configuring `grub2` boot loader which runs on the following architectures:

* AMD and Intel 64-bit architectures (x86-64)

* The 64-bit ARM architecture (ARMv8.0)

* IBM Power Systems, Little Endian (POWER9)

## Collection Requirements

The role requires additional collections to manage `rpm-ostree` systems.
Please run the following command to install them:

```bash
$ ansible-galaxy collection install -r meta/collection-requirements.yml
```

## Considerations

Since Fedora 42, or grubby-8.40-82.fc42.x86_64, there is a bug [BZ#2361624](https://bugzilla.redhat.com/show_bug.cgi?id=2361624) that causes the default kernel to change to a newly added kernel.
You can ensure that a particular kernel is booted by setting the `default: true` entry for the kernel within the [bootloader_settings](#bootloader_settings) variable.

## Configuring GRUB Boot Loader Settings

These variables control the core GRUB boot loader configuration.
This includes kernel command line parameters, timeout, and boot information gathering.

### Variables

<a id="bootloader_settings"></a>**bootloader_settings** (`list` / `dict`) - List of kernel entries and their command line parameters to configure.
Each entry specifies a kernel and the boot loader settings to apply.
Default: `[]`.

> **kernel** (`raw` / required) - The kernel to update settings for. Accepts the string `DEFAULT` or `ALL` to target the default or all kernels, or a dictionary with keys `path`, `index`, `title`, and `initrd` to identify a specific kernel.

> **state** (`str`) - Whether the kernel entry should be present (`present`) or removed (`absent`). Choices: `present`, `absent`. Default: `present`.

> **options** (`list` / `dict`) - List of boot loader arguments to apply to the specified kernel.

> > **name** (`str`) - The name of the boot loader setting. Not required when using `previous: replaced`.

> > **value** (`raw`) - The value for the setting. Not required when the setting has no value, for example `quiet`. The value must not be a YAML boolean or null type.

> > **state** (`str`) - Whether the setting should be present (`present`) or removed (`absent`). The value `absent` removes the setting with the given `name`. Choices: `present`, `absent`. Default: `present`.

> > **previous** (`str`) - Whether to replace all previous settings with the given settings. The only supported value is `replaced`. Choices: `replaced`.

> > **copy_default** (`bool`) - Whether to copy the default arguments to the created kernel. Default: `false`.

> **default** (`bool`) - Whether to make this kernel the default boot entry. Default: `false`.

<a id="bootloader_timeout"></a>**bootloader_timeout** (`raw`) - The GRUB boot loader timeout in seconds.
When set to `null` or left unset, the role does not change the timeout setting.

<a id="bootloader_gather_facts"></a>**bootloader_gather_facts** (`bool`) - Whether to gather bootloader facts containing boot information for all kernels.
The facts are returned in the [`bootloader_facts`](#bootloader_facts) variable.
Default: `false`.

### Example Playbooks

#### Updating Kernel Command Line Parameters

This example shows how to update settings for specific kernels, add and remove kernels, and update all or default kernels.

```yaml
- hosts: all
  vars:
    bootloader_settings:
      - kernel:
          path: /boot/vmlinuz-6.5.7-100.fc37.x86_64
        options:
          - name: console
            value: tty0
            state: present
          - previous: replaced
      - kernel: ALL
        options:
          - name: debug
            state: present
      - kernel: DEFAULT
        options:
          - name: quiet
            state: present
    bootloader_timeout: 5
    bootloader_reboot_ok: true
  roles:
    - linux-system-roles.bootloader
```

#### Gathering Boot Information

This example gathers bootloader facts for all kernels without making any changes.

```yaml
- hosts: all
  vars:
    bootloader_gather_facts: true
  roles:
    - linux-system-roles.bootloader
```

## Bootloader Password Protection

Use these variables to protect GRUB boot parameters with a password or to manage secure Ansible logging.
The bootloader username is always `root`.

### Variables

<a id="bootloader_password"></a>**bootloader_password** (`raw`) - The password to protect boot parameters.
When set to `null` or left unset, the current password configuration is not modified.
The boot loader username is always `root`.
This value should come from an Ansible vault.

<a id="bootloader_password_hash"></a>**bootloader_password_hash** (`raw`) - Precomputed GRUB PBKDF2 SHA512 password hash for the root boot loader user.
When null or unset, no hash is written.
Setting the same hash repeatedly is idempotent.
Store the hash in Ansible Vault.
Cannot be combined with bootloader_password or bootloader_remove_password=true.

<a id="bootloader_remove_password"></a>**bootloader_remove_password** (`bool`) - Whether to remove the boot loader password configuration.
Default: `false`.

<a id="bootloader_secure_logging"></a>**bootloader_secure_logging** (`bool`) - Whether to suppress potentially sensitive output from tasks that handle credentials by setting `no_log` to `true` on those tasks.
Default: `true`.

### Example Playbooks

#### Setting a Bootloader Password

In a real environment, pull the password from Ansible Vault.

```yaml
- hosts: all
  vars:
    bootloader_password: "{{ vault_bootloader_password }}"
    bootloader_secure_logging: true
  roles:
    - linux-system-roles.bootloader
```

#### Setting an Idempotent Password Hash

Generate the hash with `grub2-mkpasswd-pbkdf2` and store it in Ansible Vault for idempotent password configuration.

```yaml
- hosts: all
  vars:
    bootloader_password_hash: "{{ vault_bootloader_password_hash }}"
    bootloader_secure_logging: true
  roles:
    - linux-system-roles.bootloader
```

#### Removing the Bootloader Password

```yaml
- hosts: all
  vars:
    bootloader_remove_password: true
  roles:
    - linux-system-roles.bootloader
```

## System Reboot Behavior

Use this variable to control whether the role is permitted to automatically reboot the managed host when GRUB changes require a restart to take effect.

### Variables

<a id="bootloader_reboot_ok"></a>**bootloader_reboot_ok** (`bool`) - Whether the role is allowed to reboot the managed host when changes require a reboot to take effect.
If `false`, the role sets [`bootloader_reboot_required`](#bootloader_reboot_required) to `true` instead.
Default: `false`.

### Example Playbooks

#### Allowing Automatic Reboot

```yaml
- hosts: all
  vars:
    bootloader_reboot_ok: true
    bootloader_settings:
      - kernel: DEFAULT
        options:
          - name: crashkernel
            value: 512M
  roles:
    - linux-system-roles.bootloader
```

## Return Variables

The following variables are set by the role and can be used in subsequent tasks.

<a id="bootloader_reboot_required"></a>**bootloader_reboot_required** (`bool`)

If `true`, a reboot is needed to apply the changes made by the role.
Set when [`bootloader_reboot_ok`](#bootloader_reboot_ok) is `false` and changes were made.
Returned: changed.

<a id="bootloader_facts"></a>**bootloader_facts** (`list`)

Contains boot information for all kernels.
Returned when [`bootloader_gather_facts`](#bootloader_gather_facts) is set to `true`.
Returned: when bootloader_gather_facts is true.

Example:

```yaml
[
    {
        "args": "ro rootflags=subvol=root rhgb quiet",
        "index": "0",
        "initrd": "/boot/initramfs-6.5.7-100.fc37.x86_64.img",
        "kernel": "/boot/vmlinuz-6.5.7-100.fc37.x86_64",
        "root": "UUID=65c70529-...",
        "title": "Fedora Linux (6.5.7-100.fc37.x86_64) 37",
        "default": true
    }
]
```

## rpm-ostree

See README-ostree.md

## License

MIT
