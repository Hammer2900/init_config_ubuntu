## Apps for help

```
xrand - check monitors
arand - setup monitors
xprop - get class names
lxappearance - prepare folder view
```

## Bars and other staff

```
https://github.com/greshake/i3status-rust
```

## Mount NTFS

```
sudo fdisk -l
sudo mount -t ntfs-3g /dev/nvme0n1p2 /mnt/ntfs
```

## Settings

```
xset q - show you the current settings for the x
xset r rate 250 30 - key repeat rate like windows
xset r rate 200 30 - key repeat rate like mac os
xset m 6 1 - mouse pointer speed like Mac os
```
---

|  No | Example                                         | Description                                                                 |
| --: | :---------------------------------------------- | :-------------------------------------------------------------------------- |
|   1 | `ssh -D 1337 user@host`                         | Connect to remote host and set up a SOCKS5 proxy                            |
|   2 | `ssh -L 8080:www.example.com:80 user@host`      | Connect to remote host and forward local port 8080 to remote host's port 80 |
|   3 | `ssh -t user@host command`                      | Connect to remote host and run a command                                    |
|   4 | `ssh -X user@host`                              | Connect to remote host and enable X11 forwarding                            |
|   5 | `ssh -i ~/.ssh/id_rsa user@host`                | Connect to remote host using a private key                                  |
|   6 | `ssh -N user@host`                              | Connect to remote host without running a command                            |
|   7 | `ssh -R 8080:localhost:8080 user@host`          | Connect to remote host and forward remote port 8080 to local port 8080      |
|   8 | `ssh -f user@host`                              | Connect to remote host and run commands in the background                   |
|   9 | `ssh -p 2222 user@host`                         | Connect to remote host on port 2222                                         |
|  10 | `ssh -C user@host`                              | Connect to remote host and enable compression                               |
|  11 | `ssh -o StrictHostKeyChecking=no user@host`     | Connect to remote host and skip host key checking                           |
|  12 | `ssh -o UserKnownHostsFile=/dev/null user@host` | Connect to remote host and disable known hosts checking                     |
|  13 | `ssh -o LogLevel=QUIET user@host`               | Connect to remote host and disable logging                                  |
|  14 | `ssh -o ConnectionAttempts=3 user@host`         | Connect to remote host and try 3 times before giving up                     |
|  15 | `ssh -o ServerAliveInterval=30 user@host`       | Connect to remote host and send keepalive packets every 30 seconds          |

---

| Fab command                   | Description                                                | Example                                                              |
| ----------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------- |
| fab -h                        | Show help                                                  | fab -h                                                               |
| fab -l                        | List available tasks                                       | fab -l                                                               |
| fab -d task                   | Display detailed info about a task                         | fab -d deploy:production                                             |
| fab -P                        | Run tasks with a parallel pool of processes                | fab -P deploy:production                                             |
| fab -R role                   | Run tasks on a remote server                               | fab -R web deploy:production                                         |
| fab -f file                   | Get tasks from an alternate fabfile                        | fab -f other-fabfile.py deploy:production                            |
| fab --list                    | List available tasks (alias for -l)                        | fab --list                                                           |
| fab --show                    | Show detailed info about a task (alias for -d)             | fab --show deploy:production                                         |
| fab --pool                    | Run tasks with a parallel pool of processes (alias for -P) | fab --pool deploy:production                                         |
| fab --roles                   | Run tasks on a remote server (alias for -R)                | fab --roles web deploy:production                                    |
| fab --fabfile                 | Get tasks from an alternate fabfile (alias for -f)         | fab --fabfile other-fabfile.py deploy:production                     |
| fab --version                 | Show version and exit                                      | fab --version                                                        |
| fab --shortlist               | List available tasks (short format)                        | fab --shortlist                                                      |
| fab --hide                    | Hide command-line output on success                        | fab --hide deploy:production                                         |
| fab --show-output             | Show command-line output even on success                   | fab --show-output deploy:production                                  |
| fab --no-colors               | Don't colorize command output                              | fab --no-colors deploy:production                                    |
| fab --no-pty                  | Don't use a pty when executing shell commands              | fab --no-pty deploy:production                                       |
| fab --shell                   | Don't execute commands, just print them                    | fab --shell deploy:production                                        |
| fab --initial-password-prompt | Prompt for a password before connecting                    | fab --initial-password-prompt deploy:production                      |
| fab --no-agent                | Don't use SSH agent for authentication                     | fab --no-agent deploy:production                                     |
| fab --ssh-config-path         | Specify an alternate SSH config path                       | fab --ssh-config-path=other-config.cfg deploy:production             |
| fab --ssh-common-args         | Specify common SSH args                                    | fab --ssh-common-args="-o LogLevel=quiet" deploy:production          |
| fab --ssh-extra-args          | Specify extra SSH args                                     | fab --ssh-extra-args="-o StrictHostKeyChecking=no" deploy:production |
| fab --disable-known-hosts     | Disables SSH known hosts file                              | fab --disable-known-hosts deploy:production                          |
| fab --keepalive               | Send keepalive packets while executing tasks               | fab --keepalive=60 deploy:production                                 |
| fab --linewise                | Enable linewise output                                     | fab --linewise deploy:production                                     |
| fab --abort-on-prompts        | Abort when SSH prompts for input                           | fab --abort-on-prompts deploy:production                             |
| fab --skip-bad-hosts          | Skip over unreachable hosts                                | fab --skip-bad-hosts deploy:production                               |
| fab --skip-unknown-tasks      | Skip over unknown tasks                                    | fab --skip-unknown-tasks deploy:production                           |
| fab --set                     | Set a default value for a command argument                 | fab --set user=admin deploy:production                               |
| fab --config                  | Load config from a file                                    | fab --config=config.cfg deploy:production                            |

