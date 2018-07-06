#!/usr/bin/env python
# Adapted from Mark Mandel's implementation
# https://github.com/ansible/ansible/blob/devel/plugins/inventory/vagrant.py
import argparse
import json
import paramiko
import subprocess
import sys
from collections import defaultdict


def parse_args():
    parser = argparse.ArgumentParser(description="Vagrant inventory script")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true')
    group.add_argument('--host')
    return parser.parse_args()


def list_running_hosts():
    cmd = "vagrant status --machine-readable"
    status = subprocess.check_output(cmd.split()).rstrip()
    hosts = []
    for line in status.split('\n'):
        (_, host, key, value) = line.split(',', 3)
        if key == 'state' and value == 'running':
            hosts.append(host)

            # inventory_groups = host.split('.')
            #
            # # Remove precending "agave" token as that's not a group
            # if inventory_groups[0] == 'agave':
            #     del inventory_groups[0]
            #
            # if len(inventory_groups) == 1 :
            #     hosts.setdefault(host, []).append(host)
            # elif len(inventory_groups) == 2 :
            #
            #     hosts.setdefault(inventory_groups[0], {}).setdefault(inventory_groups[1], []).append(host)
            # elif len(inventory_groups) == 3 :
            #     hosts.setdefault(inventory_groups[0], {}).setdefault(inventory_groups[1], {}).setdefault(inventory_groups[2], []).append(host)

    return hosts


def get_host_details(host):
    cmd = "vagrant ssh-config {}".format(host)
    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    config = paramiko.SSHConfig()
    config.parse(p.stdout)
    c = config.lookup(host)
    return {'ansible_ssh_host': c['hostname'],
            'ansible_ssh_port': c['port'],
            'ansible_ssh_user': c['user'],
            'ansible_ssh_private_key_file': c['identityfile'][0]}


def main():
    args = parse_args()
    if args.list:
        hosts = list_running_hosts()
        json.dump({'agave': hosts}, sys.stdout)
    else:
        details = get_host_details(args.host)
        json.dump(details, sys.stdout)

if __name__ == '__main__':
    main()