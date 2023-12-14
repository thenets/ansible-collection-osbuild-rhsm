#!/bin/bash

# exit 0

set -ex

# Create random ~/.ssh/id_rsa if not exists
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
fi

# Enable repo and copy redhat.repo
# subscription-manager repos --enable=ansible-automation-platform-2.4-for-rhel-9-x86_64-rpms

set -ex
ansible-playbook -e=@secrets/vars.yml -vv \
    thenets.osbuild.host_setup
ansible-playbook -e=@secrets/vars.yml -vv \
    thenets.osbuild.build_azure
