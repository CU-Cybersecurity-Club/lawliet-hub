#!/bin/sh

#curl -XPOST localhost:8080/container -H "Content-Type: application/json" --data "@testbody.json"
curl -XPOST localhost:8080/container -H "Content-Type: application/json" --data "{ \"ssh_public_key\": \"$(cat ~/.ssh/id_rsa.pub)\" }"
