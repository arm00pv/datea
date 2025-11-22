# Deployment Guide

This guide provides step-by-step instructions for deploying the inventory management application on a production server using Apache2, Gunicorn, and MySQL.

## 1. Preliminary Setup: Virtual Environment and Dependencies

Before configuring the servers, it's crucial to set up the project environment correctly.

### a. Create a Virtual Environment

First, create a Python virtual environment in your project's root directory. This will isolate the project's dependencies from the system's Python packages.

```bash
cd /path/to/your/project/
python3 -m venv venv
```

### b. Activate the Virtual Environment

Activate the new environment. You will need to do this every time you work on the project in a new terminal session.

```bash
source venv/bin/activate
```

### c. Install Dependencies

With the virtual environment active, install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

## 2. File Permissions

For the web server to access your project files, you need to set the correct ownership and permissions. The user running the Gunicorn service (e.g., `www-data`) must be able to read and execute the project files.

```bash
sudo chown -R www-data:www-data /path/to/your/project/
sudo chmod -R 755 /path/to/your/project/
```

## 3. Apache2 Web Server Configuration

This section details how to configure Apache2 to serve the Django application.

### a. Update Apache Configuration

First, you need to add a new `<Location>` block to your Apache site configuration file (e.g., `/etc/apache2/sites-enabled/webhost-le-ssl.conf`) to proxy requests to the Gunicorn server. You also need to add an `Alias` to serve static files directly.

Add the following blocks to your configuration file, inside the `<VirtualHost>` section:

```apache
    # --- Inventory Management App ---
    Alias /inventory/static/ /path/to/your/project/inventory_management/staticfiles/
    <Directory /path/to/your/project/inventory_management/staticfiles>
        Require all granted
    </Directory>

    <Location /inventory/>
        RequestHeader set X-Forwarded-Prefix "/inventory/"
        ProxyPass http://127.0.0.1:8002/
        ProxyPassReverse http://127.0.0.1:8002/
    </Location>
```

**Note:** Make sure to replace `/path/to/your/project/` with the actual path to your project directory.

### b. Create a Gunicorn Systemd Service

Next, create a systemd service file to manage the Gunicorn process. This will ensure that your application starts automatically on server boot and is restarted if it crashes.

Create a new file at `/etc/systemd/system/inventory.service`:

```ini
[Unit]
Description=Gunicorn instance for Inventory Management
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project/inventory_management
ExecStart=/path/to/your/project/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8002 inventory_management.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

**Note:**
- Replace `/path/to/your/project/` with the actual path to your project directory.
- Make sure the `User` and `Group` are appropriate for your server setup. `www-data` is a common choice.
- `venv/bin/gunicorn` assumes you have a virtual environment named `venv` in your project directory.

### c. Enable and Start the Service

Finally, enable and start the new Gunicorn service:

```bash
sudo systemctl daemon-reload
sudo systemctl start inventory.service
sudo systemctl enable inventory.service
```

Your application should now be accessible at `https://your-domain.com/inventory/`.

## 4. MySQL Database Configuration

This section covers how to set up a MySQL database for the application.

### a. Check for Existing MySQL Server

First, check if a MySQL server is already running on your system:

```bash
sudo systemctl status mysql
```

If the service is active, you can proceed to the next step. If not, you will need to install it:

```bash
sudo apt update
sudo apt install mysql-server
```

### b. Create a New Database and User

Next, log in to the MySQL shell as the root user:

```bash
sudo mysql
```

From the MySQL shell, run the following commands to create a new database and a dedicated user for your application. Replace `'your_database_name'`, `'your_username'`, and `'your_password'` with your desired values.

```sql
CREATE DATABASE your_database_name;
CREATE USER 'your_username'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON your_database_name.* TO 'your_username'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### c. Configure Django Settings

Now, update your Django `settings.py` file to connect to the new database. You'll need to install the `mysqlclient` package first. **Make sure your virtual environment is active.**

```bash
pip install mysqlclient
```

Then, in your `settings.py` file, find the `DATABASES` section and update it as follows:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## 5. Final Django Commands

Before the application is fully deployed, you need to run a couple of final management commands.

### a. Collect Static Files

This command gathers all static files (CSS, JavaScript, images) from your apps and puts them in a single directory (`staticfiles`) so Apache can serve them.

```bash
sudo /path/to/your/project/venv/bin/python manage.py collectstatic
```

### b. Run Migrations

Finally, run the initial database migrations to set up the necessary tables.

```bash
sudo /path/to/your/project/venv/bin/python manage.py migrate
```

## 6. Production Considerations

### a. Caching

The `LocMemCache` is suitable for development but not for production, as each Gunicorn worker will have its own separate cache. For a production environment, you should use a shared cache backend like Redis or Memcached.

### b. Scheduled Tasks (Cron Job)

To automatically send expiry notifications, you need to set up a cron job to run the `send_expiry_notifications` management command periodically.

Open the crontab for editing:

```bash
crontab -e
```

Add the following line to run the command every day at midnight:

```
0 0 * * * /path/to/your/project/venv/bin/python /path/to/your/project/inventory_management/manage.py send_expiry_notifications
```
