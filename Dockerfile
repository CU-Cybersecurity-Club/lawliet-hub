# To run:
# docker run -it penlite

FROM kalilinux/kali-linux-docker

RUN apt-get update \
    && apt-get install -y \
        curl \
        gnupg

# Delay installation of OpenSSH server for now -- won't be
# needed unless users are directly SSH'ing into the container,
# which we don't know is the case yet.
#RUN apt install -y openssh-server \
#    && mkdir ~/.ssh

###
### Install tools
###

# Metasploit
RUN apt-get install -y metasploit-framework

COPY start.sh /
ENTRYPOINT [ "/start.sh" ]
