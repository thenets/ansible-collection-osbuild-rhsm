# osbuild + Red Hat Subscription Manager repos

By default, when you create a new image using `osbuild`, you don't have access to other Red Hat repositories beyond the main ones.

This project is a Proof of Concept to include the Ansible Automation Platform repos into the main `osbuild` available repos with the respective RHSM (Red Hat Subscription Manager).


Almost everything was based on the official `osbuild` docs: https://www.osbuild.org/guides/introduction.html

