#!/usr/bin/env python3

import configparser
import json
import os
import sys


def get_hostname():
    return os.popen("hostname").read().strip()


def get_repo_data(repo_section_name):
    repo_file = "/etc/yum.repos.d/redhat.repo"
    # For containers, search for for /tmp/redhat.repo
    if not os.path.isfile(repo_file):
        repo_file = "/tmp/redhat.repo"

    if not os.path.isfile(repo_file):
        print("ERROR: Could not find Red Hat repo file")
        print(f"ERROR: Not found: {repo_file}")
        sys.exit(1)

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
        with open(gpgkey_file, "r") as f:
            gpgkey = f.read()
        output_repo["gpgkey"] = gpgkey
    except:
        print("ERROR: Could not read GPG key file")
        sys.exit(1)

    return output_repo


# Get arguments
rhsm_repo = sys.argv[1]

if not rhsm_repo:
    print("ERROR: No RHSM repo provided")
    sys.exit(1)

# Output
output = {}
output["hostname"] = get_hostname()
output["repo"] = get_repo_data(rhsm_repo)

print(json.dumps(output))
