# Deployment Instructions for Digital Ocean with Apache2

This guide provides instructions for deploying the inventory management application on a Digital Ocean server running Ubuntu with an existing Apache2 setup.

## 1. Server Setup

First, connect to your server via SSH.

### 1.1. Install System Dependencies

You likely have most of these installed. Ensure that `virtualenv` and the MySQL client libraries are installed.

```bash
sudo apt update
sudo apt install python3-pip python3-dev virtualenv default-libmysqlclient-dev build-essential
```

### 1.2. Project Directory

Your project should be cloned into `/var/www/webhost/datea/`.

```bash
# Ensure you are in the correct directory
cd /var/www/webhost/datea/
```

### 1.3. Create and Activate Virtual Environment

If you haven't already, create a virtual environment and activate it.

```bash
virtualenv venv
source venv/bin/activate
```

### 1.4. Install Python Dependencies

Install the required Python packages, which now includes the MySQL driver.

```bash
pip install -r requirements.txt
```

## 2. Django Configuration

### 2.1. Set Environment Variables for Database

For the application to connect to your MySQL database, it needs a `DATABASE_URL`. You should set this as an environment variable for security.

You will need to create a `.env` file in the project's root directory (`/var/www/webhost/datea/`) to store your database credentials.

```bash
sudo nano /var/www/webhost/datea/.env
```

Add the following line to the file, replacing `YOUR_DB_USER`, `YOUR_DB_PASSWORD`, and `YOUR_DB_NAME` with your actual MySQL credentials. The IP address is the one you provided.

```
DATABASE_URL='mysql://YOUR_DB_USER:YOUR_DB_PASSWORD@64.225.55.254:3306/YOUR_DB_NAME'
```

### 2.2. Run Migrations

Apply the database migrations to create the database schema in your MySQL database.

```bash
python inventory_management/manage.py migrate
```

### 2.3. Collect Static Files

Collect all static files into a single directory for Apache to serve.

```bash
python inventory_management/manage.py collectstatic
```

### 2.4. Create a Superuser

Create a superuser to access the Django admin interface.

```bash
python inventory_management/manage.py createsuperuser
```

## 3. Gunicorn Setup

### 3.1. Update Gunicorn Systemd Service

You need to create or update the systemd service file for Gunicorn to manage the process and load the environment variables from your `.env` file.

```bash
sudo nano /etc/systemd/system/gunicorn-datea.service
```

Paste the following content into the file. Make sure to replace `<your-user>` with your username.

```ini
[Unit]
Description=gunicorn daemon for datea app
After=network.target

[Service]
User=<your-user>
Group=www-data
WorkingDirectory=/var/www/webhost/datea
EnvironmentFile=/var/www/webhost/datea/.env
ExecStart=/var/www/webhost/datea/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind 127.0.0.1:8000 \
          inventory_management.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start and enable the Gunicorn service.

```bash
sudo systemctl start gunicorn-datea
sudo systemctl enable gunicorn-datea
```

## 4. Apache2 Setup

### 4.1. Update Apache2 Configuration

You need to add a configuration block for the `datea` app to your existing `webhost-le-ssl.conf` file.

```bash
sudo nano /etc/apache2/sites-enabled/webhost-le-ssl.conf
```

Add the following lines inside the `<VirtualHost *:443>` block, alongside your other app configurations:

```apache
    # --- Configuration for Datea App ---
    Alias /datea/static/ /var/www/webhost/datea/staticfiles/
    <Directory /var/www/webhost/datea/staticfiles>
        Require all granted
    </Directory>

    ProxyPass /datea/ http://127.0.0.1:8000/
    ProxyPassReverse /datea/ http://127.0.0.1:8000/
```

The final file should look something like this (some sections omitted for brevity):
```apache
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName zapp.sytes.net
    DocumentRoot /var/www/webhost

    # ... your other app configs ...

    # --- Configuration for Datea App ---
    Alias /datea/static/ /var/www/webhost/datea/staticfiles/
    <Directory /var/www/webhost/datea/staticfiles>
        Require all granted
    </Directory>

    ProxyPass /datea/ http://127.0.0.1:8000/
    ProxyPassReverse /datea/ http://127.0.0.1:8000/

    # ... rest of your config ...
</VirtualHost>
</IfModule>
```

### 4.2. Test and Restart Apache2

Test your Apache configuration for syntax errors and restart the service.

```bash
sudo apache2ctl configtest
sudo systemctl restart apache2
```

## 5. Final Django Setting for Subdirectory

Because the application is served from the `/datea/` subdirectory, you need to adjust your Django settings.

In `inventory_management/settings.py`, add this line:

```python
FORCE_SCRIPT_NAME = '/datea'
```

After adding this, restart the Gunicorn service for the change to take effect:
```bash
sudo systemctl restart gunicorn-datea
```

Your application should now be accessible at `https://zapp.sytes.net/datea/`.