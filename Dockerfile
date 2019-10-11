FROM ubuntu:18.04

RUN apt update
RUN apt install -y curl gnupg
RUN apt install -y openssh-server

RUN service ssh start
RUN mkdir ~/.ssh


# install metasploit
RUN curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && \
  chmod 755 msfinstall && \
  ./msfinstall
