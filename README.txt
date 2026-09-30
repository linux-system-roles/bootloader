fedora.linux_system_roles.bootloader role -- Configure the GRUB2 boot loader
****************************************************************************

Note:

  This role is part of the fedora.linux_system_roles collection
  (version 1.0.0).It is not included in "ansible-core". To check
  whether it is installed, run "ansible-galaxy collection list".To
  install it use: "ansible-galaxy collection install
  fedora.linux_system_roles".To use it in a playbook, specify:
  "fedora.linux_system_roles.bootloader".

* Entry point "main" -- Configure the GRUB2 boot loader

  * Synopsis

  * Parameters

  * Attributes

  * Notes

  * Examples

  * Authors


Entry point "main" -- Configure the GRUB2 boot loader
=====================================================


Synopsis
--------

* The "bootloader" role allows you to manage GRUB2 boot loader
  settings, kernel command line parameters, boot loader timeout, and
  boot loader password.

* Considerations: Since Fedora 42, or grubby-8.40-82.fc42.x86_64,
  there is a bug BZ#2361624 that causes the default kernel to change
  to a newly added kernel. You can ensure that a particular kernel is
  booted by setting "default: true" for the kernel within the
  "**bootloader_settings**" variable.

* Collection requirements: to manage "rpm-ostree" systems, the role
  requires additional modules from external collections; install them
  with "ansible-galaxy collection install -vv -r meta/collection-
  requirements.yml". To manage non-ostree systems, the role has no
  additional requirements.

* For rpm-ostree systems, see the "README-ostree.md" file in the role.


Parameters
----------

