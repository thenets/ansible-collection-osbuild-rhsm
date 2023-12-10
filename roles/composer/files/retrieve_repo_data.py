#!/usr/bin/env python3

import sys
import os
import configparser
import json

def get_hostname():
    return os.popen('hostname').read().strip()

def get_repo_data():
    repo_file = '/etc/yum.repos.d/redhat.repo'
    repo_section_name = "ansible-automation-platform-2.4-for-rhel-9-x86_64-rpms"
    try:
        config = configparser.ConfigParser()
        config.read(repo_file)
        output_repo = {}
        output_repo["baseurl"] = config.get(repo_section_name, "baseurl")
        output_repo["name"] = config.get(repo_section_name, "name")
    except:
        print("ERROR: Could not read Red Hat repo data")
        sys.exit(1)

    try:
        _tmp_gpgkey_file = config.get(repo_section_name, "gpgkey")
        gpgkey_file = _tmp_gpgkey_file.replace("file://", "")
        with open(gpgkey_file, 'r') as f:
            gpgkey = f.read()
        output_repo["gpgkey"] = gpgkey
    except:
        print("ERROR: Could not read GPG key file")
        sys.exit(1)

    return output_repo

# Get arguments
composer_aap_version = sys.argv[1]
composer_rhel_version = sys.argv[2]

allowed_composer_aap_versions = ["2.4"]
allowed_composer_rhel_versions = ["9"]

if composer_aap_version not in allowed_composer_aap_versions:
    print("ERROR: AAP version not supported")
    sys.exit(1)

if composer_rhel_version not in allowed_composer_rhel_versions:
    print("ERROR: RHEL version not supported")
    sys.exit(1)

# Output
output = {}
output['hostname'] = get_hostname()
output['repo'] = get_repo_data()

print(json.dumps(output))
