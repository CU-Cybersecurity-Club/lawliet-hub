#!/bin/sh

LHS="UI.initSetting('path', 'websockify');"
RHS_1="let loc = String(window.location.pathname)"
RHS_2="UI.initSetting('path', loc.substring(1, loc.lastIndexOf('\\/')) + '\\/websockify')"
sed -i "s/$LHS/$RHS_1; $RHS_2;/g" $1/app/ui.js
