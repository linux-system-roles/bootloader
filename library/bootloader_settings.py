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
                type: dict
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


def get_dict_same_keys(dict1, dict2):
    """Shorten dict2 to the same keys as in dict1"""
    return {key1: dict2[key1] for key1 in dict1 if key1 in dict2}


def compare_dicts(dict1, dict2):
    """Compare dict1 to dict2 and return same and different entries"""
    dict1_keys = set(dict1.keys())
    dict2_keys = set(dict2.keys())
    shared_keys = dict1_keys.intersection(dict2_keys)
    diff = {o: (dict1[o], dict2[o]) for o in shared_keys if dict1[o] != dict2[o]}
    same = set(o for o in shared_keys if dict1[o] == dict2[o])
    return diff, same


def validate_kernel_initrd(bootloader_setting_kernel, kernel_mod_keys):
    """Validate that initrd is not provided as a single key when not creating a kernel"""
    if (
        len(bootloader_setting_kernel) == 1
        and "initrd" in bootloader_setting_kernel.keys()
    ):
        err = (
            "You can use 'initrd' as a kernel key only when you must create a kernel. To modify or remove an existing kernel, use one of %s"
            % ", ".join(kernel_mod_keys)
        )
        return err
    err = ""
    return err


def get_kernel_to_mod(bootloader_setting_kernel, kernel_mod_keys):
    """From a list of kernels, select not initrd kernel dict to use it for modifying options"""
    return {
        key: value
        for key, value in bootloader_setting_kernel.items()
        if key in kernel_mod_keys
    }


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
    kernel_action = ""
    kernel = ""
    state = ""
    kernel_str_values = ["DEFAULT", "ALL"]
    kernel_keys = ["path", "index", "title", "initrd"]
    kernel_create_keys = ["path", "title", "initrd"]
    kernel_mod_keys = ["path", "title", "index"]
    states = ["present", "absent"]
    state = bootloader_setting["state"] if "state" in bootloader_setting else "present"

    if "state" in bootloader_setting and bootloader_setting["state"] not in states:
        err = "State must be one of '%s'" % ", ".join(states)
        return err, kernel_action, kernel

    if (not isinstance(bootloader_setting["kernel"], dict)) and (
        not isinstance(bootloader_setting["kernel"], str)
    ):
        err = (
            "kernel value in %s must be of type str or dict"
            % bootloader_setting["kernel"]
        )
        return err, kernel_action, kernel

    if (isinstance(bootloader_setting["kernel"], str)) and (
        bootloader_setting["kernel"] not in kernel_str_values
    ):
        err = "kernel %s is of type str, it must be one of '%s'" % (
            bootloader_setting["kernel"],
            ", ".join(kernel_str_values),
        )
        return err, kernel_action, kernel

    if isinstance(bootloader_setting["kernel"], str):
        kernel_action = "modify" if state == "present" else "remove"
        kernel = escapeval(bootloader_setting["kernel"])
        return err, kernel_action, kernel

    # Process bootloader_setting["kernel"] being dict
    # Validate kernel key and value
    for key, value in bootloader_setting["kernel"].items():
        if key not in kernel_keys:
            err = "kernel key in '%s: %s' must be one of '%s'" % (
                key,
                value,
                ", ".join(kernel_keys),
            )
            return err, kernel_action, kernel
        if (not isinstance(value, str)) and (not isinstance(value, int)):
            err = "kernel value in '%s: %s' must be of type str or int" % (key, value)
            return err, kernel_action, kernel

    # Validate with len(bootloader_setting["kernel"]) == 1
    if len(bootloader_setting["kernel"]) == 1:
        err = validate_kernel_initrd(bootloader_setting["kernel"], kernel_mod_keys)
        if not err:
            kernel = get_single_kernel(bootloader_setting["kernel"])
            kernel_action = "modify" if state == "present" else "remove"
        return err, kernel_action, kernel

    # Validate with len(bootloader_setting["kernel"]) > 1
    for fact in bootloader_facts:
        # Rename kernel to path in fact dict
        if "kernel" in fact:
            fact["path"] = fact.pop("kernel")
        fact_trunc = get_dict_same_keys(bootloader_setting["kernel"], fact)
        diff, same = compare_dicts(bootloader_setting["kernel"], fact_trunc)
        # diff, same = compare_dicts(bootloader_setting["kernel"], fact)
        if diff and same:
            err = (
                "A kernel with provided %s already exists and it's other fields are different %s"
                % (same, diff)
            )
            return err, kernel_action, kernel
        elif not diff and same:
            kernel_action = "modify" if state == "present" else "remove"
            break

    # Process kernel_action when none of the facts had same keys with bootloader_setting["kernel"]
    if not kernel_action:
        if len(bootloader_setting["kernel"]) != 3 and (
            sorted(bootloader_setting["kernel"].keys()) != sorted(kernel_create_keys)
        ):
            err = (
                "To create a kernel, you must provide 3 kernel keys - '%s'"
                % ", ".join(kernel_create_keys)
            )
            return err, kernel_action, kernel
        kernel_action = "create" if state == "present" else "remove"

    if kernel_action == "create":
        kernel = get_create_kernel(bootloader_setting["kernel"])

    err = validate_kernel_initrd(bootloader_setting["kernel"], kernel_mod_keys)
    if err:
        return err, kernel_action, kernel

    if kernel_action == "remove":
        kernel_to_mod = get_kernel_to_mod(bootloader_setting["kernel"], kernel_mod_keys)
        kernel = get_single_kernel(kernel_to_mod)
    elif kernel_action == "modify":
        kernel_to_mod = get_kernel_to_mod(bootloader_setting["kernel"], kernel_mod_keys)
        kernel = get_single_kernel(kernel_to_mod)
    return err, kernel_action, kernel


