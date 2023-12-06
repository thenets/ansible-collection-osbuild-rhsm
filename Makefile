all: setup-host build

build:
	ansible-playbook -i inventory playbook-build-azure.yml -vv

setup-host:
	ansible-playbook -i inventory playbook-setup-host.yml -vv


IMAGE_TAG=thenets/osbuild-rhsm:test
RHSM_USERNAME ?= ""
RHSM_PASSWORD ?= ""
test: _check-rhsm-credentials
	podman build \
		-t $(IMAGE_TAG) \
		-f tests/Containerfile \
		--no-cache \
		.

_check-rhsm-credentials:
ifeq ($(RHSM_USERNAME),"")
	$(error RHSM_USERNAME is not set)
endif
ifeq ($(RHSM_PASSWORD),"")
	$(error RHSM_PASSWORD is not set)
endif
