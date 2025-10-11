# Gunicorn Service File Fix

The `ModuleNotFoundError` is caused by an incorrect `WorkingDirectory` in your Gunicorn service file. Please **replace the entire content** of your `/etc/systemd/system/gunicorn-datea.service` file with the following configuration.

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
# The WorkingDirectory should be the directory that contains the `manage.py` file.
WorkingDirectory=/var/www/webhost/datea/inventory_management
EnvironmentFile=/var/www/webhost/datea/.env
ExecStart=/var/www/webhost/datea/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind 127.0.0.1:8000 \
          inventory_management.wsgi:application

[Install]
WantedBy=multi-user.target
```

**After updating the file, you must run these two commands to apply the changes:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn-datea
```

This will fix the error and get your application running. After you've confirmed it's working, I will proceed with the other features and optimizations we discussed.