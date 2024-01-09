#!/usr/bin/python

# Copyright: (c) 2023, Sergei Petrosian <spetrosi@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: bootloader_facts

short_description: Gather information for kernels as Ansible facts

version_added: "0.0.1"

description:
    - "WARNING: Do not use this module directly! It is only for role internal use."
    - Gather information for kernels as Ansible facts

author:
    - Sergei Petrosian (@spetrosi)
"""

EXAMPLES = r"""
# Run with no parameters to gather facts
bootloader_facts:
"""

RETURN = r"""
ansible_facts:
    description: Facts to add to ansible_facts.
    returned: always
    type: complex
    contains:
        bootloader_facts:
            description: Boot information for available kernels
            type: list
            returned: always
            contains:
                args:
                    description: command line arguments passed to the kernel
                    returned: always
                    type: str
                default:
                    description: whether this kernel is default
                    returned: always
                    type: bool
                id:
                    description: kernel id
                    returned: always
                    type: str
                index:
                    description: kernel id
                    returned: always
                    type: str
                initrd:
                    description: kernel initrd
                    returned: always
                    type: str
                kernel:
                    description: kernel path
                    returned: always
                    type: str
                root:
                    description: kernel root
                    returned: always
                    type: str
                title:
                    description: kernel title
                    returned: always
                    type: str
            sample: |-
                {
                    "bootloader_facts": [
                        {
                            "args": "ro rootflags=subvol=root console=tty0 print-fatal-signals=1 no_timer_check quiet debug",
                            "default": false,
                            "id": "14339c81a6054561a8effc83d511ce77-6.6.4-100.fc38.x86_64",
                            "index": "0",
                            "initrd": "/boot/new_initrd",
                            "kernel": "/boot/vmlinuz-6.6.4-100.fc38.x86_64",
                            "root": "UUID=2b95a97a-3f73-4566-b0a3-a11b4e9c3663",
                            "title": "entry_title"
                        },
                        {
                            "args": "ro rootflags=subvol=root console=tty0 print-fatal-signals=1 no_timer_check quiet debug",
                            "default": true,
                            "id": "890cea0fd7b140cf890eb0145b3caa72-6.6.4-100.fc38.x86_64",
                            "index": "1",
                            "initrd": "/boot/initramfs-6.6.4-100.fc38.x86_64.img",
                            "kernel": "/boot/vmlinuz-6.6.4-100.fc38.x86_64",
                            "root": "UUID=2b95a97a-3f73-4566-b0a3-a11b4e9c3663",
                            "title": "Fedora Linux (6.6.4-100.fc38.x86_64) 38 (Cloud Edition)"
                        }
                    ]
                }
"""


import re
from ansible.module_utils.basic import AnsibleModule


def get_facts(kernels_info, default_kernel):
    """Get kernel facts"""
    kernels_info_lines = kernels_info.strip().split("\n")
    kernels = []
    index_count = 0

    for line in kernels_info_lines:
        index = re.search(r"index=(\d+)", line)
        if index:
            is_default = index.group(1) == default_kernel.strip()
            index_count += 1
            kernels.append({})
        search = re.search(r"(.*?)=(.*)", line)
        if search:
            key = search.group(1).strip('"')
            value = search.group(2).strip('"')
            kernels[index_count - 1].update({key: value})
        else:
            kernels[index_count - 1].update({"kernel": line})
        kernels[index_count - 1].update({"default": is_default})
    return kernels


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict()

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(changed=False, ansible_facts=dict(bootloader_facts=dict()))

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    rc, kernels_info, stderr = module.run_command("grubby --info=ALL")
    if "Permission denied" in stderr:
        module.fail_json(msg="You must run this as sudo", **result)
    rc, default_kernel, stderr = module.run_command("grubby --default-index")
    result["ansible_facts"]["bootloader_facts"] = get_facts(
        kernels_info, default_kernel
    )

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
