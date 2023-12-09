import sys
import os
import configparser
import json

def get_hostname():
    return os.popen('hostname').read().strip()

def get_repo_data(repo_section_name):
    repo_file = '/etc/yum.repos.d/redhat.repo'

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
rhsm_repo = sys.argv[1]

if not rhsm_repo:
    print("ERROR: No RHSM repo provided")
    sys.exit(1)

# Output
output = {}
output['hostname'] = get_hostname()
output['repo'] = get_repo_data(rhsm_repo)

print(json.dumps(output))