---

| Option | Description                                                      | Example                |
| ------ | ---------------------------------------------------------------- | ---------------------- |
| -l     | List partition tables for the specified devices and then exit.   | fdisk -l               |
| -u     | Give the start and end cylinders in units of sectors.            | fdisk -u /dev/sda      |
| -v     | Display the program version and then exit.                       | fdisk -v               |
| -b     | Specify the sector size.                                         | fdisk -b 512 /dev/sda  |
| -c     | Display the BIOS geometry.                                       | fdisk -c /dev/sda      |
| -h     | Display help and then exit.                                      | fdisk -h               |
| -I     | Display information about the specified device.                  | fdisk -I /dev/sda      |
| -s     | Display the size of a partition.                                 | fdisk -s /dev/sda1     |
| -S     | Specify the sector size.                                         | fdisk -S 2048 /dev/sda |
| -u     | Give the start and end cylinders in units of sectors.            | fdisk -u /dev/sda      |
| -V     | Display the program version and then exit.                       | fdisk -V               |
| -d     | Delete a partition.                                              | fdisk -d /dev/sda      |
| -e     | Enter interactive mode after reading the partition table.        | fdisk -e /dev/sda      |
| -f     | Force wiping out of the partition table on the specified device. | fdisk -f /dev/sda      |
| -g     | Display the cylinder/head/sector geometry.                       | fdisk -g /dev/sda      |
| -i     | Enter interactive mode.                                          | fdisk -i /dev/sda      |
| -n     | Do not actually write to the disk.                               | fdisk -n /dev/sda      |
| -p     | Preserve the existing partition table.                           | fdisk -p /dev/sda      |
| -q     | Quiet operation.                                                 | fdisk -q /dev/sda      |
| -r     | Re-read partition table from the specified device.               | fdisk -r /dev/sda      |
| -t     | Change the system type of the specified partition.               | fdisk -t /dev/sda      |
| -w     | Write the partition table to the specified device and exit.      | fdisk -w /dev/sda      |
| -x     | Display the expert command menu.                                 | fdisk -x /dev/sda      |
| -y     | Assume yes to all questions.                                     | fdisk -y /dev/sda      |

---

