# Use Python 3.9 slim as base
FROM python:3.9-slim

# Set timezone to Asia/Bangkok
ENV TZ=Asia/Bangkok

RUN apt-get update && apt-get install -y tzdata cron && rm -rf /var/lib/apt/lists/*

# Symlink to the correct timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set the working directory
WORKDIR /app

# Copy the Main Python script into the container
COPY price_change_detector.py .

# Copy the FTP Python script into the container
COPY ftp_upload.py .

# Install Python dependencies
RUN pip install requests

# Copy the crontab file into the container
COPY crontab /etc/cron.d/fpl-cron

# Give execution rights on the cron job file
RUN chmod 0644 /etc/cron.d/fpl-cron

# Create directories for snapshots and logs
RUN mkdir -p /app/fpl_snapshots && mkdir -p /app/logs

# Run cron in the foreground
CMD ["cron", "-f"]
