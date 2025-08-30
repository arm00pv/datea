# Deploying the Inventory Management Application to Digital Ocean

This guide provides step-by-step instructions for deploying the Django inventory management application to a Digital Ocean droplet. The application will be served by Gunicorn and Nginx, and will be accessible at `http://zapp.sytes.net/datea`.

This guide also covers setting up a CI/CD pipeline using GitHub Actions for automatic deployments.

## 1. Server Setup

### 1.1. Create a Digital Ocean Droplet

1.  Log in to your Digital Ocean account.
2.  Create a new Droplet.
3.  **Choose an image:** Ubuntu 22.04 LTS is recommended.
4.  **Choose a plan:** A basic shared CPU droplet is sufficient for this application.
5.  **Choose a datacenter region:** Select a region closest to your users.
6.  **Authentication:** Select "SSH keys" for authentication. Add your public SSH key. This is more secure than using a password.
7.  **Finalize and create:** Choose a hostname for your droplet (e.g., `inventory-management-server`) and click "Create Droplet".

Once the droplet is created, you will get an IP address. You will use this IP address to connect to your server via SSH.

### 1.2. Initial Server Setup

Connect to your droplet via SSH using the IP address provided by Digital Ocean:

```bash
ssh root@YOUR_DROPLET_IP
```

It is a security best practice to create a non-root user with `sudo` privileges for day-to-day tasks.

1.  **Create a new user:**

    ```bash
    adduser your_username
    ```

2.  **Grant administrative privileges:**

    ```bash
    usermod -aG sudo your_username
    ```

3.  **Set up the firewall:**

    Enable the Uncomplicated Firewall (ufw) to allow only necessary traffic.

    ```bash
    ufw allow OpenSSH
    ufw allow 'Nginx Full'
    ufw enable
    ```

4.  **Log out from the root user and log in as the new user:**

    ```bash
    exit
    ssh your_username@YOUR_DROPLET_IP
    ```

### 1.3. Install System Dependencies

Now, update the package lists and install the necessary system packages for Python, PostgreSQL, and Nginx.

```bash
sudo apt update
sudo apt install python3-pip python3-dev python3-venv nginx postgresql postgresql-contrib

## 2. Database Setup

Next, you'll create a PostgreSQL database and a dedicated user for your Django application.

1.  **Log in to the PostgreSQL interactive terminal:**

    ```bash
    sudo -u postgres psql
    ```

2.  **Create a new database:**

    ```sql
    CREATE DATABASE inventory_db;
    ```

3.  **Create a new user and set a password:**

    Replace `your_password` with a strong, secure password.

    ```sql
    CREATE USER inventory_user WITH PASSWORD 'your_password';
    ```

4.  **Grant privileges to the new user on the database:**

    ```sql
    GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;
    ```

5.  **Exit the PostgreSQL terminal:**

    ```sql
    \q
    ```

### 2.1. The `DATABASE_URL` Environment Variable

Your application uses the `DATABASE_URL` environment variable to connect to the database. The format for this URL is:

`postgres://<user>:<password>@<host>:<port>/<dbname>`

Based on the steps above, your `DATABASE_URL` will be:

`postgres://inventory_user:your_password@localhost:5432/inventory_db`

You will use this URL later when you configure the application's environment variables. **Remember to replace `your_password` with the actual password you created.**

## 3. Application Deployment

Now, you will deploy the Django application itself. Make sure you are in your home directory.

```bash
cd ~
```

### 3.1. Clone the Repository

Clone your application's source code from GitHub. Replace `your-github-username/your-repo-name.git` with your actual repository URL.

```bash
git clone https://github.com/your-github-username/your-repo-name.git
cd your-repo-name
```

### 3.2. Create a Python Virtual Environment