| Command               | Description                                       | Example                                                    |
| --------------------- | ------------------------------------------------- | ---------------------------------------------------------- |
| mount                 | Used to mount a filesystem                        | mount /dev/sda1 /mnt                                       |
| mount -a              | Mount all filesystems in fstab                    | mount -a                                                   |
| mount -o remount      | Remount a filesystem                              | mount -o remount,rw /                                      |
| mount -o loop         | Mount a filesystem in a file                      | mount -o loop image.iso /mnt/iso                           |
| mount -t              | Specify the filesystem type                       | mount -t ext4 /dev/sda1 /mnt                               |
| mount -r              | Mount read-only                                   | mount -r /dev/sda1 /mnt                                    |
| mount -o ro           | Mount read-only                                   | mount -o ro,loop image.iso /mnt/iso                        |
| mount -l              | List all mounted filesystems                      | mount -l                                                   |
| mount -n              | Mount without writing in /etc/mtab                | mount -n -t ext4 /dev/sda1 /mnt                            |
| mount -o bind         | Mount one directory to another                    | mount -o bind /olddir /newdir                              |
| mount -u              | Unmount a filesystem                              | mount -u /mnt                                              |
| mount -o move         | Move a mounted filesystem                         | mount -o move /old /new                                    |
| mount -o noexec       | Mount filesystem without execution                | mount -o noexec /dev/sda1 /mnt                             |
| mount -o nosuid       | Mount filesystem without setuid                   | mount -o nosuid /dev/sda1 /mnt                             |
| mount -o nouser       | Mount filesystem without user access              | mount -o nouser /dev/sda1 /mnt                             |
| mount -o nodev        | Mount filesystem without devices                  | mount -o nodev /dev/sda1 /mnt                              |
| mount -o noatime      | Mount filesystem without access time              | mount -o noatime /dev/sda1 /mnt                            |
| mount -o noauto       | Mount filesystem without autoconfig               | mount -o noauto /dev/sda1 /mnt                             |
| mount -o nodiratime   | Mount filesystem without directory access time    | mount -o nodiratime /dev/sda1 /mnt                         |
| mount -o noquota      | Mount filesystem without quota                    | mount -o noquota /dev/sda1 /mnt                            |
| mount -o nouser_xattr | Mount filesystem without user extended attributes | mount -o nouser_xattr /dev/sda1 /mnt                       |
| mount -o context      | Mount filesystem with specified SELinux context   | mount -o context=system_u:object_r:var_t:s0 /dev/sda1 /mnt |
| mount -o comment      | Mount filesystem with specified comment           | mount -o comment="My Filesystem" /dev/sda1 /mnt            |
| mount -o user         | Mount filesystem with specified user              | mount -o user=someuser /dev/sda1 /mnt                      |
| mount -o users        | Mount filesystem with user access                 | mount -o users /dev/sda1 /mnt                              |
| mount -o uid          | Mount filesystem with specified user id           | mount -o uid=1000 /dev/sda1 /mnt                           |
| mount -o gid          | Mount filesystem with specified group id          | mount -o gid=1000 /dev/sda1 /mnt                           |
| mount -o mode         | Mount filesystem with specified permission        | mount -o mode=0777 /dev/sda1 /mnt                          |

---

| Option | Description                                                                                               | Example                           |
| ------ | --------------------------------------------------------------------------------------------------------- | --------------------------------- |
| -a     | Archive mode                                                                                              | cp -a /tmp/src/. /tmp/dest/       |
| -b     | Make a backup of each existing destination file                                                           | cp -b file1 file2                 |
| -d     | Preserve links                                                                                            | cp -d /usr/bin/firefox ~/Desktop/ |
| -f     | Force overwrite                                                                                           | cp -f file1 file2                 |
| -i     | Prompt before overwrite                                                                                   | cp -i file1 file2                 |
| -l     | Create link                                                                                               | cp -l file1 file2                 |
| -n     | Do not overwrite an existing file                                                                         | cp -n file1 file2                 |
| -p     | Preserve file attributes                                                                                  | cp -p file1 file2                 |
| -R     | Copy directories recursively                                                                              | cp -R /tmp/src/ /tmp/dest/        |
| -r     | Copy directories recursively                                                                              | cp -r /tmp/src/ /tmp/dest/        |
| -s     | Create symbolic links instead of copying                                                                  | cp -s file1 file2                 |
| -u     | Copy only when the SOURCE file is newer than the destination file or when the destination file is missing | cp -u file1 file2                 |
| -v     | Verbosely describe what is being done                                                                     | cp -v file1 file2                 |
| -x     | Do not cross filesystem boundaries                                                                        | cp -x file1 file2                 |
| -z     | Compress file data during the copy                                                                        | cp -z file1 file2                 |

---

