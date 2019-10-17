# To run:
# docker run -it penlite

FROM kalilinux/kali-linux-docker

RUN apt-get update \
    && apt-get install -y \
        curl \
        gnupg

RUN apt install -y openssh-server \
    && mkdir ~/.ssh

###
### Install tools
###

# Metasploit
RUN apt-get install -y metasploit-framework

COPY start.sh /
# ENTRYPOINT [ "/start.sh", "&&", "/bin/bash", "-c" ]
