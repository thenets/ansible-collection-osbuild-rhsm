# thenets.osbuild : tests

Instructions for running the tests.


## Local

TODO

## Container

TODO

## Vagrant (VM)

Tested on:

- Fedora 38

```bash
# Install Fedora's virtualization packages
sudo dnf install -y @virtualization
sudo dnf install -y libvirt-devel

# Install vagrant and the libvirt plugin
sudo dnf install -y vagrant
vagrant plugin install vagrant-libvirt
```
