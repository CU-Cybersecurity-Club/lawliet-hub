#!/bin/sh

###################################################################################
# 1. Force the path to websockify to be relative rather than absolute. This
#    allows us to evade some issues when trying to proxy to the NoVNC server.
###################################################################################
LHS="UI.initSetting('path', 'websockify');"
RHS_1="let loc = String(window.location.pathname)"
RHS_2="UI.initSetting('path', loc.substring(1, loc.lastIndexOf('\\/')) + '\\/websockify')"
sed -i "s/$LHS/$RHS_1; $RHS_2;/g" $1/app/ui.js

###################################################################################
# 2. Make the desktop resize to fit the screen by default.
###################################################################################
LHS="UI.initSetting('resize', '[a-zA-Z0-9]*');"
RHS="UI.initSetting('resize', 'remote');"
sed -i "s/$LHS/$RHS/g" $1/app/ui.js