It's a best practice to create a virtual environment for your project's Python dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
```

Your command prompt should now be prefixed with `(venv)`.

### 3.3. Install Dependencies

Install the required Python packages using `pip`.

```bash
pip install -r requirements.txt
```

### 3.4. Set Up Environment Variables

Your application requires a `SECRET_KEY` and `DATABASE_URL`. A good way to manage this is to create a file named `.env` in the project root and have Gunicorn load it.

**Create the `.env` file:**

```bash
nano .env
```

**Add the following content to the file:**

Replace `your_password` with the database password you created earlier. For the `SECRET_KEY`, you can generate a new one. In your activated virtual environment, run `python` to open a Python shell, then run the following commands to generate a key:
`from django.core.management.utils import get_random_secret_key`
`print(get_random_secret_key())`

```
SECRET_KEY='your_strong_secret_key'
DATABASE_URL='postgres://inventory_user:your_password@localhost:5432/inventory_db'
```

Save and close the file (`Ctrl+X`, then `Y`, then `Enter`).

### 3.5. Run Initial Setup Commands

With the `.env` file created, you can now run the initial setup commands for the Django application.

1.  **Run database migrations:**

    ```bash
    python inventory_management/manage.py migrate
    ```

2.  **Collect static files:**

    This command will collect all static files (CSS, JavaScript, images) into a single directory.

    ```bash
    python inventory_management/manage.py collectstatic --no-input
    ```

3.  **Create a superuser (optional):**

    If you want to access the Django admin interface, create a superuser.

    ```bash
    python inventory_management/manage.py createsuperuser
    ```

Your application is now set up. The next step is to configure Gunicorn to run it.

## 4. Gunicorn and Nginx Setup

You will use Gunicorn as the application server and Nginx as the reverse proxy.

### 4.1. Create a Gunicorn `systemd` Service

Create a `systemd` service file to manage the Gunicorn process. This will ensure that Gunicorn starts automatically on boot.

Create and open the service file for editing:

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Paste the following content into the file. **Remember to replace `your_username` with your actual username.**

```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=your_username
Group=www-data
WorkingDirectory=/home/your_username/your-repo-name
EnvironmentFile=/home/your_username/your-repo-name/.env
ExecStart=/home/your_username/your-repo-name/venv/bin/gunicorn \
          --workers 4 \
          --bind unix:/run/gunicorn.sock \
          --chdir inventory_management \
          inventory_management.wsgi:application

[Install]
WantedBy=multi-user.target
```

Save and close the file. Now, start and enable the Gunicorn service:

```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

You can check the status of the service with:

```bash
sudo systemctl status gunicorn
```

### 4.2. Configure Nginx as a Reverse Proxy

The final step is to configure Nginx to proxy requests to Gunicorn.

Create and open a new Nginx server block configuration file:

```bash
sudo nano /etc/nginx/sites-available/inventory_management
```

Paste the following content into the file. **Replace `your_username` and `zapp.sytes.net` where appropriate.**

```nginx
server {
    listen 80;
    server_name zapp.sytes.net;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /home/your_username/your-repo-name;
    }

    location /datea/ {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header SCRIPT_NAME /datea;
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_redirect off;
    }
}
```

Now, enable this server block by creating a symbolic link to the `sites-enabled` directory:

```bash
sudo ln -s /etc/nginx/sites-available/inventory_management /etc/nginx/sites-enabled
```

Test the Nginx configuration for syntax errors:

```bash
sudo nginx -t
```

If there are no errors, restart Nginx to apply the changes:

```bash
sudo systemctl restart nginx
```

Your application should now be accessible at `http://zapp.sytes.net/datea`. You may need to configure your DNS settings to point `zapp.sytes.net` to your droplet's IP address.

## 5. CI/CD with GitHub Actions

To automate deployments, you can set up a GitHub Actions workflow. This workflow will automatically deploy your application whenever you push changes to the `main` branch.

### 5.1. Add GitHub Secrets

First, you need to add the following secrets to your GitHub repository settings. Go to `Settings` > `Secrets and variables` > `Actions` and add the following secrets:

*   `DO_HOST`: The IP address of your Digital Ocean droplet.
*   `DO_USERNAME`: The username you created for deploying the application (e.g., `your_username`).
*   `DO_SSH_KEY`: The private SSH key that corresponds to the public key you added to the droplet for the `your_username` user. You will need to generate a new key pair for this user if you haven't already.

### 5.2. The Workflow File

The CI/CD pipeline is defined in a YAML file in the `.github/workflows` directory of your repository. The file `deploy.yml` has been created for you. This workflow will:

1.  Trigger on a push to the `main` branch.
2.  Connect to your Digital Ocean droplet via SSH using the secrets you provided.
3.  Navigate to your project directory.
4.  Pull the latest changes from your repository.
5.  Install any new dependencies.
6.  Run database migrations and collect static files.
7.  Restart the Gunicorn service to apply the changes.

With this workflow in place, your application will be automatically updated every time you push to `main`.
```
