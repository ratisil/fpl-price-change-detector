# env_test.py
import os
import sys

with open("/app/logs/env_vars.txt", "w") as f:
    for k, v in os.environ.items():
        f.write(f"{k}={v}\n")
    f.write(f"Arguments: {sys.argv}\n")  # Log arguments

print("Environment variables logged.") # This will go to stdout (and the cron log, if redirected)