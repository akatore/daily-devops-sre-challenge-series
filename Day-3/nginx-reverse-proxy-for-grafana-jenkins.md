### Prerequisites

Before applying the configuration, ensure you know the internal ports your services are running on. By default:

* **Grafana:** runs on `http://127.0.0.1:3000`
* **Jenkins:** runs on `http://127.0.0.1:8080`

You will also need SSL certificates. If you are just testing locally, you can use self-signed certificates.

---

### 1. Nginx Configuration

Create a new configuration file in your Nginx directory (e.g., `/etc/nginx/conf.d/dev-tools.conf` or `/etc/nginx/sites-available/dev-tools`).

```nginx
# ==========================================
# Grafana Reverse Proxy
# ==========================================
server {
    listen 443 ssl;
    server_name grafana.local;

    # SSL Configuration (Update paths to your actual certificates)
    ssl_certificate /etc/ssl/certs/grafana.local.crt;
    ssl_certificate_key /etc/ssl/private/grafana.local.key;

    location / {
        proxy_pass http://127.0.0.1:3000;
        
        # Standard Reverse Proxy Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# ==========================================
# Jenkins Reverse Proxy (With Basic Auth)
# ==========================================
server {
    listen 443 ssl;
    server_name jenkins.local;

    # SSL Configuration (Update paths to your actual certificates)
    ssl_certificate /etc/ssl/certs/jenkins.local.crt;
    ssl_certificate_key /etc/ssl/private/jenkins.local.key;

    location / {
        # Basic Authentication Setup
        auth_basic "Restricted Jenkins Access";
        auth_basic_user_file /etc/nginx/.htpasswd;

        proxy_pass http://127.0.0.1:8080;
        
        # Standard Reverse Proxy Headers required by Jenkins
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Fix for Jenkins "It appears that your reverse proxy set up is broken" error
        proxy_read_timeout  90;
        proxy_redirect      http://127.0.0.1:8080 https://jenkins.local;
    }
}

# Optional: Redirect HTTP traffic to HTTPS
server {
    listen 80;
    server_name grafana.local jenkins.local;
    return 301 https://$host$request_uri;
}

```

---

### 2. Setup Basic Authentication for Jenkins

To make the `auth_basic_user_file` work, you need to create a `.htpasswd` file containing the allowed username and encrypted password. You will need the `apache2-utils` (Ubuntu/Debian) or `httpd-tools` (CentOS/RHEL) package.

Run the following command in your terminal to create the file and add a user (e.g., `admin`):

```bash
sudo htpasswd -c /etc/nginx/.htpasswd admin

```

*You will be prompted to type and confirm a password.*

If you want to add more users later, omit the `-c` flag (which creates a new file):

```bash
sudo htpasswd /etc/nginx/.htpasswd another_user

```

---

### 3. Configure Local DNS Resolution

Since `.local` domains are not real public internet domains, your computer needs to know to route them to your local Nginx server.

Edit your `/etc/hosts` file (Linux/macOS) or `C:\Windows\System32\drivers\etc\hosts` (Windows) and add the following line:

```text
127.0.0.1   grafana.local jenkins.local

```

*(If your Nginx server is on a remote machine or VM, replace `127.0.0.1` with the IP address of that server).*

---

### 4. Test and Reload Nginx

Finally, verify that your Nginx configuration has no syntax errors and reload the service:

```bash
# Test the configuration
sudo nginx -t

# If the test is successful, reload Nginx
sudo systemctl reload nginx

```