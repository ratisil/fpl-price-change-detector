# Use Python 3.9 slim as base
FROM python:3.9-slim

# Set timezone to Asia/Bangkok
ENV TZ=Asia/Bangkok
RUN apt-get update && apt-get install -y tzdata cron && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the Python script into the container
COPY price_change_detector.py .

# Install Python dependencies
RUN pip install requests

# Copy the crontab file into the container
COPY crontab /etc/cron.d/fpl-cron

# Give execution rights on the cron job file and install it
RUN chmod 0644 /etc/cron.d/fpl-cron && crontab /etc/cron.d/fpl-cron

# Create a directory for snapshots (this will be mounted as a volume)
RUN mkdir /app/fpl_snapshots

# Run cron in the foreground
CMD ["cron", "-f"]
