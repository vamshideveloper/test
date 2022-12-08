#!/bin/env python3
"""Utility to automate secret engines in the vault"""
__author__ = "vamshi"
import os
import json
import sys

from common.logs import info, debug, error
from vault_common.vault import get_authorized_vault_client


def main():
    """Authentication to vault"""

    client = get_authorized_vault_client()
    define_kv(client)

    client.logout()
    sys.exit(0)


def get_kv_list(client):
    """Get list of secret engines from vault.
        :param client: Used for performing requests.
        :type client: hvac.Client
    """
    secrets_engines = client.sys.list_mounted_secrets_engines()
    all_secret_eng = []
    for key, value in secrets_engines['data'].items():
        if value['type'] == 'kv':
            key_strip_space = key.strip()
            key_strip_slash = key_strip_space.strip('/')
            all_secret_eng.append(key_strip_slash.strip('/'))
    info(f'Secret engines in Vault {all_secret_eng}')
    return all_secret_eng


def define_kv(client):
    """Enable kv secret engines added to github.
        :param client: Used for performing requests.
        :type client: hvac.Client
    """
    info('************ Starting Kv engine check *************')
    all_secret_eng = get_kv_list(client)
    path = "kv/"
    files_in_git = []
    engines_in_github = []
    for dir_name, subdir_list, file_list in os.walk(path):
        for files in file_list:
            if '.json' in files:
                files_in_git.append(os.path.join(dir_name, files))
    for file_git in files_in_git:
        with open(file_git, 'r') as j:
            req = json.load(j)
            name = req['name']
            engines_in_github.append(req['name'])
            version = req['version']
            if name in all_secret_eng:
                info(f'secret engine exists with name: {name}')
            else:
                info(f'Secret engine: {name} do not exists in vault')
                if version == '1':
                    info(f'Enabling secret {name} version:1')
                    client.sys.enable_secrets_engine('kv', path=name)
                if version == '2':
                    info(f'Enabling secret {name} version:2')
                    options = {
                        'version': 2
                    }
                    client.sys.enable_secrets_engine('kv', path=name, options=options)
    info(f'Secret engines in Github {engines_in_github}')


if __name__ == '__main__':
    main()
