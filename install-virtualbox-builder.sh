#!/bin/bash
set -x

echo "Running install-virtualbox-builder.sh"

VIRTUALBOX_VERSION=6.1

# Install Virtualbox
echo \
	"deb http://download.virtualbox.org/virtualbox/debian $(lsb_release -cs) \
contrib" >> /etc/apt/sources.list
wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | \
	sudo apt-key add -
wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | \
	sudo apt-key add - 
DEBIAN_FRONTEND=noninteractive apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -qq git unzip curl \
 	dkms build-essential \
 	"linux-headers-$(uname -r)" x11-common x11-xserver-utils \
	libxtst6 libxinerama1 psmisc

sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
	virtualbox-${VIRTUALBOX_VERSION}

# Install VirtualBox extension pack
vbox=$(VBoxManage --version)
vboxversion=${vbox%r*}
vboxrevision=${vbox#*r}
wget \
	https://download.virtualbox.org/virtualbox/${vboxversion}/Oracle_VM_VirtualBox_Extension_Pack-${vboxversion}-${vboxrevision}.vbox-extpack
yes | VBoxManage extpack install \
	Oracle_VM_VirtualBox_Extension_Pack-${vboxversion}-${vboxrevision}.vbox-extpack
rm \
	Oracle_VM_VirtualBox_Extension_Pack-${vboxversion}-${vboxrevision}.vbox-extpack
