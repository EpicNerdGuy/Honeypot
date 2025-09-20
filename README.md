# SSH Honeypot (Corporate Jumpbox Emulation)

A lightweight SSH honeypot that emulates a corporate jumpbox shell to collect attacker credentials and commands. Designed for learning, CTF practice, and low-interaction telemetry, not for production exposure of secrets.

---

## Features

* Accepts SSH connections and logs attempted usernames and passwords.
* Emulated interactive shell with basic fake commands (`ls`, `pwd`, `whoami`, `cd`, `exit`).
* Command and credential logging with rotating logs (`audit.log`, `cmd_audit.log`).
* Robust terminal behavior: backspace, Ctrl-C, Ctrl-D, proper prompts and line editing.
* Non-blocking I/O and graceful session teardown for stability.
* Web-based SSH monitoring UI (coming soon)

---

## Roadmap / Coming soon

* **Web-based SSH UI** - a browser-accessible frontend for monitoring sessions and replaying command logs (coming soon).
* Per-directory fake file trees and richer command emulation (`cat`, `ps`, simple `bash`-like responses).
* Optional telemetry export (JSON) and integration with ELK / Grafana dashboards.

---

## Quick Start

> **Requirements:** Python 3.10+, `paramiko` installed, and a generated `server.key` RSA host key present in the project folder.

1. Install dependencies:

```bash
pip install -r requirements.txt
# or
pip install paramiko
```

2. Generate an RSA host key (if you don't already have one):

```bash
ssh-keygen -t rsa -b 2048 -f server.key -N ""
```

3. Make sure the private key is ignored by git (the project provides a `.gitignore`):

```bash
# verify .gitignore contains server.key
git check-ignore -v server.key
```

4. Run the honeypot (example on localhost port 2222):

```bash
python ssh_honeypot.py
```

5. From another terminal test a connection:

```bash
ssh -p 2222 user@127.0.0.1
```

The server will accept the connection and log any attempted credentials and commands.

---

## Logs & Files

* `audit.log` - records connection attempts (client IP, username, password). Rotates after configured size.
* `cmd_audit.log` - records commands executed in the emulated shell.
* `server.key` - the SSH host private key (must **never** be committed to git).
* `server.key.pub` - public host key (optional to keep tracked or ignore).

**Important:** If `server.key` was ever pushed to a remote repository, assume it is compromised — rotate/regenerate the key immediately.

---

## Configuration

* `ssh_honeypot.py` arguments: `honeypot(username, password, port, address)` — the code supports accepting all credentials by default and logs them. Adjust behavior in `check_auth_password` to only accept specific pairs if you prefer.
* Logging format and rotation are defined in the script using Python's `logging` and `RotatingFileHandler`.

---

## Security Considerations

* This is a low-interaction honeypot intended for research and learning. Do **not** run it on a public, production-facing IP without isolating it behind proper monitoring and containment.
* Always ignore and never commit private keys. Use `.gitignore` and `git rm --cached` to stop tracking sensitive files.
* If a private key is accidentally pushed, rotate the key and, if necessary, rewrite history with tools like `git filter-repo` or BFG.

---

## Contributing

PRs welcome. If you add features that increase interaction fidelity (e.g., `cat` or `scp` emulation), please add tests or record sample telemetry to the `examples/` folder.

