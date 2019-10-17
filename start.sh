#!/bin/bash

# Start postgres, and initialize database for use
# with metasploit.
echo "Starting Postgres..."
service postgresql start > /dev/null
echo "Initializing database..."
msfdb init > /dev/null 2>&1
