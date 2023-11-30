all: setup-host build

build:
	ansible-playbook -i inventory playbook-build-azure.yml -vv

setup-host:
	ansible-playbook -i inventory playbook-setup-host.yml -vv
