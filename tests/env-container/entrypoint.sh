#!/bin/bash

# If $@ is found, run it and bypass the rest of the script
if [ $# -gt 0 ]; then
    exec "$@"
    exit 0
fi

# Helpers
# =========================
# Copied from https://github.com/thenets/rinted-container/blob/main/container/entrypoint.sh
if ! type tput >/dev/null 2>&1; then
    tput() {
        return 0
    }
fi
log_info() {
    local CYAN=$(tput setaf 6)
    local NC=$(tput sgr0)
    echo "${CYAN}[INFO   ]${NC} $*" 1>&2
}
log_warning() {
    local YELLOW=$(tput setaf 3)
    local NC=$(tput sgr0)
    echo "${YELLOW}[WARNING]${NC} $*" 1>&2
}
log_error() {
    local RED=$(tput setaf 1)
    local NC=$(tput sgr0)
    echo "${RED}[ERROR  ]${NC} $*" 1>&2
}
log_success() {
    local GREEN=$(tput setaf 2)
    local NC=$(tput sgr0)
    echo "${GREEN}[SUCCESS]${NC} $*" 1>&2
}
log_title() {
    local GREEN=$(tput setaf 2)
    local BOLD=$(tput bold)
    local NC=$(tput sgr0)
    echo 1>&2
    echo "${GREEN}${BOLD}---- $* ----${NC}" 1>&2
}
h_run() {
    local ORANGE=$(tput setaf 3)
    local NC=$(tput sgr0)
    echo "${ORANGE}\$${NC} $*" 1>&2
    eval "$*"
}

# Test script
# =========================
# Create an `osbuild` compose build using a RHSM repo.

function install_main_packages() {
    log_title "Installing dnf dependencies"
    h_run "dnf install -y ncurses python3-pip jq openssh"

    log_title "Installing Ansible and Ansible Collections"
    h_run "pip3 install ansible"
    h_run "ansible-galaxy collection install community.general"
    h_run "ansible-galaxy collection install containers.podman"
}

function _rhsm_register() {
    function _disable_container_check() {
        # HACK: Remove in_container() check from rhsm config
        # https://access.redhat.com/discussions/5889431
        log_info "HACK: Disabling in_container() check from rhsm config"
        set -x
        sed -i 's/\(def in_container():\)/\1\n    return False/g' /usr/lib64/python*/*-packages/rhsm/config.py
        set +x
    }

    function _load_creds() {
        # Protect potentially creds leak
        set +x

        # If /opt/rhsm-credentials not found
        if [ ! -f /opt/rhsm-credentials ]; then
            log_error "/opt/rhsm-credentials not found"
            exit 1
        fi

        source /opt/rhsm-credentials
        # If RHSM_USERNAME and RHSM_PASSWORD not set
        if [ -z "$RHSM_USERNAME" ] || [ -z "$RHSM_PASSWORD" ]; then
            log_error "RHSM_USERNAME and RHSM_PASSWORD must be set in /opt/rhsm-credentials"
            exit 1
        fi
    }

    _load_creds
    _disable_container_check

    log_info "Registering to RHSM"
    subscription-manager register --auto-attach --username $RHSM_USERNAME --password $RHSM_PASSWORD
}

function _rhsm_unregister() {
    # TODO: remove this
    return 0

    log_info "Unregister from RHSM"
    subscription-manager unregister
}

function start_systemd_services() {
    set -e
    function _start_systemd_services_sigterm() {
        log_info "Caught SIGTERM signal, shutting down systemd"
        PID_SYSTEMD=$(pgrep systemd)
        if [ -z "$PID_SYSTEMD" ]; then
            log_error "Systemd not found"
            exit 1
        fi
        h_run "kill -TERM $PID_SYSTEMD"
    }
    trap _start_systemd_services_sigterm SIGTERM

    log_title "Setup systemd"
    log_info "Install osbuild packages"
    h_run "dnf install -y osbuild-composer composer-cli"

    log_info "Creating systemd config files"
    h_run "cp ./units/* /etc/systemd/system/"

    log_info "Enabling systemd services"
    h_run "systemctl daemon-reload"
    h_run "systemctl enable --now \
        osbuild-composer.socket \
        osbuild-composer-proxy.socket \
        osbuild-composer-journal.service \
        osbuild-composer-loopback.service"
}

# Main
# =========
function main() {
    set +x -e -o pipefail

    log_title "Starting testing script"

    install_main_packages

    # Perform operations that depends on RHSM
    # if something fails, unregister from RHSM
    function _step_rhsm() {
        function _step_rhsm_error() {
            # This function is called when an error occurs
            # during operations that depends on RHSM
            set +e
            log_error "Something went wrong during operations that depends on RHSM"
            _rhsm_unregister
            set -e
            log_error "Exit with error"
            exit 1
        }
        trap _step_rhsm_error ERR

        _rhsm_register

        start_systemd_services

        ./test-runner.sh

        _rhsm_unregister
    }

    # Run _step_rhsm and trap errors
    _step_rhsm

    log_success "Tests completed successfully"
}

main
