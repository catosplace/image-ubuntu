#!/bin/bash
set -x

PACKER_VERSION=1.5.5

curl -OL \
  "https://releases.hashicorp.com/packer/${PACKER_VERSION}/packer_${PACKER_VERSION}_linux_amd64.zip"
unzip ./packer_${PACKER_VERSION}_linux_amd64.zip
chmod +x packer
mv packer /usr/local/packer
