#!/usr/bin/env python3

# Copyright: (c) 2023, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
import os
import configparser
import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

DOCUMENTATION = r'''
---
module: repo_info
author: Scott Harwell <sharwell@redhat.com>
short_description: Retrieves information about repositories managed by subscription manager.
version_added: "1.1.1"
description: Retrieves name, URL, and GPG key information about repositories managed by subscription manager.  This data can be used to populate TOML files for other tools, like Image Builder, to interact with these repositories.
options:
    _terms:
        description: path(s) of files to read
        required: True
    path:
        description:
            - Path to a different repository file
        type: string
'''

EXAMPLES = r'''
# Pass in a repository
- name: Get Ansible repository info
  lab.composer.repo_info:
    name: ansible-automation-platform-2.4-for-rhel-9-x86_64-rpms

# Pass in a repository from a non-standard repo path
- name: Get Ansible repository info
  lab.composer.repo_info:
    name: ansible-automation-platform-2.4-for-rhel-9-x86_64-rpms
    path: /etc/yum.repos.d/epel.repo

# fail the module
- name: Test failure of the module
  lab.composer.repo_info:
    name: invalid_repo_name
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
repo:
    description: The repository requested.
    type: str
    returned: always
    sample: 'ansible-automation-platform-2.4-for-rhel-9-x86_64-rpms'
repo_file_path:
    description: The path of the repo file examined.
    type: str
    returned: always
    sample: '/etc/yum.repos.d/redhat.repo'
repo_response:
    description: The details of the repository returned.
    type: obj
    returned: always
    sample: {
            "baseurl": "https://cdn.redhat.com/content/dist/layered/rhel9/x86_64/ansible-automation-platform/2.4/os",
            "gpgkey": "The following public key can be used to verify RPM packages built and\nsigned by Red Hat, Inc.  This key is used for packages in Red Hat\nproducts shipped after November 2009, and for all updates to those\nproducts.\n\nQuestions about this key should be sent to security@redhat.com.\n\npub  4096R/FD431D51 2009-10-22 Red Hat, Inc. (release key 2) <security@redhat.com>\n\n-----BEGIN PGP PUBLIC KEY BLOCK-----\n\nmQINBErgSTsBEACh2A4b0O9t+vzC9VrVtL1AKvUWi9OPCjkvR7Xd8DtJxeeMZ5eF\n0HtzIG58qDRybwUe89FZprB1ffuUKzdE+HcL3FbNWSSOXVjZIersdXyH3NvnLLLF\n0DNRB2ix3bXG9Rh/RXpFsNxDp2CEMdUvbYCzE79K1EnUTVh1L0Of023FtPSZXX0c\nu7Pb5DI5lX5YeoXO6RoodrIGYJsVBQWnrWw4xNTconUfNPk0EGZtEnzvH2zyPoJh\nXGF+Ncu9XwbalnYde10OCvSWAZ5zTCpoLMTvQjWpbCdWXJzCm6G+/hx9upke546H\n5IjtYm4dTIVTnc3wvDiODgBKRzOl9rEOCIgOuGtDxRxcQkjrC+xvg5Vkqn7vBUyW\n9pHedOU+PoF3DGOM+dqv+eNKBvh9YF9ugFAQBkcG7viZgvGEMGGUpzNgN7XnS1gj\n/DPo9mZESOYnKceve2tIC87p2hqjrxOHuI7fkZYeNIcAoa83rBltFXaBDYhWAKS1\nPcXS1/7JzP0ky7d0L6Xbu/If5kqWQpKwUInXtySRkuraVfuK3Bpa+X1XecWi24JY\nHVtlNX025xx1ewVzGNCTlWn1skQN2OOoQTV4C8/qFpTW6DTWYurd4+fE0OJFJZQF\nbuhfXYwmRlVOgN5i77NTIJZJQfYFj38c/Iv5vZBPokO6mffrOTv3MHWVgQARAQAB\ntDNSZWQgSGF0LCBJbmMuIChyZWxlYXNlIGtleSAyKSA8c2VjdXJpdHlAcmVkaGF0\nLmNvbT6JAjYEEwECACAFAkrgSTsCGwMGCwkIBwMCBBUCCAMEFgIDAQIeAQIXgAAK\nCRAZni+R/UMdUWzpD/9s5SFR/ZF3yjY5VLUFLMXIKUztNN3oc45fyLdTI3+UClKC\n2tEruzYjqNHhqAEXa2sN1fMrsuKec61Ll2NfvJjkLKDvgVIh7kM7aslNYVOP6BTf\nC/JJ7/ufz3UZmyViH/WDl+AYdgk3JqCIO5w5ryrC9IyBzYv2m0HqYbWfphY3uHw5\nun3ndLJcu8+BGP5F+ONQEGl+DRH58Il9Jp3HwbRa7dvkPgEhfFR+1hI+Btta2C7E\n0/2NKzCxZw7Lx3PBRcU92YKyaEihfy/aQKZCAuyfKiMvsmzs+4poIX7I9NQCJpyE\nIGfINoZ7VxqHwRn/d5mw2MZTJjbzSf+Um9YJyA0iEEyD6qjriWQRbuxpQXmlAJbh\n8okZ4gbVFv1F8MzK+4R8VvWJ0XxgtikSo72fHjwha7MAjqFnOq6eo6fEC/75g3NL\nGht5VdpGuHk0vbdENHMC8wS99e5qXGNDued3hlTavDMlEAHl34q2H9nakTGRF5Ki\nJUfNh3DVRGhg8cMIti21njiRh7gyFI2OccATY7bBSr79JhuNwelHuxLrCFpY7V25\nOFktl15jZJaMxuQBqYdBgSay2G0U6D1+7VsWufpzd/Abx1/c3oi9ZaJvW22kAggq\ndzdA27UUYjWvx42w9menJwh/0jeQcTecIUd0d0rFcw/c1pvgMMl/Q73yzKgKYw==\n=zbHE\n-----END PGP PUBLIC KEY BLOCK-----\n-----BEGIN PGP PUBLIC KEY BLOCK-----\n\nmQINBGIpIp4BEAC/o5e1WzLIsS6/JOQCs4XYATYTcf6B6ALzcP05G0W3uRpUQSrL\nFRKNrU8ZCelm/B+XSh2ljJNeklp2WLxYENDOsftDXGoyLr2hEkI5OyK267IHhFNJ\ng+BN+T5Cjh4ZiiWij6o9F7x2ZpxISE9M4iI80rwSv1KOnGSw5j2zD2EwoMjTVyVE\n/t3s5XJxnDclB7ZqL+cgjv0mWUY/4+b/OoRTkhq7b8QILuZp75Y64pkrndgakm1T\n8mAGXV02mEzpNj9DyAJdUqa11PIhMJMxxHOGHJ8CcHZ2NJL2e7yJf4orTj+cMhP5\nLzJcVlaXnQYu8Zkqa0V6J1Qdj8ZXL72QsmyicRYXAtK9Jm5pvBHuYU2m6Ja7dBEB\nVkhe7lTKhAjkZC5ErPmANNS9kPdtXCOpwN1lOnmD2m04hks3kpH9OTX7RkTFUSws\neARAfRID6RLfi59B9lmAbekecnsMIFMx7qR7ZKyQb3GOuZwNYOaYFevuxusSwCHv\n4FtLDIhk+Fge+EbPdEva+VLJeMOb02gC4V/cX/oFoPkxM1A5LHjkuAM+aFLAiIRd\nNp/tAPWk1k6yc+FqkcDqOttbP4ciiXb9JPtmzTCbJD8lgH0rGp8ufyMXC9x7/dqX\nTjsiGzyvlMnrkKB4GL4DqRFl8LAR02A3846DD8CAcaxoXggL2bJCU2rgUQARAQAB\ntDVSZWQgSGF0LCBJbmMuIChhdXhpbGlhcnkga2V5IDMpIDxzZWN1cml0eUByZWRo\nYXQuY29tPokCUgQTAQgAPBYhBH5GJCWMQGU11W1vE1BU5KRaY0CzBQJiKSKeAhsD\nBQsJCAcCAyICAQYVCgkICwIEFgIDAQIeBwIXgAAKCRBQVOSkWmNAsyBfEACuTN/X\nYR+QyzeRw0pXcTvMqzNE4DKKr97hSQEwZH1/v1PEPs5O3psuVUm2iam7bqYwG+ry\nEskAgMHi8AJmY0lioQD5/LTSLTrM8UyQnU3g17DHau1NHIFTGyaW4a7xviU4C2+k\nc6X0u1CPHI1U4Q8prpNcfLsldaNYlsVZtUtYSHKPAUcswXWliW7QYjZ5tMSbu8jR\nOMOc3mZuf0fcVFNu8+XSpN7qLhRNcPv+FCNmk/wkaQfH4Pv+jVsOgHqkV3aLqJeN\nkNUnpyEKYkNqo7mNfNVWOcl+Z1KKKwSkIi3vg8maC7rODsy6IX+Y96M93sqYDQom\naaWue2gvw6thEoH4SaCrCL78mj2YFpeg1Oew4QwVcBnt68KOPfL9YyoOicNs4Vuu\nfb/vjU2ONPZAeepIKA8QxCETiryCcP43daqThvIgdbUIiWne3gae6eSj0EuUPoYe\nH5g2Lw0qdwbHIOxqp2kvN96Ii7s1DK3VyhMt/GSPCxRnDRJ8oQKJ2W/I1IT5VtiU\nzMjjq5JcYzRPzHDxfVzT9CLeU/0XQ+2OOUAiZKZ0dzSyyVn8xbpviT7iadvjlQX3\nCINaPB+d2Kxa6uFWh+ZYOLLAgZ9B8NKutUHpXN66YSfe79xFBSFWKkJ8cSIMk13/\nIfs7ApKlKCCRDpwoDqx/sjIaj1cpOfLHYjnefg==\n=UZd/\n-----END PGP PUBLIC KEY BLOCK-----\n",
            "name": "Red Hat Ansible Automation Platform 2.4 for RHEL 9 x86_64 (RPMs)"
        }
'''

def get_config_parser(path: str) -> configparser.ConfigParser:
    abs_path = os.path.abspath(path)
    config = configparser.ConfigParser()
    config.read(abs_path)

    return config

def get_repo_data(config: configparser.ConfigParser, repo: str) -> {}:
    output_repo = {}
    output_repo["baseurl"] = config.get(repo, "baseurl")
    output_repo["name"] = config.get(repo, "name")

    _tmp_gpgkey_file = config.get(repo, "gpgkey")
    gpgkey_file = _tmp_gpgkey_file.replace("file://", "")
    with open(gpgkey_file, 'r', encoding='UTF8') as f:
        gpgkey = f.read()
    output_repo["gpgkey"] = gpgkey

    return output_repo

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        repo=dict(type='str', required=True),
        path=dict(type='str', required=False, default='/etc/yum.repos.d/redhat.repo')
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)

    config = get_config_parser(module.params['path'])

    result['repo'] = module.params['repo']
    result['repo_file_path'] = module.params['path']
    result['repo_response'] = get_repo_data(config, module.params['repo'])
    result['changed'] = False

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
