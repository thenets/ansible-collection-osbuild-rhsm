# lab.osbuild A Collection to build cloud VM images

## Introduction

The Ansible on Clouds team has a need to publish VM images that contain the Ansible installer packaged with a standard RHEL base image.  This repository implements examples for creating that image.

This project is a Proof of Concept to include the Ansible Automation Platform repos into the main `osbuild` available repos with the respective RHSM (Red Hat Subscription Manager).

Almost everything was based on the official [osbuild docs][os_build_docs].

## Instructions

### Prepare your accounts

The build process will require that you have an active Red Hat account that may be used to login to `registry.redhat.io`.  For pushing images to Azure, you will also need an Azure storage account with the account name, bucket name, and access key.  For pushing images to AWS, you will need to create an access key and set the IAM variables as parameters in later steps.

#### AWS Setup

If you are pushing images to AWS, this collection has a playbook that will setup the proper resources to deploy images.  View the defaults in the role's defaults file.  Change any variable either inline when running the playbook, or in a vars file like in the example below.

```bash
ansible-navigator run lab.osbuild.aws_setup \
-i env/inventory \
--pae false \
--mode stdout \
--lf /dev/null \
--ee false \
--extra-vars "@env/vars.yml"
```

### Prepare the local machine

Install this collection onto your local machine so that calling the fully-qualified playbook name will work.

```bash
ansible-galaxy collection install git+https://github.com/scottharwell/osbuild-with-rhsm-repos.git
```

Next, create a vars file to configure variables that can be saved to the filesystem (not secrets).

```yaml
---
local_public_key_file: ~/.ssh/id_rsa.pub
composer_build_image_version: "1.0.0"
composer_azure_storage_account_name: myimageaccount
composer_azure_storage_container_name: images
composer_aws_bucket: aoc-vm-image-imports
aws_s3_import_bucket: aoc-vm-image-imports
aws_s3_export_bucket: aoc-vm-image-exports
composer_clouds:
  - name: azure
    image_format: vhd
  - name: aws
    image_format: ami
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
ansible-navigator run lab.osbuild.host_setup \
-i env/inventory \
--pae false \
--mode stdout \
--lf /dev/null \
--ee false \
--extra-vars "@env/vars.yml" \
-vv
```

### Build Image

The `build_images` playbook currently builds images based on the files in the `roles/composer/templates/` folder.  Each cloud has a slightly different setup.  Changes to that templates will result in changes to the build image.

The `composer_clouds` variable will determine which images are built.  Remove or comment a particular cloud from the list if you do not want to deploy to that cloud.  If a cloud is removed, the variables specific to that cloud are not required; for instance, if you remove AWS from the list, then `composer_aws_access_key_id` and so on are not required.

```yaml
composer_clouds:
  - name: azure
    image_format: vhd
  - name: aws
    image_format: ami
```

You will also need to prepare environment variables that will pass the secrets required for this operation.  Those are identified in the command below.

```bash
ansible-navigator run lab.osbuild.build_images \
-i env/inventory \
--pae false \
--mode stdout \
--lf /dev/null \
--ee false \
--extra-vars "podman_username=$RED_HAT_ACCOUNT" \
--extra-vars "podman_password='$RED_HAT_PASSWORD'" \
--extra-vars "composer_azure_storage_account_name='$AZURE_STORAGE_ACCOUNT_NAME'" \
--extra-vars "composer_azure_storage_account_access_key='$AZURE_STORAGE_ACCOUNT_KEY'" \
--extra-vars "composer_aws_access_key_id='$AWS_ACCESS_KEY_ID'" \
--extra-vars "composer_aws_secret_access_key='$AWS_SECRET_ACCESS_KEY'" \
--extra-vars "composer_aws_session_token='$AWS_SESSION_TOKEN'" \
--extra-vars "composer_aws_bucket='$AWS_SESSION_TOKEN'" \
--extra-vars "@env/vars.yml" \
-vv
```

[os_build_docs]: https://www.osbuild.org/guides/introduction.html
