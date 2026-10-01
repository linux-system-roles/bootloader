

# fedora.linux_system_roles.bootloader role – Configure the GRUB2 boot loader

Note

This role is part of the <a href="https://galaxy.ansible.com/ui/repo/published/fedora/linux_system_roles/" class="reference external">fedora.linux_system_roles collection</a> (version 1.0.0).

It is not included in `ansible-core`. To check whether it is installed, run `ansible-galaxy collection list`.

To install it use: `ansible-galaxy collection install fedora.linux_system_roles`.

To use it in a playbook, specify: `fedora.linux_system_roles.bootloader`.

- <a href="#entry-point-main-configure-the-grub2-boot-loader" id="id1" class="reference internal">Entry point <code class="docutils literal notranslate">main</code> – Configure the GRUB2 boot loader</a>

  - <a href="#synopsis" id="id2" class="reference internal">Synopsis</a>

  - <a href="#parameters" id="id3" class="reference internal">Parameters</a>

  - <a href="#attributes" id="id4" class="reference internal">Attributes</a>

  - <a href="#notes" id="id5" class="reference internal">Notes</a>

  - <a href="#examples" id="id6" class="reference internal">Examples</a>

  - <a href="#authors" id="id7" class="reference internal">Authors</a>

## Entry point <code class="docutils literal notranslate">main</code> – Configure the GRUB2 boot loader

### Synopsis

- The `bootloader` role allows you to manage GRUB2 boot loader settings, kernel command line parameters, boot loader timeout, and boot loader password.

- Considerations: Since Fedora 42, or grubby-8.40-82.fc42.x86_64, there is a bug <a href="https://bugzilla.redhat.com/show_bug.cgi?id=2361624" class="reference external">BZ#2361624</a> that causes the default kernel to change to a newly added kernel. You can ensure that a particular kernel is booted by setting `default: true` for the kernel within the **<a href="#ansible-collections-fedora-linux-system-roles-bootloader-role-parameter-main-bootloader-settings" class="reference internal"><span class="std std-ref"><code class="ansible-option docutils literal notranslate">bootloader_settings</code></span></a>** variable.

- Collection requirements: to manage `rpm-ostree` systems, the role requires additional modules from external collections; install them with `ansible-galaxy collection install -vv -r meta/collection-requirements.yml`. To manage non-ostree systems, the role has no additional requirements.

- For rpm-ostree systems, see the `README-ostree.md` file in the role.

### Parameters

