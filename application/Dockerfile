# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install necessary modules
RUN pip install Flask pymysql cryptography

# Install Nginx and nano
RUN apt-get update && apt-get install -y nginx nano && rm -rf /var/lib/apt/lists/*

# Copy files to root of container
COPY app.py /opt/app.py
COPY templates /opt/templates/
COPY static /opt/static/

# Expose the necessary port(s)
EXPOSE 8000
EXPOSE 5000
EXPOSE 3306

WORKDIR /opt/

# Start Nginx and your Flask application
CMD service nginx start && python /opt/app.py