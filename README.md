# Inventory Management Application

This is a Django-based web application for managing inventory.

## Deployment on Render.com

There is a known issue where Render may try to run an incorrect start command based on your repository name. If your deployment fails with an error like `ModuleNotFoundError: No module named 'datea'`, you need to manually set the Start Command in the Render dashboard.

### Instructions to Fix Deployment:

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
