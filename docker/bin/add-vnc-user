#!/bin/bash

###
### Simple bash script to create a new user for the VNC
###

if [[ $# < 1 ]] || [[ $# > 2 ]]
then
    cat <<- EOT
add-vnc-user username [vnc-password]

Configure a user to be able to run a desktop session over VNC.
EOT
    exit 1
fi

export VNC_USER=$1
export VNC_USER_HOME=$(eval echo ~$VNC_USER)

echo "Configuring VNC for ${VNC_USER}..."

mkdir ${VNC_USER_HOME}/.vnc

echo "Creating self-signed certificates to encrypt VNC connection..."
openssl req \
    -x509 \
    -newkey rsa:4096 \
    -keyout ${VNC_USER_HOME}/.vnc/vnc.key \
    -out ${VNC_USER_HOME}/.vnc/vnc.cert \
    -days 365 \
    -subj '/CN=${VNC_USER}' \
    -nodes

echo "Setting user password..."
if [ $# = 2 ]
then
    bash -c "vncpasswd -f <<< '$2' > ${VNC_USER_HOME}/.vnc/passwd"
else
    vncpasswd ${VNC_USER_HOME}/.vnc/passwd
fi

# Set appropriate ownership and permissions
chmod 700 ${VNC_USER_HOME}/.vnc \
    && chmod 400 ${VNC_USER_HOME}/.vnc/* \
    && chown -R ${VNC_USER}:${VNC_USER_DEFAULT_GROUP} \
        ${VNC_USER_HOME}/.vnc

echo "Finished"
