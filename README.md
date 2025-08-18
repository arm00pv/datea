# Inventory Management Application

This is a simple, collective inventory management application built with Django. It is designed for a single organization to track items and their expiration dates.

## Features

*   **Item List:** View all items in the inventory.
*   **Add Item:** Add new items to the inventory.
*   **Expiring Soon:** View a list of items that are expiring within the next 7 days.
*   **Subscribe:** Subscribe to receive email reminders for expiring items.

## Local Development

To run the application locally, follow these steps:

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run database migrations:**
    ```bash
    python inventory_management/manage.py migrate
    ```
3.  **Start the development server:**
    ```bash
    python inventory_management/manage.py runserver
    ```
    The application will be available at `http://localhost:8000`.

## Email Reminders

The application can send email reminders for items that are about to expire. To send the reminders, run the following management command:

```bash
python inventory_management/manage.py send_reminders
```

In a production environment, you should schedule this command to run periodically (e.g., once a day using a cron job).

## Deployment on Render.com

For a successful deployment on Render, you need to configure the start command and set up the necessary environment variables.

### Environment Variables

For the application to work correctly in a production environment, you need to set the following environment variables in your Render dashboard:

1.  **`DATABASE_URL`**: This should be set to the connection URL of your PostgreSQL database. For example: `postgresql://user:password@host:port/database`
2.  **`SECRET_KEY`**: This should be a long, random string for Django's cryptographic signing. You can generate one using an online tool or Python's `secrets` module.
3.  **`DEBUG`**: Set this to `False` in production.

To set these variables:

1.  Go to your **Render Dashboard** and click on your `inventory-management` web service.
2.  On the left-hand side menu, click on the **"Environment"** tab.
3.  Click **"Add Environment Variable"** and add the key-value pairs for `DATABASE_URL`, `SECRET_KEY`, and `DEBUG`.
4.  Render will automatically trigger a new deployment with the updated environment.

### Start Command

There is a known issue where Render may try to run an incorrect start command based on your repository name. If your deployment fails with an error like `ModuleNotFoundError: No module named 'datea'`, you need to manually set the Start Command in the Render dashboard.

#### Instructions to Fix Deployment:

1.  Go to your **Render Dashboard** and click on your `inventory-management` web service.
2.  On the left-hand side menu, click on the **"Settings"** tab.
3.  Scroll down to the **"Start Command"** field.
4.  Replace whatever is in that field with this exact command:
    ```
    gunicorn inventory_management.inventory_management.wsgi:application
    ```
5.  Scroll to the bottom of the page and click **"Save Changes"**.
6.  This will trigger a new deployment. You can monitor its progress in the "Events" tab.

This should resolve the deployment error.
