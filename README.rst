.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.27.0

.. Anchors

.. _ansible_collections.fedora.linux_system_roles.bootloader_role:

.. Title

fedora.linux_system_roles.bootloader role -- Configure the GRUB2 boot loader
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This role is part of the `fedora.linux_system_roles collection <https://galaxy.ansible.com/ui/repo/published/fedora/linux_system_roles/>`_ (version 1.0.0).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it use: :code:`ansible\-galaxy collection install fedora.linux\_system\_roles`.

    To use it in a playbook, specify: :code:`fedora.linux_system_roles.bootloader`.

.. contents::
   :local:
   :depth: 2

.. _ansible_collections.fedora.linux_system_roles.bootloader_role__entrypoint-main:

.. Entry point title

Entry point ``main`` -- Configure the GRUB2 boot loader
-------------------------------------------------------

.. version_added


.. Deprecated


Synopsis
^^^^^^^^

.. Description

- The :literal:`bootloader` role allows you to manage GRUB2 boot loader settings, kernel command line parameters, boot loader timeout, and boot loader password.
- Considerations: Since Fedora 42, or grubby\-8.40\-82.fc42.x86\_64, there is a bug \ `BZ#2361624 <https://bugzilla.redhat.com/show_bug.cgi?id=2361624>`__ that causes the default kernel to change to a newly added kernel. You can ensure that a particular kernel is booted by setting :literal:`default: true` for the kernel within the :ansopt:`fedora.linux\_system\_roles.bootloader#role:main:bootloader\_settings` variable.
- Collection requirements: to manage :literal:`rpm\-ostree` systems, the role requires additional modules from external collections; install them with :literal:`ansible\-galaxy collection install \-vv \-r meta/collection\-requirements.yml`. To manage non\-ostree systems, the role has no additional requirements.
- For rpm\-ostree systems, see the :literal:`README\-ostree.md` file in the role.

.. Requirements


.. Options

Parameters
^^^^^^^^^^

.. tabularcolumns:: \X{1}{3}\X{2}{3}

.. list-table::
  :width: 100%
  :widths: auto
  :header-rows: 1
  :class: longtable ansible-option-table

  * - Parameter
    - Comments

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_gather_facts"></div>

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_gather_facts:

      .. rst-class:: ansible-option-title

      **bootloader_gather_facts**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_gather_facts" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`




      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Whether to gather bootloader facts containing boot information for all kernels. The facts are returned in the :literal:`bootloader\_facts` variable.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_password"></div>

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_password:

      .. rst-class:: ansible-option-title

      **bootloader_password**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_password" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`any`




      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The password to protect boot parameters. When set to :ansval:`null` or left unset, the current password configuration is not modified. The boot loader username is always :ansval:`root`. This value should come from an Ansible vault. Changing the password is :strong:`not` idempotent; use :ansopt:`fedora.linux\_system\_roles.bootloader#role:main:bootloader\_password\_hash` for idempotent password configuration. These two variables cannot be used together.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_password_hash"></div>

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_password_hash:

      .. rst-class:: ansible-option-title

      **bootloader_password_hash**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_password_hash" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`any`




      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Precomputed GRUB PBKDF2 SHA512 password hash for the root boot loader user. Generate the hash with :literal:`grub2\-mkpasswd\-pbkdf2` and store it in Ansible Vault. Supply only the resulting :literal:`grub.pbkdf2.sha512...` hash, without the command's explanatory text or a trailing newline. The hash must have a positive iteration count, a nonempty hexadecimal salt consisting of whole bytes, and a 64\-byte hexadecimal digest. Setting the same hash repeatedly is idempotent. When :ansval:`null` or unset, no hash is written. An empty string is invalid; to remove a password set :ansopt:`fedora.linux\_system\_roles.bootloader#role:main:bootloader\_remove\_password`\ =\ :ansval:`true` with this variable unset or :ansval:`null`. Cannot be combined with :ansopt:`fedora.linux\_system\_roles.bootloader#role:main:bootloader\_password` or :ansopt:`fedora.linux\_system\_roles.bootloader#role:main:bootloader\_remove\_password`\ =\ :ansval:`true`.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_reboot_ok"></div>

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_reboot_ok:

      .. rst-class:: ansible-option-title

      **bootloader_reboot_ok**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_reboot_ok" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`




      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Whether the role is allowed to reboot the managed host when changes require a reboot to take effect. If :ansval:`false`\ , the role sets :literal:`bootloader\_reboot\_required` to :ansval:`true` instead.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_remove_password"></div>

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_remove_password:

      .. rst-class:: ansible-option-title

      **bootloader_remove_password**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_remove_password" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`




      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Whether to remove the boot loader password configuration.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_secure_logging"></div>

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_secure_logging:

      .. rst-class:: ansible-option-title

      **bootloader_secure_logging**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_secure_logging" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`




      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Whether to suppress potentially sensitive output from tasks that handle credentials by setting :literal:`no\_log` to :ansval:`true` on those tasks.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`false`
      - :ansible-option-choices-entry-default:`true` :ansible-option-choices-default-mark:`← (default)`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_settings"></div>

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_settings:

      .. rst-class:: ansible-option-title

      **bootloader_settings**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_settings" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=dictionary`




      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      List of kernel entries and their command line parameters to configure. Each entry specifies a kernel and the boot loader settings to apply.


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`[]`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_settings/default"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_settings/default:

      .. rst-class:: ansible-option-title

      **default**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_settings/default" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`




      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Whether to make this kernel the default boot entry.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_settings/kernel"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_settings/kernel:

      .. rst-class:: ansible-option-title

      **kernel**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_settings/kernel" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`any` / :ansible-option-required:`required`




      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      The kernel to update settings for. Accepts the string :ansval:`DEFAULT` or :ansval:`ALL` to target the default or all kernels, or a dictionary with keys :literal:`path`\ , :literal:`index`\ , :literal:`title`\ , and :literal:`initrd` to identify a specific kernel. To modify or remove a kernel, specify one or more of these keys; to add a kernel, specify :literal:`path`\ , :literal:`title`\ , and :literal:`initrd`.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_settings/options"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_settings/options:

      .. rst-class:: ansible-option-title

      **options**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_settings/options" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=dictionary`




      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      List of boot loader arguments to apply to the specified kernel.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_settings/options/copy_default"></div>

      .. raw:: latex

        \hspace{0.04\textwidth}\begin{minipage}[t]{0.28\textwidth}

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_settings/options/copy_default:

      .. rst-class:: ansible-option-title

      **copy_default**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_settings/options/copy_default" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`




      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Whether to copy the default arguments to the created kernel.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_settings/options/name"></div>

      .. raw:: latex

        \hspace{0.04\textwidth}\begin{minipage}[t]{0.28\textwidth}

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_settings/options/name:

      .. rst-class:: ansible-option-title

      **name**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_settings/options/name" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`




      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      The name of the boot loader setting. Not required when using :literal:`previous: replaced`.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_settings/options/previous"></div>

      .. raw:: latex

        \hspace{0.04\textwidth}\begin{minipage}[t]{0.28\textwidth}

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_settings/options/previous:

      .. rst-class:: ansible-option-title

      **previous**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_settings/options/previous" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`




      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Whether to replace all previous settings with the given settings. The only supported value is :ansval:`replaced`.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`"replaced"`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_settings/options/state"></div>

      .. raw:: latex

        \hspace{0.04\textwidth}\begin{minipage}[t]{0.28\textwidth}

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_settings/options/state:

      .. rst-class:: ansible-option-title

      **state**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_settings/options/state" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`




      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Whether the setting should be :ansval:`present` or :ansval:`absent`. The value :ansval:`absent` removes the setting with the given :literal:`name`.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`"present"` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`"absent"`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_settings/options/value"></div>

      .. raw:: latex

        \hspace{0.04\textwidth}\begin{minipage}[t]{0.28\textwidth}

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_settings/options/value:

      .. rst-class:: ansible-option-title

      **value**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_settings/options/value" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`any`




      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      The value for the setting. Not required when the setting has no value, for example :ansval:`quiet`. The value must not be a YAML boolean; quote values such as :literal:`value: "on"` that YAML would parse as a boolean. The value must also not be null: :literal:`value:`\ , :literal:`value: ~`\ , and :literal:`value: null` are not allowed and raise an error.


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_settings/state"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_settings/state:

      .. rst-class:: ansible-option-title

      **state**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_settings/state" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`




      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Whether the kernel entry should be :ansval:`present` or removed with :ansval:`absent`.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`"present"` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`"absent"`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-main--bootloader_timeout"></div>

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__parameter-main__bootloader_timeout:

      .. rst-class:: ansible-option-title

      **bootloader_timeout**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-main--bootloader_timeout" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`any`




      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The GRUB boot loader timeout in seconds. When set to :ansval:`null` or left unset, the role does not change the timeout setting.


      .. raw:: html

        </div>


