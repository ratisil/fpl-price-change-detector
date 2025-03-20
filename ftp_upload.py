import logging
import os
import sys
from ftplib import FTP

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

# Output to stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

def ftp_upload(local_filepath, remote_filename):
    logger.info("FTP upload job triggered.")
    logger.info(f"Arguments received: local_file = {local_filepath}, remote_file = {remote_filename}")
    
    ftp_host = os.environ.get("FTP_HOST")
    ftp_port = int(os.environ.get("FTP_PORT"))
    ftp_user = os.environ.get("FTP_USER")
    ftp_pass = os.environ.get("FTP_PASS")

    if not ftp_pass:
        logger.error("FTP_PASS environment variable is not set!")
        return

    try:
        ftp = FTP()
        ftp.connect(ftp_host, ftp_port)
        ftp.login(user=ftp_user, passwd=ftp_pass)
        current_dir = ftp.pwd()
        logger.info(f"Current FTP directory: {current_dir}")
        with open(local_filepath, "rb") as f:
            ftp.storbinary("STOR " + remote_filename, f)
        logger.info(f"Uploaded {local_filepath} to FTP as {remote_filename}.")
        ftp.quit()
    except Exception as e:
        logger.error(f"Failed to upload file to FTP: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python ftp_upload.py <local_file> <remote_file>")
        sys.exit(1)

    local_file = sys.argv[1]
    remote_file = sys.argv[2]
    ftp_upload(local_file, remote_file)

if __name__ == "__main__":
    main()
