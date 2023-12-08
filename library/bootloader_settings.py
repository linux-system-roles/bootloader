#!/usr/bin/python

# Copyright: (c) 2023, Sergei Petrosian <spetrosi@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: bootloader_settings

short_description: Configure grubby boot loader arguments for specified kernels

version_added: "0.0.1"

description:
    - "WARNING: Do not use this module directly! It is only for role internal use."
    - Configure grubby boot loader arguments for specified kernels

options:
    bootloader_settings:
        description: List of dict of kernels and their command line parameters that you want to set.
        required: true
        type: list
        elements: dict

author:
    - Sergei Petrosian (@spetrosi)
"""

EXAMPLES = r"""
- name: Test with a message
  bootloader_settings:
    bootloader_settings:
"""

RETURN = r"""
# These are examples of possible return values, and in general should use other names for return values.
# original_message:
#     description: The original name param that was passed in.
#     type: str
#     returned: always
#     sample: 'hello world'
# message:
#     description: The output message that the test module generates.
#     type: str
#     returned: always
#     sample: 'goodbye'
"""

import re

from ansible.module_utils.basic import AnsibleModule

# This is a bit of a mystery - bug in pylint?
# pylint: disable=import-error
import ansible.module_utils.six.moves as ansible_six_moves


def escapeval(val):
    """make sure val is quoted as in shell"""
    return ansible_six_moves.shlex_quote(str(val))


def get_kernels(bootloader_setting_kernel, kernels_keys):
    kernels = []
    for kernel_key in kernels_keys:
        if (
            kernel_key in bootloader_setting_kernel
            and kernel_key != bootloader_setting_kernel
        ):
            kernel_key_prefix = ""
            if kernel_key == "kernel_title":
                kernel_key_prefix = "TITLE="
            if not isinstance(bootloader_setting_kernel[kernel_key], list):
                kernels.append(
                    kernel_key_prefix + str(bootloader_setting_kernel[kernel_key])
                )
            else:
                for kernel_entry in bootloader_setting_kernel[kernel_key]:
                    kernels.append(kernel_key_prefix + str(kernel_entry))
        elif kernel_key == bootloader_setting_kernel:
            kernels.append(bootloader_setting_kernel)
    return kernels


def get_boot_args(kernel_info):
    args = re.search(r'args="(.*)"', kernel_info)
    if args is None:
        return ""
    return args.group(1).strip()


def get_rm_boot_args_cmd(kernel_info, kernel):
    bootloader_args = get_boot_args(kernel_info)
    if bootloader_args:
        return (
            "grubby --update-kernel="
            + kernel
            + " --remove-args="
            + escapeval(bootloader_args)
        )


def get_mod_boot_args_cmd(bootloader_setting_options, kernel, kernel_info):
    boot_absent_args = ""
    boot_present_args = ""
    boot_mod_args = ""
    bootloader_args = get_boot_args(kernel_info)
    for kernel_setting in bootloader_setting_options:
        if {"previous": "replaced"} == kernel_setting:
            continue
        if "value" in kernel_setting:
            setting_name = kernel_setting["name"] + "=" + str(kernel_setting["value"])
        else:
            setting_name = kernel_setting["name"]
        if "state" in kernel_setting and kernel_setting["state"] == "absent":
            if re.search(r"(^|$| )" + setting_name + r"(^|$| )", bootloader_args):
                boot_absent_args += setting_name + " "
        else:
            if not re.search(r"(^|$| )" + setting_name + r"(^|$| )", bootloader_args):
                boot_present_args += setting_name + " "
    if boot_absent_args:
        boot_mod_args = " --remove-args=" + escapeval(boot_absent_args.strip())
    if len(boot_present_args) > 0:
        boot_mod_args += " --args=" + escapeval(boot_present_args.strip())
    if boot_mod_args:
        return "grubby --update-kernel=" + kernel + boot_mod_args


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        bootloader_settings=dict(type="list", required=True, elements="dict")
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(changed=False, actions=list())

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    kernels_keys = ["kernel_index", "kernel_path", "kernel_title", "DEFAULT", "ALL"]
    for bootloader_setting in module.params["bootloader_settings"]:
        kernels = get_kernels(bootloader_setting["kernel"], kernels_keys)
        if not kernels:
            module.fail_json(
                msg="bootloader_settings.kernel must contain one of %s"
                % ", ".join(kernels_keys),
                **result
            )
        for kernel in kernels:
            kernel = escapeval(kernel)
            # Remove all existing boot settings
            if {"previous": "replaced"} in bootloader_setting["options"]:
                rc, stdout, stderr = module.run_command("grubby --info=" + kernel)
                rm_boot_args_cmd = get_rm_boot_args_cmd(stdout, kernel)
                if rm_boot_args_cmd:
                    rc, stdout, stderr = module.run_command(str(rm_boot_args_cmd))
                    result["changed"] = True
                    result["actions"].append(rm_boot_args_cmd)
            rc, stdout, stderr = module.run_command("grubby --info=" + kernel)
            # Configure boot settings
            mod_boot_args_cmd = get_mod_boot_args_cmd(
                bootloader_setting["options"], kernel, stdout
            )
            if mod_boot_args_cmd:
                rc, stdout, stderr = module.run_command(mod_boot_args_cmd)
                result["changed"] = True
                result["actions"].append(mod_boot_args_cmd)
    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    # if module.check_mode:
    #     module.exit_json(**result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