.. Attributes


Attributes
^^^^^^^^^^

.. tabularcolumns:: \X{2}{10}\X{3}{10}\X{5}{10}

.. list-table::
  :width: 100%
  :widths: auto
  :header-rows: 1
  :class: longtable ansible-option-table

  * - Attribute
    - Support
    - Description

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="attribute-architectures"></div>

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__attribute-main__architectures:

      .. rst-class:: ansible-option-title

      **architectures**

      .. raw:: html

        <a class="ansibleOptionLink" href="#attribute-architectures" title="Permalink to this attribute"></a>

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      :ansible-attribute-support-label:`Support: \ `\ :ansible-attribute-support-partial:`partial`


      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Supported on AMD and Intel 64\-bit architectures (x86\-64), the 64\-bit ARM architecture (ARMv8.0), and IBM Power Systems, Little Endian (POWER9). Not supported on 32\-bit x86 (i686) or other architectures.


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="attribute-platform"></div>

      .. _ansible_collections.fedora.linux_system_roles.bootloader_role__attribute-main__platform:

      .. rst-class:: ansible-option-title

      **platform**

      .. raw:: html

        <a class="ansibleOptionLink" href="#attribute-platform" title="Permalink to this attribute"></a>

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      :ansible-attribute-support-property:`Platforms:` |antsibull-internal-nbsp|:ansible-attribute-support-full:`Fedora`, :ansible-attribute-support-full:`RHEL`, :ansible-attribute-support-full:`CentOS`


      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Target operating systems.


      .. raw:: html

        </div>



.. Notes

Notes
^^^^^

.. note::
   - :strong:`Values returned by the role`\ :
   - :literal:`bootloader\_reboot\_required` — if :ansval:`true`\ , a reboot is needed to apply the changes made by the role. Set when :ansopt:`fedora.linux\_system\_roles.bootloader#role:main:bootloader\_reboot\_ok` is :ansval:`false` and changes were made.
   - :literal:`bootloader\_facts` — contains boot information for all kernels. Returned when :ansopt:`fedora.linux\_system\_roles.bootloader#role:main:bootloader\_gather\_facts` is set to :ansval:`true`.

.. Seealso


Examples
^^^^^^^^

.. code-block:: yaml+jinja

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
^^^^^^^

- Sergei Petrosian (@spetrosi)



.. Extra links


.. Parsing errors