<table class="longtable ansible-option-table docutils align-default" style="width: 100%">
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<thead>
<tr class="row-odd">
<th class="head"><p>Parameter</p></th>
<th class="head"><p>Comments</p></th>
</tr>
</thead>
<tbody>
<tr class="row-even">
<td>&#10;<p><strong>bootloader_gather_facts</strong></p>
<a href="#parameter-main--bootloader_gather_facts" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">boolean</span></p>
</td>
<td><p>Whether to gather bootloader facts containing boot information for all kernels. The facts are returned in the <code class="docutils literal notranslate">bootloader_facts</code> variable.</p>
<p><strong>Choices:</strong></p>
<ul>
<li><p><strong><code class="ansible-option-default-bold docutils literal notranslate">false</code></strong> <span class="ansible-option-choices-default-mark">← (default)</span></p></li>
<li><p><code class="ansible-option-choices-entry docutils literal notranslate">true</code></p></li>
</ul>
</td>
</tr>
<tr class="row-odd">
<td>&#10;<p><strong>bootloader_password</strong></p>
<a href="#parameter-main--bootloader_password" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">any</span></p>
</td>
<td><p>The password to protect boot parameters. When set to <code class="ansible-value docutils literal notranslate">null</code> or left unset, the current password configuration is not modified. The boot loader username is always <code class="ansible-value docutils literal notranslate">root</code>. This value should come from an Ansible vault. Changing the password is <strong>not</strong> idempotent; use <strong><a href="#ansible-collections-fedora-linux-system-roles-bootloader-role-parameter-main-bootloader-password-hash" class="reference internal"><span class="std std-ref"><code class="ansible-option docutils literal notranslate">bootloader_password_hash</code></span></a></strong> for idempotent password configuration. These two variables cannot be used together.</p>
</td>
</tr>
<tr class="row-even">
<td>&#10;<p><strong>bootloader_password_hash</strong></p>
<a href="#parameter-main--bootloader_password_hash" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">any</span></p>
</td>
<td><p>Precomputed GRUB PBKDF2 SHA512 password hash for the root boot loader user. Generate the hash with <code class="docutils literal notranslate">grub2-mkpasswd-pbkdf2</code> and store it in Ansible Vault. Supply only the resulting <code class="docutils literal notranslate">grub.pbkdf2.sha512...</code> hash, without the command’s explanatory text or a trailing newline. The hash must have a positive iteration count, a nonempty hexadecimal salt consisting of whole bytes, and a 64-byte hexadecimal digest. Setting the same hash repeatedly is idempotent. When <code class="ansible-value docutils literal notranslate">null</code> or unset, no hash is written. An empty string is invalid; to remove a password set <strong><a href="#ansible-collections-fedora-linux-system-roles-bootloader-role-parameter-main-bootloader-remove-password" class="reference internal"><span class="std std-ref"><code class="ansible-option docutils literal notranslate">bootloader_remove_password</code></span></a></strong>=<code class="ansible-value docutils literal notranslate">true</code> with this variable unset or <code class="ansible-value docutils literal notranslate">null</code>. Cannot be combined with <strong><a href="#ansible-collections-fedora-linux-system-roles-bootloader-role-parameter-main-bootloader-password" class="reference internal"><span class="std std-ref"><code class="ansible-option docutils literal notranslate">bootloader_password</code></span></a></strong> or <strong><a href="#ansible-collections-fedora-linux-system-roles-bootloader-role-parameter-main-bootloader-remove-password" class="reference internal"><span class="std std-ref"><code class="ansible-option docutils literal notranslate">bootloader_remove_password</code></span></a></strong>=<code class="ansible-value docutils literal notranslate">true</code>.</p>
</td>
</tr>
<tr class="row-odd">
<td>&#10;<p><strong>bootloader_reboot_ok</strong></p>
<a href="#parameter-main--bootloader_reboot_ok" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">boolean</span></p>
</td>
<td><p>Whether the role is allowed to reboot the managed host when changes require a reboot to take effect. If <code class="ansible-value docutils literal notranslate">false</code>, the role sets <code class="docutils literal notranslate">bootloader_reboot_required</code> to <code class="ansible-value docutils literal notranslate">true</code> instead.</p>
<p><strong>Choices:</strong></p>
<ul>
<li><p><strong><code class="ansible-option-default-bold docutils literal notranslate">false</code></strong> <span class="ansible-option-choices-default-mark">← (default)</span></p></li>
<li><p><code class="ansible-option-choices-entry docutils literal notranslate">true</code></p></li>
</ul>
</td>
</tr>
<tr class="row-even">
<td>&#10;<p><strong>bootloader_remove_password</strong></p>
<a href="#parameter-main--bootloader_remove_password" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">boolean</span></p>
</td>
<td><p>Whether to remove the boot loader password configuration.</p>
<p><strong>Choices:</strong></p>
<ul>
<li><p><strong><code class="ansible-option-default-bold docutils literal notranslate">false</code></strong> <span class="ansible-option-choices-default-mark">← (default)</span></p></li>
<li><p><code class="ansible-option-choices-entry docutils literal notranslate">true</code></p></li>
</ul>
</td>
</tr>
<tr class="row-odd">
<td>&#10;<p><strong>bootloader_secure_logging</strong></p>
<a href="#parameter-main--bootloader_secure_logging" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">boolean</span></p>
</td>
<td><p>Whether to suppress potentially sensitive output from tasks that handle credentials by setting <code class="docutils literal notranslate">no_log</code> to <code class="ansible-value docutils literal notranslate">true</code> on those tasks.</p>
<p><strong>Choices:</strong></p>
<ul>
<li><p><code class="ansible-option-choices-entry docutils literal notranslate">false</code></p></li>
<li><p><strong><code class="ansible-option-default-bold docutils literal notranslate">true</code></strong> <span class="ansible-option-choices-default-mark">← (default)</span></p></li>
</ul>
</td>
</tr>
<tr class="row-even">
<td>&#10;<p><strong>bootloader_settings</strong></p>
<a href="#parameter-main--bootloader_settings" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">list</span> / <span class="ansible-option-elements">elements=dictionary</span></p>
</td>
<td><p>List of kernel entries and their command line parameters to configure. Each entry specifies a kernel and the boot loader settings to apply.</p>
<p><strong>Default:</strong> <code class="ansible-option-default docutils literal notranslate">[]</code></p>
</td>
</tr>
<tr class="row-odd">
<td>&#10;&#10;<p>    ↳ <strong>default</strong></p>
<a href="#parameter-main--bootloader_settings/default" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">boolean</span></p>
</td>
<td>&#10;<p>Whether to make this kernel the default boot entry.</p>
<p><strong>Choices:</strong></p>
<ul>
<li><p><strong><code class="ansible-option-default-bold docutils literal notranslate">false</code></strong> <span class="ansible-option-choices-default-mark">← (default)</span></p></li>
<li><p><code class="ansible-option-choices-entry docutils literal notranslate">true</code></p></li>
</ul>
</td>
</tr>
<tr class="row-even">
<td>&#10;&#10;<p>    ↳ <strong>kernel</strong></p>
<a href="#parameter-main--bootloader_settings/kernel" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">any</span> / <span class="ansible-option-required">required</span></p>
</td>
<td>&#10;<p>The kernel to update settings for. Accepts the string <code class="ansible-value docutils literal notranslate">DEFAULT</code> or <code class="ansible-value docutils literal notranslate">ALL</code> to target the default or all kernels, or a dictionary with keys <code class="docutils literal notranslate">path</code>, <code class="docutils literal notranslate">index</code>, <code class="docutils literal notranslate">title</code>, and <code class="docutils literal notranslate">initrd</code> to identify a specific kernel. To modify or remove a kernel, specify one or more of these keys; to add a kernel, specify <code class="docutils literal notranslate">path</code>, <code class="docutils literal notranslate">title</code>, and <code class="docutils literal notranslate">initrd</code>.</p>
</td>
</tr>
<tr class="row-odd">
<td>&#10;&#10;<p>    ↳ <strong>options</strong></p>
<a href="#parameter-main--bootloader_settings/options" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">list</span> / <span class="ansible-option-elements">elements=dictionary</span></p>
</td>
<td>&#10;<p>List of boot loader arguments to apply to the specified kernel.</p>
</td>
</tr>
<tr class="row-even">
<td>&#10;&#10;&#10;<p>        ↳ <strong>copy_default</strong></p>
<a href="#parameter-main--bootloader_settings/options/copy_default" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">boolean</span></p>
</td>
<td>&#10;&#10;<p>Whether to copy the default arguments to the created kernel.</p>
<p><strong>Choices:</strong></p>
<ul>
<li><p><strong><code class="ansible-option-default-bold docutils literal notranslate">false</code></strong> <span class="ansible-option-choices-default-mark">← (default)</span></p></li>
<li><p><code class="ansible-option-choices-entry docutils literal notranslate">true</code></p></li>
</ul>
</td>
</tr>
<tr class="row-odd">
<td>&#10;&#10;&#10;<p>        ↳ <strong>name</strong></p>
<a href="#parameter-main--bootloader_settings/options/name" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">string</span></p>
</td>
<td>&#10;&#10;<p>The name of the boot loader setting. Not required when using <code class="docutils literal notranslate">previous: replaced</code>.</p>
</td>
</tr>
<tr class="row-even">
<td>&#10;&#10;&#10;<p>        ↳ <strong>previous</strong></p>
<a href="#parameter-main--bootloader_settings/options/previous" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">string</span></p>
</td>
<td>&#10;&#10;<p>Whether to replace all previous settings with the given settings. The only supported value is <code class="ansible-value docutils literal notranslate">replaced</code>.</p>
<p><strong>Choices:</strong></p>
<ul>
<li><p><code class="ansible-option-choices-entry docutils literal notranslate">"replaced"</code></p></li>
</ul>
</td>
</tr>
<tr class="row-odd">
<td>&#10;&#10;&#10;<p>        ↳ <strong>state</strong></p>
<a href="#parameter-main--bootloader_settings/options/state" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">string</span></p>
</td>
<td>&#10;&#10;<p>Whether the setting should be <code class="ansible-value docutils literal notranslate">present</code> or <code class="ansible-value docutils literal notranslate">absent</code>. The value <code class="ansible-value docutils literal notranslate">absent</code> removes the setting with the given <code class="docutils literal notranslate">name</code>.</p>
<p><strong>Choices:</strong></p>
<ul>
<li><p><strong><code class="ansible-option-default-bold docutils literal notranslate">"present"</code></strong> <span class="ansible-option-choices-default-mark">← (default)</span></p></li>
<li><p><code class="ansible-option-choices-entry docutils literal notranslate">"absent"</code></p></li>
</ul>
</td>
</tr>
<tr class="row-even">
<td>&#10;&#10;&#10;<p>        ↳ <strong>value</strong></p>
<a href="#parameter-main--bootloader_settings/options/value" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">any</span></p>
</td>
<td>&#10;&#10;<p>The value for the setting. Not required when the setting has no value, for example <code class="ansible-value docutils literal notranslate">quiet</code>. The value must not be a YAML boolean; quote values such as <code class="docutils literal notranslate">value: "on"</code> that YAML would parse as a boolean. The value must also not be null: <code class="docutils literal notranslate">value:</code>, <code class="docutils literal notranslate">value: ~</code>, and <code class="docutils literal notranslate">value: null</code> are not allowed and raise an error.</p>
</td>
</tr>
<tr class="row-odd">
<td>&#10;&#10;<p>    ↳ <strong>state</strong></p>
<a href="#parameter-main--bootloader_settings/state" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">string</span></p>
</td>
<td>&#10;<p>Whether the kernel entry should be <code class="ansible-value docutils literal notranslate">present</code> or removed with <code class="ansible-value docutils literal notranslate">absent</code>.</p>
<p><strong>Choices:</strong></p>
<ul>
<li><p><strong><code class="ansible-option-default-bold docutils literal notranslate">"present"</code></strong> <span class="ansible-option-choices-default-mark">← (default)</span></p></li>
<li><p><code class="ansible-option-choices-entry docutils literal notranslate">"absent"</code></p></li>
</ul>
</td>
</tr>
<tr class="row-even">
<td>&#10;<p><strong>bootloader_timeout</strong></p>
<a href="#parameter-main--bootloader_timeout" class="ansibleOptionLink" title="Permalink to this option"></a>
<p><span class="ansible-option-type">any</span></p>
</td>
<td><p>The GRUB boot loader timeout in seconds. When set to <code class="ansible-value docutils literal notranslate">null</code> or left unset, the role does not change the timeout setting.</p>
</td>
</tr>
</tbody>
</table>

