# Local machine test targets
# ===================================
## local test: run all tests
local-play-all: play-host-setup play-build-azure

## local test: thenets.osbuild.host_setup
local-play-host-setup: export ANSIBLE_CONFIG=./env-local/ansible.cfg
local-play-host-setup:
	ansible-playbook -vv thenets.osbuild.host_setup

## local test: thenets.osbuild.build_azure
local-play-build-azure: export ANSIBLE_CONFIG=./env-local/ansible.cfg
local-play-build-azure:
	ansible-playbook -vv thenets.osbuild.build_azure


# In-container tests
# ===================================
IMAGE_TAG=thenets/osbuild-rhsm:test
RHSM_USERNAME ?= ""
RHSM_PASSWORD ?= ""
## in-container tests, requires RHSM_USERNAME and RHSM_PASSWORD
container-test: _check-rhsm-credentials _check-inventory-file
	@echo '#!/bin/bash' > /tmp/rhsm-credentials
	@echo export RHSM_USERNAME=$(RHSM_USERNAME) >> /tmp/rhsm-credentials
	@echo export RHSM_PASSWORD=$(RHSM_PASSWORD) >> /tmp/rhsm-credentials
	podman build \
		--ignorefile ./env-container/.containerignore \
		-t $(IMAGE_TAG) \
		-v /tmp/rhsm-credentials:/opt/rhsm-credentials:ro,z \
		-f container/Containerfile \
		--no-cache \
		./../
	rm -f /tmp/rhsm-credentials

## REMOVE_ME DEBUG
container-test-shell:
	podman run -it --rm $(IMAGE_TAG) /bin/bash

_check-rhsm-credentials:
ifeq ($(RHSM_USERNAME),"")
	$(error RHSM_USERNAME is not set)
endif
ifeq ($(RHSM_PASSWORD),"")
	$(error RHSM_PASSWORD is not set)
endif

_check-inventory-file:
ifeq (,$(wildcard ./inventory))
	$(error ./inventory file does not exist)
endif


# HELP related targets
#
# This generates one-line help for each target.
# Also usefull to improve documentation and manutenability.
# --------------------------------------
HELP_FILTER=.PHONY
T_COLOR_RED=\033[0;31m
T_COLOR_GREEN=\033[0;32m
T_RESET=\033[0m

# Display help targets
help:
	@printf "Available targets:\n"
	@make -s help-generate | grep -vE "\w($(HELP_FILTER))"

# Generate help output from MAKEFILE_LIST
help-generate:
	@awk '/^[-a-zA-Z_0-9%:\\\.\/]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = $$1; \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			gsub("\\\\", "", helpCommand); \
			gsub(":+$$", "", helpCommand); \
			printf "  \x1b[32;01m%-35s\x1b[0m %s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST) | sort -u
	@printf "\n"
