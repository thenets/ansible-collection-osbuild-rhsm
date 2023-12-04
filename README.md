# lab.osbuild A Collection to build cloud VM images

## Introduction

The Ansible on Clouds team has a need to publish VM images that contain the Ansible installer packaged with a standard RHEL base image.  This repository implements examples for creating that image.

This project is a Proof of Concept to include the Ansible Automation Platform repos into the main `osbuild` available repos with the respective RHSM (Red Hat Subscription Manager).

Almost everything was based on the official [osbuild docs][os_build_docs].

## Variables

The following variables may be set to alter the behavior of this collection.

## Instructions

### Prepare your accounts

The build process will require that you have an active Red Hat account that may be used to login to `registry.redhat.io`.  You will also need an Azure storage account with the account name, bucket name, and access key.

### Prepare the local machine

Install this collection onto your local machine so that calling the fully-qualified playbook name will work.

```bash
ansible-galaxy collection install git+https://github.com/scottharwell/osbuild-with-rhsm-repos.git
```

Next, create a vars file to configure variables that can be saved to the filesystem (not secrets).

```yaml
---
local_public_key_file: ~/.ssh/id_rsa.pub
azure_storage_account_name: myimageaccount
azure_storage_container_name: images
composer_build_image_version: "1.0.0"
```

Create an inventory file for your RHEL builder machine.

```ini
[builder]
builder.host.your.domain
```

### Prepare Build Machine

This collection assumes that you have a RHEL 9 machine that will act as a build host for the images.  The playbooks included in this collection will allow you to prepare that RHEL host and then deploy a VM image.  The following must be performed on the build machine prior to using this playbook.

* The OS must be RHEL 9
* RHEL should have subscription manager registered and attached

### Setup Host

You should now be ready to run the playbook that will prepare your RHEL host with Image Builder and dependencies.  No extra vars should be required for this playbook.

```bash
ansible-playbook -i inventory lab.osbuild.host_setup
```

### Build Image

Next, run the build image playbook.  This playbook currently builds an Azure VM image based on the files in the `roles/composer/templates/pipeline.j2` file.  Changes to that template will result in changes to the build image.

You will also need to prepare environment variables that will pass the secrets required for this operation.  Those are identified in the command below.

```bash
ansible-playbook -i inventory lab.osbuild.host_setup \
--extra-vars "@vars.yml"
--extra-vars "azure_storage_account_access_key=$AZURE_STORAGE_ACCESS_KEY" \
--extra-vars "podman_username=$PODMAN_USERNAME" \
--extra-vars "podman_password=$PODMAN_PASSWORD" \
```

[os_build_docs]: https://www.osbuild.org/guides/introduction.html
