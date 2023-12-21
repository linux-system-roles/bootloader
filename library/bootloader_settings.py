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
        suboptions:
            kernel:
                description: Kernels to operate on. Can be a string DEFAULT or ALL, or dict.clear
                required: true
                type: str or dict
            state:
                description: State of the kernel.
                required: false
                type: str
                choices: ["absent", "present"]
                default: "present"
            options:
                description: list bootloader arguments to apply
                required: false
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
actions:
    description: Commands that the module runs
    type: str
    returned: always
    # sample: 'hello world'
"""

import re

from ansible.module_utils.basic import AnsibleModule

# This is a bit of a mystery - bug in pylint?
# pylint: disable=import-error
import ansible.module_utils.six.moves as ansible_six_moves


def get_facts(kernels_info, default_kernel):
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


def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    shared_keys = d1_keys.intersection(d2_keys)
    diff = {o: (d1[o], d2[o]) for o in shared_keys if d1[o] != d2[o]}
    same = set(o for o in shared_keys if d1[o] == d2[o])
    return diff, same


def validate_kernel_initrd(bootloader_setting_kernel, kernel_mod_keys):
    """Validate that initrd is not provided as a single key when not creating a kernel"""
    if (
        len(bootloader_setting_kernel) == 1
        and "initrd" in bootloader_setting_kernel.keys()
    ):
        err = (
            "You can use 'initrd' as a kernel key only when you must create a kernel. To modify an existing kernel, use one of %s"
            % ", ".join(kernel_mod_keys)
        )
        return err
    err = ""
    return err


def get_kernel_to_mod(bootloader_setting_kernel, kernel_mod_keys):
    """From a list of kernels, select not initrd kernel dict to use it for modifying options"""
    for key, value in bootloader_setting_kernel.items():
        if key in kernel_mod_keys:
            return {key: value}


def get_single_kernel(bootloader_setting_kernel):
    """Get kernel in the format expected by 'grubby --update-kernel=' from a one-element dict"""
    kernel_key, kernel_val = list(bootloader_setting_kernel.items())[0]
    kernel_key_prefix = ""
    if kernel_key == "title":
        kernel_key_prefix = "TITLE="
    return kernel_key_prefix + escapeval(kernel_val)


def get_create_kernel(bootloader_setting_kernel):
    """Get kernel in the format expected by 'grubby --add-kernel=' from a multiple-element dict"""
    kernel = ""
    for key, value in bootloader_setting_kernel.items():
        if key == "path":
            kernel += " --add-kernel=" + escapeval(value)
        elif key == "title":
            kernel += " --title=" + escapeval(value)
        elif key == "initrd":
            kernel += " --initrd=" + escapeval(value)
    return kernel.strip()


def validate_kernels(bootloader_setting, bootloader_facts):
    """Validate that user passes bootloader_setting correctly"""
    err = ""
    create_kernel = False
    kernel = ""
    kernel_str_values = ["DEFAULT", "ALL"]
    kernel_keys = ["path", "index", "title", "initrd"]
    kernel_create_keys = ["path", "title", "initrd"]
    kernel_mod_keys = ["path", "title", "index"]
    states = ["present", "absent"]
    if "state" in bootloader_setting and bootloader_setting["state"] not in states:
        err = "State must be one of '%s'" % ", ".join(states)
        return err, create_kernel, kernel
    if (not isinstance(bootloader_setting["kernel"], dict)) and (
        not isinstance(bootloader_setting["kernel"], str)
    ):
        err = (
            "kernel value in %s must be of type str or dict"
            % bootloader_setting["kernel"]
        )
        return err, create_kernel, kernel
    if (isinstance(bootloader_setting["kernel"], str)) and (
        bootloader_setting["kernel"] not in kernel_str_values
    ):
        err = "kernel %s is of type str, it must be one of '%s'" % (
            bootloader_setting["kernel"],
            ", ".join(kernel_str_values),
        )
        return err, create_kernel, kernel
    if isinstance(bootloader_setting["kernel"], str):
        kernel = escapeval(bootloader_setting["kernel"])
        return err, create_kernel, kernel

    """Process bootloader_setting["kernel"] being dict"""
    """Validate kernel key and value"""
    for key, value in bootloader_setting["kernel"].items():
        if key not in kernel_keys:
            err = "kernel key in '%s: %s' must be one of '%s'" % (
                key,
                value,
                ", ".join(kernel_keys),
            )
            return err, create_kernel, kernel
        if (not isinstance(value, str)) and (not isinstance(value, int)):
            err = "kernel value in '%s: %s' must be of type str or int" % (key, value)
            return err, create_kernel, kernel

    if len(bootloader_setting["kernel"]) == 1:
        err = validate_kernel_initrd(bootloader_setting["kernel"], kernel_mod_keys)
        if not err:
            kernel = get_single_kernel(bootloader_setting["kernel"])
        return err, create_kernel, kernel

    """Validate with len(bootloader_setting["kernel"]) > 1"""
    for fact in bootloader_facts:
        # Rename kernel to path in fact dict
        if "kernel" in fact:
            fact["path"] = fact.pop("kernel")
        diff, same = dict_compare(bootloader_setting["kernel"], fact)
        if diff and same:
            err = (
                "A kernel with provided %s already exists and it's other fields are different %s"
                % (same, diff)
            )
            return err, create_kernel, kernel
        elif not same and diff:
            if len(bootloader_setting["kernel"]) != 3 and sorted(
                bootloader_setting["kernel"].keys()
            ) != sorted(kernel_create_keys):
                err = (
                    "To create a kernel, you must provide 3 kernel keys - '%s'"
                    % ", ".join(kernel_create_keys)
                )
                return err, create_kernel, kernel
            create_kernel = True
            break
        elif not diff and same:
            create_kernel = False
            break
    if not create_kernel:
        err = validate_kernel_initrd(bootloader_setting["kernel"], kernel_mod_keys)
        if err:
            return err, create_kernel, kernel
        kernel_to_mod = get_kernel_to_mod(bootloader_setting["kernel"], kernel_mod_keys)
        kernel = get_single_kernel(kernel_to_mod)
    else:
        kernel = get_create_kernel(bootloader_setting["kernel"])
    return err, create_kernel, kernel


def escapeval(val):
    """Make sure val is quoted as in shell"""
    return ansible_six_moves.shlex_quote(str(val))


def get_boot_args(kernel_info):
    """Get arguments from kernel info"""
    args = re.search(r'args="(.*)"', kernel_info)
    if args is None:
        return ""
    return args.group(1).strip()


def get_rm_boot_args_cmd(kernel_info, kernel):
    """Build cmd to rm all existing args for a kernel"""
    bootloader_args = get_boot_args(kernel_info)
    if bootloader_args:
        return (
            "grubby --update-kernel="
            + kernel
            + " --remove-args="
            + escapeval(bootloader_args)
        )


def get_setting_name(kernel_setting):
    """Get setting name based on whether it is with or without a value"""
    if kernel_setting == {"previous": "replaced"}:
        return ""
    if "value" in kernel_setting:
        return kernel_setting["name"] + "=" + str(kernel_setting["value"])
    else:
        return kernel_setting["name"]


def get_add_kernel_cmd(bootloader_setting_options, kernel):
    """Build cmd to add a kernel with specified args"""
    boot_args = ""
    for kernel_setting in bootloader_setting_options:
        setting_name = get_setting_name(kernel_setting)
        boot_args += setting_name + " "
    if len(boot_args) > 0:
        args = "--args=" + escapeval(boot_args.strip())
    # Need to add ability to set --copy-default
    return "grubby %s %s" % (kernel, args)


def get_mod_boot_args_cmd(bootloader_setting_options, kernel, kernel_info):
    """Build cmd to modify args for a kernel"""
    boot_absent_args = ""
    boot_present_args = ""
    boot_mod_args = ""
    bootloader_args = get_boot_args(kernel_info)
    for kernel_setting in bootloader_setting_options:
        setting_name = get_setting_name(kernel_setting)
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
    for bootloader_setting in module.params["bootloader_settings"]:
        rc, kernels_info, stderr = module.run_command("grubby --info=ALL")
        if "Permission denied" in stderr:
            module.fail_json(msg="You must run this as sudo", **result)

        rc, default_kernel, stderr = module.run_command("grubby --default-index")
        bootloader_facts = get_facts(kernels_info, default_kernel)

        err, create_kernel, kernel = validate_kernels(
            bootloader_setting, bootloader_facts
        )
        if err:
            module.fail_json(msg=err, **result)

        # Remove all existing boot settings
        if ({"previous": "replaced"} in bootloader_setting["options"]) and (
            not create_kernel
        ):
            rc, kernel_info, stderr = module.run_command("grubby --info=" + kernel)
            rm_boot_args_cmd = get_rm_boot_args_cmd(kernel_info, kernel)
            if rm_boot_args_cmd:
                rc, stdout, stderr = module.run_command(rm_boot_args_cmd)
                result["changed"] = True
                result["actions"].append(rm_boot_args_cmd)

        # Create a kernel with provided options
        if create_kernel:
            add_kernel_cmd = get_add_kernel_cmd(bootloader_setting["options"], kernel)
            rc, stdout, stderr = module.run_command(add_kernel_cmd)
            result["changed"] = True
            result["actions"].append(add_kernel_cmd)

        # Modify boot settings
        else:
            rc, kernel_info, stderr = module.run_command("grubby --info=" + kernel)
            mod_boot_args_cmd = get_mod_boot_args_cmd(
                bootloader_setting["options"], kernel, kernel_info
            )
            if mod_boot_args_cmd:
                rc, stdout, stderr = module.run_command(mod_boot_args_cmd)
                result["changed"] = True
                result["actions"].append(mod_boot_args_cmd)
            else:
                result["changed"] = False

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
