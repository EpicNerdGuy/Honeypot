---

# SSH Honeypot

This project is a simple **SSH honeypot** built in Python using **Paramiko**.
It emulates a fake SSH server, accepts connections, captures credentials, and provides a basic shell environment to trick attackers into interacting with it.
All activity is logged for later analysis.

---

## Features

* **Custom SSH Banner** → Pretends to be a real OpenSSH server (`SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1`).
* **Fake Shell Emulation** → Supports simple commands:

  * `pwd`
  * `whoami`
  * `ls`
  * `exit`
  * Any other command returns a fake `sudo: command not found`.
* **Credential Capture** → Logs usernames and passwords attempted.
* **Rotating Logs** →

  * `audit.log`: Funnel connection logs.
  * `cmd_audit.log`: Captured credentials and commands.
* **Paramiko Transport** → Handles authentication, channels, and key exchange.

---

## Project Structure

```
.
├── honeypot.py        # main honeypot script
├── server_key         # RSA private key for the fake SSH server
├── audit.log          # funnel logs (rotating)
├── cmd_audit.log      # credentials + command logs (rotating)
└── README.md          # project documentation
```

---

## ⚙️ Requirements

* Python 3.x
* Paramiko (`pip install paramiko`)

---

## 🚀 Usage

1. **Generate a server key** if you don’t have one:

   ```bash
   ssh-keygen -t rsa -b 2048 -f server_key
   ```
2. **Run the honeypot:**

   ```bash
   python3 honeypot.py
   ```
3. **Connect to it** (from attacker’s perspective):

   ```bash
   ssh user@<honeypot-ip> -p 22
   ```
4. The honeypot logs all activity in:

   * `audit.log`
   * `cmd_audit.log`

---

## 📝 Example Interaction

Attacker runs:

```bash
ssh username@honeypot
```

Inside fake shell:

```
corporate-jumpbox2$ pwd
\usr\local\
corporate-jumpbox2$ whoami
corpuser
corporate-jumpbox2$ ls
jumpbox.conf1
corporate-jumpbox2$ exit
Bye
```

---

## Disclaimer

This project is for **educational and research purposes only**.
Do not expose it to the internet without proper isolation — attackers may use it for malicious purposes.
Use at your own risk.


