#!/bin/bash
echo "run_ftp_upload.sh triggered at $(date)" >> /app/logs/cron_debug.txt

# Export the FTP environment variables so that they are available to the script.
export FTP_HOST="${FTP_HOST}"
export FTP_PORT="${FTP_PORT}"
export FTP_USER="${FTP_USER}"
export FTP_PASS="${FTP_PASS}"

cd /app
/usr/local/bin/python ftp_upload.py /app/logs/fpl_prices.html fpl_prices.html
