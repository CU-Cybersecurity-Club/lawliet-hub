#!/bin/bash

# Start postgres, and initialize database for use
# with metasploit.
echo "Starting Postgres..."
service postgresql start > /dev/null
echo "Initializing database..."
msfdb init > /dev/null 2>&1

#mkdir -p /dev/net
#mknod /dev/net/tun c 10 200
#chmod 0666 /dev/net/tun