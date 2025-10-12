# Gunicorn Service File Fix

The `ModuleNotFoundError` is caused by an incorrect Python path for the Gunicorn service. Please **replace the entire content** of your `/etc/systemd/system/gunicorn-datea.service` file with the following configuration.

This version uses the `--chdir` flag to explicitly tell Gunicorn to change into your project's main directory before trying to load the application. This is the most robust and standard way to resolve this kind of import error.

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
WorkingDirectory=/var/www/webhost/datea
EnvironmentFile=/var/www/webhost/datea/.env
ExecStart=/var/www/webhost/datea/venv/bin/gunicorn \
          --workers 3 \
          --bind 127.0.0.1:8000 \
          --chdir /var/www/webhost/datea/inventory_management \
          inventory_management.wsgi:application

[Install]
WantedBy=multi-user.target
```

**After updating the file, you must run these two commands to apply the changes:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn-datea
```

This will fix the error and get your application running. I am very sorry for the repeated errors and I thank you for your patience. After you've confirmed it's working, I will proceed with the other features and optimizations we discussed.