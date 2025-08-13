# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /code/

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "inventory_management.inventory_management.wsgi:application", "--bind", "0.0.0.0:8000"]
