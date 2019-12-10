# To run:
# docker run -it penlite

FROM kalilinux/kali-linux-docker

# Install the noVNC server and Xfce desktop
RUN apt-get update \
    && apt-get upgrade -y \
    && DEBIAN_FRONTEND=noninteractive \
        apt-get install -y \
            # Packages for the VNC server (or for installing the VNC server)
            git \
            tigervnc-standalone-server \
            tigervnc-xorg-extension \
            openssl \
            procps \
            python3 \
            python3-pip \
            # Packages for the Xfce desktop
            xfce4 \
            xfce4-goodies \
    && git clone \
        --depth 1 \
        https://github.com/novnc/noVNC.git \
        /tmp/noVNC \
#
# Only keep the files we need from the git repository
    && mkdir -p /usr/share/noVNC \
    && mv /tmp/noVNC/vnc.html /usr/share/noVNC \
    && mv /tmp/noVNC/app      /usr/share/noVNC \
    && mv /tmp/noVNC/core     /usr/share/noVNC \
    && mv /tmp/noVNC/utils    /usr/share/noVNC \
    && mv /tmp/noVNC/vendor   /usr/share/noVNC \
    && git clone \
        --depth 1 \
        https://github.com/novnc/websockify.git \
        /usr/share/noVNC/utils/websockify \
    && pip3 install --no-cache-dir numpy \
# Cleanup
    && apt-get remove -y \
        git \
        python3-pip \
    && apt-get autoremove -y \
    && apt-get purge \
    && rm -rf /tmp/* \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s \
        $(which python3) \
        $(dirname $(which python3))/python

# Add pentesting packages
RUN apt-get update \
    && apt-get install -y \
        --no-install-recommends \
        curl \
        gnupg \
        openvpn \
        openssh-server \
        metasploit-framework \
    && rm -rf /var/lib/apt/lists/*

# Create config directories (both user and global) for SSH and VNC
RUN mkdir ~/.ssh \
    && mkdir ~/.vnc

# Configure VNC
ENV TERM=xterm-256color

ADD vnc/ /etc/vnc
ADD x11/ /etc/x11
ADD bin/ /usr/bin
COPY vnc.conf /etc/vnc.conf

# Change x-terminal-emulator to /usr/bin/xfce4-terminal.wrapper so that we
# avoid "input/output error" when attempting to open a terminal in a VNC
# session.
RUN bash -c "update-alternatives --config x-terminal-emulator <<< 2"

# Enable OpenVPN when the OPENVPN flag is set to one (by default it is set
# to zero.)
ARG OPENVPN=0
RUN if [ ${OPENVPN} = 1 ]; then \
        mkdir -p /dev/net \
        && mknod /dev/net/tun c 10 200 \
        && chmod 0666 /dev/net/tun; \
    fi

###
### Install tools
###
RUN mkdir /root/Desktop
COPY Terminal.desktop /root/Desktop

COPY start.sh /
CMD [ "/start.sh" ]
