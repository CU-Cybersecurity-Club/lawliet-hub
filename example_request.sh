#!/bin/sh

curl -XPOST localhost:8080/container -H "Content-Type: application/json" --data "@testbody.json"
