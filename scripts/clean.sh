#!/usr/bin/env bash -eux

# Uninstall Ansible and remove PPA.
apt -y remove --purge ansible
apt-add-repository --remove ppa:ansible/ansible

# Apt cleanup
apt -y autoremove --purge
apt -y clean
apt -y autoclean

# Delete unneeded files
rm -f /home/vagrant/*.sh

# Zero out the rest of the free space using dd, then delete the written file.
#dd if=/dev/zero of=zero.small.file bs=1024 count=102400
#dd if=/dev/zero of=zero.file bs=1024
#sync; sleep 60; sync
#rm zero.small.file
#rm zero.file

# Add 'sync' so Packer doesn't quit too early, before the large file is deleted.
sync
