

# fedora.linux_system_roles.bootloader role – Configure the GRUB2 boot loader

This role is part of the [fedora.linux_system_roles collection](https://galaxy.ansible.com/ui/repo/published/fedora/linux_system_roles/).

It is not included in `ansible-core`. To check whether it is installed, run `ansible-galaxy collection list`.

To install it use: `ansible-galaxy collection install fedora.linux_system_roles`.

To use it in a playbook, specify: `fedora.linux_system_roles.bootloader`.

- [Entry point `main` – Configure the GRUB2 boot loader](#entry-point-main--configure-the-grub2-boot-loader)

  - [Synopsis](#synopsis)

  - [Parameters](#parameters)

  - [Attributes](#attributes)

  - [Notes](#notes)

  - [Examples](#examples)

  - [Authors](#authors)

## Entry point `main` – Configure the GRUB2 boot loader

### Synopsis

- The `bootloader` role manages GRUB2 boot loader settings: kernel command line parameters, the boot loader timeout, and the boot loader password.

- **Considerations**: Fedora 42 (`grubby-8.40-82.fc42.x86_64`) introduced a bug, [BZ#2361624](https://bugzilla.redhat.com/show_bug.cgi?id=2361624), that changes the default kernel to a newly added kernel. To keep a specific kernel as the default, set `default: true` for that kernel in the **`bootloader_settings`** variable.

- **Collection requirements**: To manage `rpm-ostree` systems, the role needs extra modules from external collections. Install them with `ansible-galaxy collection install -vv -r meta/collection-requirements.yml`. Non-ostree systems need no extra collections.

- For `rpm-ostree` systems, see the `README-ostree.md` file in the role.

### Parameters

| Parameter                                            | Comments |
| ---------------------------------------------------- | --- |
| **bootloader_gather_facts** *boolean*                | Whether to gather bootloader facts containing boot information for all kernels. The role returns the facts in the `bootloader_facts` variable. **Choices:** `false` (default), `true` |
| **bootloader_password** *any*                        | The password to protect boot parameters. When set to `null` or left unset, the role leaves the current password unchanged. The boot loader username is always `root`. Store this value in Ansible Vault. Changing the password is **not** idempotent; use **`bootloader_password_hash`** for idempotent password configuration. You cannot set this variable together with **`bootloader_password_hash`**. |
| **bootloader_password_hash** *any*                   | Precomputed GRUB PBKDF2 SHA512 password hash for the root boot loader user. Generate the hash with `grub2-mkpasswd-pbkdf2` and store it in Ansible Vault. Supply only the resulting `grub.pbkdf2.sha512...` hash, without the command’s explanatory text or a trailing newline. The hash must have a positive iteration count, a nonempty hexadecimal salt consisting of whole bytes, and a 64-byte hexadecimal digest. Setting the same hash repeatedly is idempotent. When `null` or unset, the role writes no hash. An empty string is invalid; to remove a password set **`bootloader_remove_password`**=`true` with this variable unset or `null`. You cannot combine it with **`bootloader_password`** or **`bootloader_remove_password`**=`true`. |
| **bootloader_reboot_ok** *boolean*                   | Whether the role is allowed to reboot the managed host when changes require a reboot to take effect. If `false`, the role sets `bootloader_reboot_required` to `true` instead. **Choices:** `false` (default), `true` |
| **bootloader_remove_password** *boolean*             | Whether to remove the boot loader password configuration. **Choices:** `false` (default), `true` |
| **bootloader_secure_logging** *boolean*              | Whether to suppress potentially sensitive output from tasks that handle credentials by setting `no_log` to `true` on those tasks. **Choices:** `false`, `true` (default) |
| **bootloader_settings** *list / elements=dictionary* | List of kernel entries and their command line parameters to configure. Each entry specifies a kernel and the boot loader settings to apply. **Default:** `[]` |
| • **default** *boolean*                              | Whether to make this kernel the default boot entry. **Choices:** `false` (default), `true` |
| • **kernel** *any / required*                        | The kernel to update settings for. Accepts the string `DEFAULT` or `ALL` to target the default or all kernels, or a dictionary with keys `path`, `index`, `title`, and `initrd` to identify a specific kernel. To modify or remove a kernel, specify one or more of these keys; to add a kernel, specify `path`, `title`, and `initrd`. |
| • **options** *list / elements=dictionary*           | List of boot loader arguments to apply to the specified kernel. |
| • • **copy_default** *boolean*                       | Whether to copy the default arguments to the created kernel. **Choices:** `false` (default), `true` |
| • • **name** *string*                                | The name of the boot loader setting. Not required when using `previous: replaced`. |
| • • **previous** *string*                            | Whether to replace all previous settings with the given settings. The only supported value is `replaced`. **Choices:** `"replaced"` |
| • • **state** *string*                               | Whether the setting is `present` or `absent`. `absent` removes the setting with the given `name`. **Choices:** `"present"` (default), `"absent"` |
| • • **value** *any*                                  | The value for the setting. Not required when the setting has no value, for example `quiet`. The value must not be a YAML boolean; quote values such as `value: "on"` that YAML would parse as a boolean. The value must also not be null; `value:`, `value: ~`, and `value: null` raise an error. |
| • **state** *string*                                 | Whether to keep the kernel entry (`present`) or remove it (`absent`). **Choices:** `"present"` (default), `"absent"` |
| **bootloader_timeout** *any*                         | The GRUB boot loader timeout in seconds. When set to `null` or left unset, the role does not change the timeout setting. |

### Attributes

| Attribute         | Support                                         | Description |
| ----------------- | ----------------------------------------------- | --- |
| **architectures** | **partial**                                     | Supported on AMD and Intel 64-bit architectures (x86-64), the 64-bit ARM architecture (ARMv8.0), and IBM Power Systems, Little Endian (POWER9). Not supported on 32-bit x86 (i686) or other architectures. |
| **platform**      | **Platforms:** **Fedora**, **RHEL**, **CentOS** | Target operating systems. |

### Notes

- **Values returned by the role**:

- - `bootloader_reboot_required` — `true` means the host must reboot to apply the role’s changes. The role sets this when **`bootloader_reboot_ok`** is `false` and it made changes.

- - `bootloader_facts` — boot information for all kernels. The role returns this when **`bootloader_gather_facts`** is `true`.

### Examples

```yaml
- name: Manage kernels by path, index, and title, and add, remove, and copy defaults
  hosts: all
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
    bootloader_reboot_ok: true
  roles:
    - linux-system-roles.bootloader

- name: Gather bootloader facts for all kernels without making changes
  hosts: all
  vars:
    bootloader_gather_facts: true
  roles:
    - linux-system-roles.bootloader

- name: Set a bootloader password (pull the value from Ansible Vault)
  hosts: all
  vars:
    bootloader_password: "{{ vault_bootloader_password }}"
    bootloader_secure_logging: true
  roles:
    - linux-system-roles.bootloader

- name: Set an idempotent password hash from grub2-mkpasswd-pbkdf2
  hosts: all
  vars:
    bootloader_password_hash: "{{ vault_bootloader_password_hash }}"
    bootloader_secure_logging: true
  roles:
    - linux-system-roles.bootloader

- name: Remove the bootloader password
  hosts: all
  vars:
    bootloader_remove_password: true
  roles:
    - linux-system-roles.bootloader

- name: Allow the role to reboot the host automatically
  hosts: all
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

### Authors

- Sergei Petrosian (@spetrosi)