+----------------------------------------------------+----------------------------------------------------+
| Parameter                                          | Comments                                           |
|====================================================|====================================================|
| **bootloader_gather_facts**  boolean               | Whether to gather bootloader facts containing boot |
|                                                    | information for all kernels. The facts are         |
|                                                    | returned in the "bootloader_facts" variable.       |
|                                                    | **Choices:**  * "**false**" ← (default)  * "true"  |
+----------------------------------------------------+----------------------------------------------------+
| **bootloader_password**  any                       | The password to protect boot parameters. When set  |
|                                                    | to "null" or left unset, the current password      |
|                                                    | configuration is not modified. The boot loader     |
|                                                    | username is always "root". This value should come  |
|                                                    | from an Ansible vault. Changing the password is    |
|                                                    | **not** idempotent; use                            |
|                                                    | "**bootloader_password_hash**" for idempotent      |
|                                                    | password configuration. These two variables cannot |
|                                                    | be used together.                                  |
+----------------------------------------------------+----------------------------------------------------+
| **bootloader_password_hash**  any                  | Precomputed GRUB PBKDF2 SHA512 password hash for   |
|                                                    | the root boot loader user. Generate the hash with  |
|                                                    | "grub2-mkpasswd-pbkdf2" and store it in Ansible    |
|                                                    | Vault. Supply only the resulting                   |
|                                                    | "grub.pbkdf2.sha512..." hash, without the          |
|                                                    | command's explanatory text or a trailing newline.  |
|                                                    | The hash must have a positive iteration count, a   |
|                                                    | nonempty hexadecimal salt consisting of whole      |
|                                                    | bytes, and a 64-byte hexadecimal digest. Setting   |
|                                                    | the same hash repeatedly is idempotent. When       |
|                                                    | "null" or unset, no hash is written. An empty      |
|                                                    | string is invalid; to remove a password set        |
|                                                    | "**bootloader_remove_password**"="true" with this  |
|                                                    | variable unset or "null". Cannot be combined with  |
|                                                    | "**bootloader_password**" or                       |
|                                                    | "**bootloader_remove_password**"="true".           |
+----------------------------------------------------+----------------------------------------------------+
| **bootloader_reboot_ok**  boolean                  | Whether the role is allowed to reboot the managed  |
|                                                    | host when changes require a reboot to take effect. |
|                                                    | If "false", the role sets                          |
|                                                    | "bootloader_reboot_required" to "true" instead.    |
|                                                    | **Choices:**  * "**false**" ← (default)  * "true"  |
+----------------------------------------------------+----------------------------------------------------+
| **bootloader_remove_password**  boolean            | Whether to remove the boot loader password         |
|                                                    | configuration.  **Choices:**  * "**false**" ←      |
|                                                    | (default)  * "true"                                |
+----------------------------------------------------+----------------------------------------------------+
| **bootloader_secure_logging**  boolean             | Whether to suppress potentially sensitive output   |
|                                                    | from tasks that handle credentials by setting      |
|                                                    | "no_log" to "true" on those tasks.  **Choices:**   |
|                                                    | * "false"  * "**true**" ← (default)                |
+----------------------------------------------------+----------------------------------------------------+
| **bootloader_settings**  list /                    | List of kernel entries and their command line      |
| elements=dictionary                                | parameters to configure. Each entry specifies a    |
|                                                    | kernel and the boot loader settings to apply.      |
|                                                    | **Default:** "[]"                                  |
+----------------------------------------------------+----------------------------------------------------+
| **default**  boolean                               | Whether to make this kernel the default boot       |
|                                                    | entry.  **Choices:**  * "**false**" ← (default)  * |
|                                                    | "true"                                             |
+----------------------------------------------------+----------------------------------------------------+
| **kernel**  any / required                         | The kernel to update settings for. Accepts the     |
|                                                    | string "DEFAULT" or "ALL" to target the default or |
|                                                    | all kernels, or a dictionary with keys "path",     |
|                                                    | "index", "title", and "initrd" to identify a       |
|                                                    | specific kernel. To modify or remove a kernel,     |
|                                                    | specify one or more of these keys; to add a        |
|                                                    | kernel, specify "path", "title", and "initrd".     |
+----------------------------------------------------+----------------------------------------------------+
| **options**  list / elements=dictionary            | List of boot loader arguments to apply to the      |
|                                                    | specified kernel.                                  |
+----------------------------------------------------+----------------------------------------------------+
| **copy_default**  boolean                          | Whether to copy the default arguments to the       |
|                                                    | created kernel.  **Choices:**  * "**false**" ←     |
|                                                    | (default)  * "true"                                |
+----------------------------------------------------+----------------------------------------------------+
| **name**  string                                   | The name of the boot loader setting. Not required  |
|                                                    | when using "previous: replaced".                   |
+----------------------------------------------------+----------------------------------------------------+
| **previous**  string                               | Whether to replace all previous settings with the  |
|                                                    | given settings. The only supported value is        |
|                                                    | "replaced".  **Choices:**  * ""replaced""          |
+----------------------------------------------------+----------------------------------------------------+
| **state**  string                                  | Whether the setting should be "present" or         |
|                                                    | "absent". The value "absent" removes the setting   |
|                                                    | with the given "name".  **Choices:**  *            |
|                                                    | "**"present"**" ← (default)  * ""absent""          |
+----------------------------------------------------+----------------------------------------------------+
| **value**  any                                     | The value for the setting. Not required when the   |
|                                                    | setting has no value, for example "quiet". The     |
|                                                    | value must not be a YAML boolean; quote values     |
|                                                    | such as "value: "on"" that YAML would parse as a   |
|                                                    | boolean. The value must also not be null:          |
|                                                    | "value:", "value: ~", and "value: null" are not    |
|                                                    | allowed and raise an error.                        |
+----------------------------------------------------+----------------------------------------------------+
| **state**  string                                  | Whether the kernel entry should be "present" or    |
|                                                    | removed with "absent".  **Choices:**  *            |
|                                                    | "**"present"**" ← (default)  * ""absent""          |
+----------------------------------------------------+----------------------------------------------------+
| **bootloader_timeout**  any                        | The GRUB boot loader timeout in seconds. When set  |
|                                                    | to "null" or left unset, the role does not change  |
|                                                    | the timeout setting.                               |
+----------------------------------------------------+----------------------------------------------------+


Attributes
----------

+-----------------------------------+-----------------------------------+-----------------------------------+
| Attribute                         | Support                           | Description                       |
|===================================|===================================|===================================|
| **architectures**                 | **Support: ****partial**          | Supported on AMD and Intel 64-bit |
|                                   |                                   | architectures (x86-64), the       |
|                                   |                                   | 64-bit ARM architecture           |
|                                   |                                   | (ARMv8.0), and IBM Power Systems, |
|                                   |                                   | Little Endian (POWER9). Not       |
|                                   |                                   | supported on 32-bit x86 (i686) or |
|                                   |                                   | other architectures.              |
+-----------------------------------+-----------------------------------+-----------------------------------+
| **platform**                      | **Platforms:** **Fedora**,        | Target operating systems.         |
|                                   | **RHEL**, **CentOS**              |                                   |
+-----------------------------------+-----------------------------------+-----------------------------------+


Notes
-----

Note:

  * **Values returned by the role**:

  * "bootloader_reboot_required" — if "true", a reboot is needed to
    apply the changes made by the role. Set when
    "**bootloader_reboot_ok**" is "false" and changes were made.

  * "bootloader_facts" — contains boot information for all kernels.
    Returned when "**bootloader_gather_facts**" is set to "true".


Examples
--------

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


Authors
-------

* Sergei Petrosian (@spetrosi)