def escapeval(val):
    """Make sure val is quoted as in shell"""
    return ansible_six_moves.shlex_quote(str(val))


def get_boot_args(kernel_info):
    """Get arguments from kernel info"""
    args = re.search(r'args="(.*)"', kernel_info)
    if not args:
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
    if (
        kernel_setting == {"previous": "replaced"}
        or "copy_default" in kernel_setting.keys()
    ):
        return ""
    if "value" in kernel_setting:
        return kernel_setting["name"] + "=" + str(kernel_setting["value"])
    else:
        return kernel_setting["name"]


def get_add_kernel_cmd(bootloader_setting_options, kernel):
    """Build cmd to add a kernel with specified args"""
    boot_args = ""
    args = ""
    for kernel_setting in bootloader_setting_options:
        setting_name = get_setting_name(kernel_setting)
        boot_args += setting_name + " "
    if len(boot_args) > 0:
        args = "--args=" + escapeval(boot_args.strip())
    if {"copy_default": True} in bootloader_setting_options:
        args += " --copy-default"
    return "grubby %s %s" % (kernel, args.strip())


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
    else:
        return None


def get_rm_kernel_cmd(kernel):
    """Build cmd to remove a kernel"""
    return "grubby --remove-kernel=%s" % kernel


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
        _unused, kernels_info, stderr = module.run_command("grubby --info=ALL")
        if "Permission denied" in stderr:
            module.fail_json(msg="You must run this as sudo", **result)

        _unused, default_kernel, _unused = module.run_command("grubby --default-index")
        bootloader_facts = get_facts(kernels_info, default_kernel)

        err, kernel_action, kernel = validate_kernels(
            bootloader_setting, bootloader_facts
        )
        if err:
            module.fail_json(msg=err, **result)

        # Remove all existing boot settings
        if (
            "options" in bootloader_setting
            and {"previous": "replaced"} in bootloader_setting["options"]
        ) and (kernel_action != "remove"):
            rc, kernel_info, stderr = module.run_command("grubby --info=" + kernel)
            rm_boot_args_cmd = get_rm_boot_args_cmd(kernel_info, kernel)
            if rm_boot_args_cmd:
                _unused, stdout, _unused = module.run_command(rm_boot_args_cmd)
                result["changed"] = True
                result["actions"].append(rm_boot_args_cmd)

        # Create a kernel with provided options
        if kernel_action == "create":
            add_kernel_cmd = get_add_kernel_cmd(bootloader_setting["options"], kernel)
            _unused, stdout, _unused = module.run_command(add_kernel_cmd)
            result["changed"] = True
            result["actions"].append(add_kernel_cmd)

        # Modify boot settings
        if kernel_action == "modify":
            _unused, kernel_info, _unused = module.run_command(
                "grubby --info=" + kernel
            )
            mod_boot_args_cmd = get_mod_boot_args_cmd(
                bootloader_setting["options"], kernel, kernel_info
            )
            if mod_boot_args_cmd:
                _unused, stdout, _unused = module.run_command(mod_boot_args_cmd)
                result["changed"] = True
                result["actions"].append(mod_boot_args_cmd)
            else:
                result["changed"] = False

        # Remove a kernel
        if kernel_action == "remove":
            rm_kernel_cmd = get_rm_kernel_cmd(kernel)
            _unused, stdout, _unused = module.run_command(rm_kernel_cmd)
            result["changed"] = True
            result["actions"].append(rm_kernel_cmd)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
