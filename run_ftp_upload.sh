#!/bin/bash
echo "run_ftp_upload.sh triggered at $(date)" >> /app/logs/cron_debug.txt

# Print the environment variables to see if they're empty or set
echo "FTP_HOST=$FTP_HOST" >> /app/logs/cron_debug.txt
echo "FTP_PORT=$FTP_PORT" >> /app/logs/cron_debug.txt
echo "FTP_USER=$FTP_USER" >> /app/logs/cron_debug.txt
echo "FTP_PASS=$FTP_PASS" >> /app/logs/cron_debug.txt

export FTP_HOST="${FTP_HOST}"
export FTP_PORT="${FTP_PORT}"
export FTP_USER="${FTP_USER}"
export FTP_PASS="${FTP_PASS}"

cd /app
/usr/local/bin/python ftp_upload.py /app/logs/fpl_prices.html fpl_prices.html