| Option | Description                                          | Example                 |
| ------ | ---------------------------------------------------- | ----------------------- |
| -l     | List all files in a directory                        | sudo -l                 |
| -u     | Specify the user whose files will be listed          | sudo -u username -l     |
| -s     | Run a shell as the specified user                    | sudo -s                 |
| -i     | Run a login shell                                    | sudo -i                 |
| -n     | Non-interactive mode                                 | sudo -n command         |
| -v     | Update the user's timestamp                          | sudo -v                 |
| -k     | Invalidate the user's timestamp                      | sudo -k                 |
| -e     | Edit a file as the specified user                    | sudo -e filename        |
| -c     | Run the specified command configuration              | sudo -c command         |
| -p     | Preserve environment variables                       | sudo -p                 |
| -H     | Set the HOME environment variable to the target user | sudo -H command         |
| -P     | Preserve the current directory                       | sudo -P command         |
| -r     | Run a command with the root privileges               | sudo -r command         |
| -g     | Run a command with group privileges                  | sudo -g group command   |
| -b     | Run a command in the background                      | sudo -b command         |
| -h     | Display help information                             | sudo -h                 |
| -V     | Display version information                          | sudo -V                 |
| -d     | Display debug information                            | sudo -d                 |
| -m     | Specify a custom security policy                     | sudo -m policy          |
| -S     | Read password from the standard input                | sudo -S command         |
| -E     | Preserve the environment variables                   | sudo -E command         |
| -t     | Run a command with the specified type                | sudo -t type command    |
| -Z     | Set the security context                             | sudo -Z context         |
| -T     | Set the timeout value                                | sudo -T timeout command |
| -a     | Specify authentication method                        | sudo -a method command  |

---

| Option                       | Description                                          | Example                                     |
| ---------------------------- | ---------------------------------------------------- | ------------------------------------------- |
| workspace                    | Switch to the specified workspace                    | i3-msg workspace 4                          |
| move                         | Move the container in the direction specified        | i3-msg move left                            |
| resize                       | Resize the container in the direction specified      | i3-msg resize set width 600 px              |
| split                        | Split the container in the direction specified       | i3-msg split horizontal                     |
| border                       | Change the border style of the focused container     | i3-msg border normal                        |
| layout                       | Change the layout of the focused container           | i3-msg layout tabbed                        |
| floating                     | Toggle the floating state of the focused container   | i3-msg floating toggle                      |
| mark                         | Mark the focused container with the specified name   | i3-msg mark "my_window"                     |
| bar                          | Make changes to the bar                              | i3-msg bar mode dock                        |
| exec                         | Run the specified command                            | i3-msg exec --no-startup-id firefox         |
| restart                      | Restart i3                                           | i3-msg restart                              |
| shutdown                     | Shutdown i3                                          | i3-msg shutdown                             |
| focus                        | Change the focus to the specified container          | i3-msg focus left                           |
| move_workspace               | Move the specified workspace to the output           | i3-msg move workspace "2" to output "HDMI1" |
| workspace_back_and_forth     | Switch to the next/previous workspace                | i3-msg workspace back_and_forth             |
| workspace_next               | Switch to the next workspace                         | i3-msg workspace next                       |
| workspace_prev               | Switch to the previous workspace                     | i3-msg workspace prev                       |
| fullscreen                   | Toggle the fullscreen state of the focused container | i3-msg fullscreen toggle                    |
| scratchpad                   | Move the focused container to the scratchpad         | i3-msg scratchpad show                      |
| debug                        | Print debugging information                          | i3-msg debug tree                           |
| msg_reload                   | Reload i3 configuration                              | i3-msg reload                               |
| msg_nagbar                   | Show a nagbar message                                | i3-msg nagbar "message"                     |
| msg_reload_and_restart       | Reload configuration and restart                     | i3-msg reload_and_restart                   |
| msg_shutdown_and_exit        | Shutdown and exit i3                                 | i3-msg shutdown_and_exit                    |
| msg_bar_config               | Configure the bar                                    | i3-msg bar config                           |
| msg_append_layout            | Append the layout to the current workspace           | i3-msg append_layout ~/.i3/my_layout.json   |
| msg_workspace_layout         | Set the layout of the current workspace              | i3-msg workspace_layout default             |
| msg_floating                 | Toggle the floating state of a container             | i3-msg floating toggle                      |
| msg_move_container           | Move the container in the direction specified        | i3-msg move container left                  |
| msg_resize_container         | Resize the container in the direction specified      | i3-msg resize container set width 600 px    |
| msg_border                   | Change the border style of the container             | i3-msg border normal                        |
| msg_layout                   | Change the layout of the container                   | i3-msg layout tabbed                        |
| msg_mark                     | Mark the container with the specified name           | i3-msg mark "my_window"                     |
| msg_focus                    | Change the focus to the specified container          | i3-msg focus left                           |
| msg_sticky                   | Toggle the sticky state of the container             | i3-msg sticky toggle                        |
| msg_floating_toggle          | Toggle the floating state of the container           | i3-msg floating toggle                      |
| msg_workspace_back_and_forth | Switch to the next/previous workspace                | i3-msg workspace back_and_forth             |
| msg_workspace_next           | Switch to the next workspace                         | i3-msg workspace next                       |
| msg_workspace_prev           | Switch to the previous workspace                     | i3-msg workspace prev                       |
| msg_fullscreen_toggle        | Toggle the fullscreen state of the container         | i3-msg fullscreen toggle                    |
| msg_scratchpad               | Move the container to the scratchpad                 | i3-msg scratchpad show                      |
| msg_move_workspace           | Move the workspace to the output                     | i3-msg move workspace "2" to output "HDMI1" |