### Attributes

<table class="longtable ansible-option-table docutils align-default" style="width: 100%">
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="row-odd">
<th class="head"><p>Attribute</p></th>
<th class="head"><p>Support</p></th>
<th class="head"><p>Description</p></th>
</tr>
</thead>
<tbody>
<tr class="row-even">
<td>&#10;<p><strong>architectures</strong></p>
<a href="#attribute-architectures" class="ansibleOptionLink" title="Permalink to this attribute"></a>
</td>
<td><p><strong>Support:</strong> <strong>partial</strong></p>
</td>
<td><p>Supported on AMD and Intel 64-bit architectures (x86-64), the 64-bit ARM architecture (ARMv8.0), and IBM Power Systems, Little Endian (POWER9). Not supported on 32-bit x86 (i686) or other architectures.</p>
</td>
</tr>
<tr class="row-odd">
<td>&#10;<p><strong>platform</strong></p>
<a href="#attribute-platform" class="ansibleOptionLink" title="Permalink to this attribute"></a>
</td>
<td><p><strong>Platforms:</strong> <strong>Fedora</strong>, <strong>RHEL</strong>, <strong>CentOS</strong></p>
</td>
<td><p>Target operating systems.</p>
</td>
</tr>
</tbody>
</table>

### Notes

Note

- **Values returned by the role**:

- `bootloader_reboot_required` — if `true`, a reboot is needed to apply the changes made by the role. Set when **<a href="#ansible-collections-fedora-linux-system-roles-bootloader-role-parameter-main-bootloader-reboot-ok" class="reference internal"><span class="std std-ref"><code class="ansible-option docutils literal notranslate">bootloader_reboot_ok</code></span></a>** is `false` and changes were made.

- `bootloader_facts` — contains boot information for all kernels. Returned when **<a href="#ansible-collections-fedora-linux-system-roles-bootloader-role-parameter-main-bootloader-gather-facts" class="reference internal"><span class="std std-ref"><code class="ansible-option docutils literal notranslate">bootloader_gather_facts</code></span></a>** is set to `true`.

### Examples

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

### Authors

- Sergei Petrosian (@spetrosi)

