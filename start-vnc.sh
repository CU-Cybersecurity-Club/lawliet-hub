#!/bin/bash

vncserver \
		-geometry 1200x800 \
		-localhost no \
		-X509Key ${HOME}/.vnc/vnc.key \
		-X509Cert ${HOME}/.vnc/vnc.cert \
		-xstartup /etc/vnc/xstartup \
		-baseHttpPort $1 \
		-fg
