# Local machine test targets
# ===================================
## local test: run all tests
local-play-all: play-host-setup

## local test: thenets.osbuild.host_setup
local-play-host-setup: export ANSIBLE_CONFIG=./env-local/ansible.cfg
local-play-host-setup:
	ansible-playbook -vv thenets.osbuild.host_setup

## local test: thenets.osbuild.build_azure
local-play-build-azure: export ANSIBLE_CONFIG=./env-local/ansible.cfg
local-play-build-azure:
	ansible-playbook -vv thenets.osbuild.build_azure

## local test: thenets.osbuild.build_gcp
local-play-build-gcp: export ANSIBLE_CONFIG=./env-local/ansible.cfg
local-play-build-gcp:
	ansible-playbook -vv thenets.osbuild.build_gcp

## local debug
local-play-build-debug: export ANSIBLE_CONFIG=./env-local/ansible.cfg
local-play-build-debug:
	ansible-playbook -vv thenets.osbuild.debug


# In-container tests
# ===================================
CONTAINER_SECRETS_DIR=/tmp/osbuild-container-secrets/
IMAGE_TAG=docker.io/redhat/ubi9:latest
RHSM_USERNAME ?= ""
RHSM_PASSWORD ?= ""
_CONTAINER_RUNTIME = sudo podman
## in-container tests, requires RHSM_USERNAME and RHSM_PASSWORD
container-test: _check-rhsm-credentials _check-container-inventory-file _container_image_build _container_secrets_vars
	$(_CONTAINER_RUNTIME) exec -it osbuild-test \
		/bin/bash

_container_image_build:
	mkdir -p /tmp/selinux-osbuild
	$(_CONTAINER_RUNTIME) volume create --ignore osbuild-cache
	$(_CONTAINER_RUNTIME) volume create --ignore osbuild-var-tmp
	$(_CONTAINER_RUNTIME) run -it -d --rm --replace --name osbuild-test \
		-v osbuild-cache:/cache:rw,z \
		-v osbuild-var-tmp:/var/tmp:rw,z \
		--security-opt label=type:unconfined_t \
		--privileged \
		\
		--workdir /root/.ansible/collections/ansible_collections/thenets/osbuild/tests/env-container \
		-v $$(cd ./../ && pwd):/root/.ansible/collections/ansible_collections/thenets/osbuild:rw,z \
		-v /tmp/rhsm-credentials:/opt/rhsm-credentials:ro,z \
		$(IMAGE_TAG) /sbin/init
#docker build -t $(IMAGE_TAG) -f ./env-container/Containerfile ./env-container

_container_secrets_vars:
# - RHSM credentials
	@echo '#!/bin/bash' > /tmp/rhsm-credentials
	@echo export RHSM_USERNAME=$(RHSM_USERNAME) >> /tmp/rhsm-credentials
	@echo export RHSM_PASSWORD=$(RHSM_PASSWORD) >> /tmp/rhsm-credentials
# - Azure credentials
	@echo '#!/bin/bash' > /tmp/rhsm-credentials
	@echo export RHSM_USERNAME=$(RHSM_USERNAME) >> /tmp/rhsm-credentials
	@echo export RHSM_PASSWORD=$(RHSM_PASSWORD) >> /tmp/rhsm-credentials

_check-rhsm-credentials:
ifeq ($(RHSM_USERNAME),"")
	$(error RHSM_USERNAME is not set)
endif
ifeq ($(RHSM_PASSWORD),"")
	$(error RHSM_PASSWORD is not set)
endif

_check-container-inventory-file:
ifeq (,$(wildcard ./env-local/inventory))
	$(error ./env-local/inventory file does not exist)
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
