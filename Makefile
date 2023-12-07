all: setup-host build

build:
	ansible-playbook -i inventory playbook-build-azure.yml -vv

setup-host:
	ansible-playbook -i inventory playbook-setup-host.yml -vv


IMAGE_TAG=thenets/osbuild-rhsm:test
RHSM_USERNAME ?= ""
RHSM_PASSWORD ?= ""
test: _check-rhsm-credentials _check-inventory-file
	@echo '#!/bin/bash' > /tmp/rhsm-credentials
	@echo export RHSM_USERNAME=$(RHSM_USERNAME) >> /tmp/rhsm-credentials
	@echo export RHSM_PASSWORD=$(RHSM_PASSWORD) >> /tmp/rhsm-credentials
	podman build \
		-t $(IMAGE_TAG) \
		-v /tmp/rhsm-credentials:/opt/rhsm-credentials:ro,z \
		-f tests/Containerfile \
		--no-cache \
		.
	rm -f /tmp/rhsm-credentials

test-shell:
	podman run -it --rm $(IMAGE_TAG) /bin/bash

_check-rhsm-credentials:
ifeq ($(RHSM_USERNAME),"")
	$(error RHSM_USERNAME is not set)
endif
ifeq ($(RHSM_PASSWORD),"")
	$(error RHSM_PASSWORD is not set)
endif

_check-inventory-file:
ifeq (,$(wildcard ./tests/inventory))
	$(error ./tests/inventory file does not exist)
endif


debug:
	ansible-playbook -i tests/inventory tests/playbook-debug.yml -vvvv
