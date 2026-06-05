

Challanges: the syntaxes
- df -h
- ps -aux
- free -h
- top -b -n1 | head -n 10

sudo apt-get update
sudo apt-get install mailutils msmtp msmtp-mta -y

Learnings: I know the logic, i used while loop for menu operation, and installed crontab using
        ```
        sudo su
        apt-get update
        apt-get install cron
        ```
        `* */4 * * *`
        - its step of every 4 hour...


-----
To get the `mail` command working in a GitHub Codespace and sending emails to your Gmail account, there are two separate things you need to fix based on your screenshot and request.

First, your script is trying to read a file (`report.txt`) that hasn't been created yet. Second, GitHub Codespaces don't have a mail server configured by default, so the `mail` command doesn't know how to route the email to Gmail.

Here is the step-by-step guide to fixing both issues.

### 1. Fix the "No such file or directory" Error

In your terminal, the script failed with: `./menu-based-system-health-check-script.sh: line 19: report.txt: No such file or directory`.

Before the `send_report` function tries to redirect `< report.txt` into the `mail` command, you must generate the file. You can update your function to temporarily create it:

```bash
send_report() {
    echo "Sending comprehensive report via email..."
    # Create the report file first
    echo "This is the system health report." > report.txt
    
    # Now send it
    mail -s "System Health Report" abhijeetkatore@gmail.com < report.txt
    
    # Optional: clean up the file after sending
    rm report.txt
}

```

*(Note: To make this a true comprehensive report, you would append your `df`, `ps`, `free`, and `top` outputs into `report.txt` rather than just echoing them to the screen!)*

---

### 2. Set Up Mail Routing in Codespaces

To send mail from a lightweight Linux container like a Codespace to Gmail, the standard method is to use **`msmtp`** as an SMTP relay. This tells your Codespace to log into Gmail's servers to send the email, bypassing typical container restrictions.

#### Step A: Generate a Google App Password

Because you use Gmail, you cannot use your standard Google password for command-line scripts.

1. Go to your Google Account management page.
2. Search for **App Passwords** (you must have 2-Step Verification enabled).
3. Create a new App Password (name it "Codespaces" or similar) and copy the 16-character code it gives you.

#### Step B: Install the Required Packages

Run the following commands in your Codespace terminal to install the `mail` command and the `msmtp` relay:

```bash
sudo apt-get update
sudo apt-get install mailutils msmtp msmtp-mta -y

```

#### Step C: Configure `msmtp`

You need to create a configuration file that tells `msmtp` how to authenticate with your Gmail.

1. Open a new file in your home directory called `.msmtprc`:
```bash
nano ~/.msmtprc

```


2. Paste the following configuration, replacing `YOUR_APP_PASSWORD` with the 16-character code from Step A. *(Since you are sending it to yourself, your "from" and "user" will be your email address).*
```text
defaults
auth           on
tls            on
tls_trust_file /etc/ssl/certs/ca-certificates.crt
logfile        ~/.msmtp.log

account        gmail
host           smtp.gmail.com
port           587
from           abhijeetkatore@gmail.com
user           abhijeetkatore@gmail.com
password       YOUR_APP_PASSWORD

# Set a default account
account default : gmail

```


3. Save and exit (In nano: `Ctrl+O`, `Enter`, `Ctrl+X`).

#### Step D: Set the Correct File Permissions

For security reasons, `msmtp` will refuse to run if other users can read your password file. Run this to lock it down:

```bash
chmod 600 ~/.msmtprc

```

### 3. Test It!

Now that `msmtp` is configured and masking as your default Mail Transfer Agent (MTA), your original `mail` command will work.

Run your script, select option `5`, and check your Gmail inbox!