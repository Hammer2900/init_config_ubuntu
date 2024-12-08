## Apps for help

```
xrand - check monitors
arand - setup monitors
xprop - get class names
lxappearance - prepare folder view
```

## Nuitka settings

```
./switch_i3_window.bin center_window -h 300
nuitka --standalone --onefile --enable-plugin=tk-inter --include-module=_bisect --include-module=_json switch_i3_window.py
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