---

| Option | Description                                                      | Example          |
| ------ | ---------------------------------------------------------------- | ---------------- |
| -a     | Displays all network interfaces, both active and inactive        | ifconfig -a      |
| -s     | Displays statistics for the specified interfaces                 | ifconfig -s      |
| -v     | Displays verbose output for the specified interfaces             | ifconfig -v      |
| -i     | Displays the IP address for the specified interface              | ifconfig -i eth0 |
| -m     | Displays MAC addresses for the specified interfaces              | ifconfig -m eth0 |
| -n     | Displays the network mask for the specified interface            | ifconfig -n eth0 |
| -b     | Displays the broadcast address for the specified interface       | ifconfig -b eth0 |
| -l     | Displays the link status of the specified interface              | ifconfig -l eth0 |
| -r     | Displays the routing table for the specified interface           | ifconfig -r eth0 |
| -t     | Displays the current TCP connections for the specified interface | ifconfig -t eth0 |
| -u     | Displays the current UDP connections for the specified interface | ifconfig -u eth0 |
| -h     | Displays the list of available options                           | ifconfig -h      |
| -c     | Displays the configuration of the specified interface            | ifconfig -c eth0 |
| -d     | Displays the DHCP settings for the specified interface           | ifconfig -d eth0 |
| -p     | Displays the port forwarding rules for the specified interface   | ifconfig -p eth0 |
| -e     | Displays the Ethernet address for the specified interface        | ifconfig -e eth0 |
| -g     | Displays the gateway address for the specified interface         | ifconfig -g eth0 |
| -m     | Displays the multicast addresses for the specified interface     | ifconfig -m eth0 |
| -o     | Displays the IP options for the specified interface              | ifconfig -o eth0 |
| -x     | Displays the extended information for the specified interface    | ifconfig -x eth0 |

---

| Option                                      | Description                                      |
| ------------------------------------------- | ------------------------------------------------ |
| navi                                        | Default behavior                                 |
| navi fn welcome                             | Show cheatsheets for navi itself                 |
| navi --print                                | Doesn't execute the snippet                      |
| navi --tldr docker                          | Search for docker cheatsheets using tldr         |
| navi --cheatsh docker                       | Search for docker cheatsheets using cheatsh      |
| navi --path '/some/dir:/other/dir'          | Use .cheat files from custom paths               |
| navi --query git                            | Filter results by "git"                          |
| navi --query 'create db' --best-match       | Autoselect the snippet that best matches a query |
| db=my navi --query 'create db' --best-match | Same, but set the value for the \ variable |
| navi repo add denisidoro/cheats             | Import cheats from a git repository              |
| eval "$(navi widget zsh)"                   | Load the zsh widget                              |
| navi --finder 'skim'                        | Set skim as finder, instead of fzf               |
| navi --fzf-overrides '--with-nth 1,2'       | Show only the comment and tag columns            |
| navi --fzf-overrides '--no-select-1'        | Prevent autoselection in case of single line     |
| navi --fzf-overrides-var '--no-select-1'    | Same, but for variable selection                 |
| navi --fzf-overrides '--nth 1,2'            | Only consider the first two columns for search   |
| navi --fzf-overrides '--no-exact'           | Use looser search algorithm                      |
| navi --tag-rules='git,!checkout'            | Show non-checkout git snippets only              |

---

