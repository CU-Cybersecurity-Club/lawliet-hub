FROM kalilinux/kali-linux-docker

RUN apt-get update \
    && apt-get install -y \
        curl \
        gnupg \
        openvpn \
		openssh-server \
		metasploit-framework \
    && apt-get purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /dev/net && \
    mknod /dev/net/tun c 10 200 && \
    chmod 0666 /dev/net/tun

RUN mkdir ~/.ssh

COPY start.sh /
