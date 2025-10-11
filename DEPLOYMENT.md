# Gunicorn Service File Fix

The `ModuleNotFoundError` is caused by an incorrect Python path for the Gunicorn service. Please **replace the entire content** of your `/etc/systemd/system/gunicorn-datea.service` file with the following configuration.

This version sets the `WorkingDirectory` to your project's root and uses the full Python path to your WSGI application, which is the standard and correct way to configure it.

```bash
sudo nano /etc/systemd/system/gunicorn-datea.service
```

**Corrected Gunicorn Service File:**
```ini
[Unit]
Description=gunicorn daemon for datea app
After=network.target

[Service]
User=zixen
Group=www-data
# The WorkingDirectory should be the root of the project, where the .env file is.
WorkingDirectory=/var/www/webhost/datea
EnvironmentFile=/var/www/webhost/datea/.env
ExecStart=/var/www/webhost/datea/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind 127.0.0.1:8000 \
          inventory_management.inventory_management.wsgi:application

[Install]
WantedBy=multi-user.target
```

**After updating the file, you must run these two commands to apply the changes:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn-datea
```

This will fix the error and get your application running. After you've confirmed it's working, I will proceed with the other features and optimizations we discussed. I am very sorry for the repeated errors and I thank you for your patience.