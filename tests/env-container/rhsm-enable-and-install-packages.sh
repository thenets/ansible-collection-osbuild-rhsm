#!/bin/bash

function _rhsm_register() {
    function _disable_container_check() {
        # HACK: Remove in_container() check from rhsm config
        # https://access.redhat.com/discussions/5889431
        sed -i 's/\(def in_container():\)/\1\n    return False/g' /usr/lib64/python*/*-packages/rhsm/config.py
    }

    function _load_creds() {
        # If /opt/rhsm-credentials not found
        if [ ! -f /opt/rhsm-credentials ]; then
            echo "[ERROR] /opt/rhsm-credentials not found"
            exit 1
        fi

        source /opt/rhsm-credentials
        # If RHSM_USERNAME and RHSM_PASSWORD not set
        if [ -z "$RHSM_USERNAME" ] || [ -z "$RHSM_PASSWORD" ]; then
            echo "RHSM_USERNAME and RHSM_PASSWORD must be set in /opt/rhsm-credentials"
            exit 1
        fi
    }

    set +x
    _load_creds
    _disable_container_check
    # Register to RHSM
    subscription-manager register --auto-attach \
        --username $RHSM_USERNAME \
        --password $RHSM_PASSWORD
    set -x
}

function _rhsm_unregister() {
    # Unregister from RHSM
    subscription-manager unregister
}


# Main
# =========
set -xe -o pipefail

_rhsm_register

# Ignore errors, because the unregister must always be executed
set +e

# Enable repo
subscription-manager repos --enable=ansible-automation-platform-2.4-for-rhel-9-x86_64-rpms

# Install packages
dnf install -y ansible-core

set -e

_rhsm_unregister

set +x
echo DONE
