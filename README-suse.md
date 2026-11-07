# SUSE

On SUSE systems, the role manages the configuration that `grub2-mkconfig` generates instead of using `grubby`: it edits `/etc/default/grub` and `/etc/grub.d/01_password`, checks the boot loader with `pbl` from the `update-bootloader` package, and regenerates `grub.cfg`.

It supports SLES 16 and openSUSE Leap 16 with `grub2` or `grub2-efi`; other boot loaders, such as `grub2-bls` or `systemd-boot`, are refused. SLE 15 is not supported, and the role does not check for it.

## Kernel command line

All boot entries share one kernel command line, so `options` need `kernel: ALL` or `kernel: DEFAULT`. A kernel selected by `path`, `index` or `title` can only be made the default, and adding or removing kernels is not supported.

Options go to `GRUB_CMDLINE_LINUX_DEFAULT`, which the recovery entry does not read; setting a new value also takes the name out of `GRUB_CMDLINE_LINUX`, and a removal applies to both, so the recovery entry loses them. `previous: replaced` replaces `GRUB_CMDLINE_LINUX_DEFAULT` only. A value that is already on the command line is left as it is, together with the other values of its name, so an option such as `console` must list every value it should have, or be removed with `state: absent` first.

The role fails instead of guessing: when an option name has different values in the two variables, when a name or value contains whitespace, quotes, or any of `$`, `` ` ``, `;`, `\`, `{`, `}`, `|`, `&`, `<`, `>` and `#`, or when a variable it reads in `/etc/default/grub` uses shell expansion or escapes, or a command line it changes holds a quoted kernel argument.

## Default entry, timeout and password

`default: true` sets `GRUB_DEFAULT=saved` and saves the selected entry, and `bootloader_timeout` sets `GRUB_TIMEOUT`. The password is required to edit an entry, not to boot it; setting the same password again changes nothing, and the role refuses to manage it while another script in `/etc/grub.d` or `GRUB_USERS` sets one.

## Facts

`bootloader_facts` lists every menu entry that boots a kernel, the Advanced options and recovery entries included, so a kernel can appear more than once.

## Transactional systems

The configuration is regenerated in a new snapshot, which `bootloader_facts` describe, and every change takes effect after a reboot (see [bootloader_reboot_ok](README.md#bootloader_reboot_ok)). Reboot before running `transactional-update` again without `--continue`.
