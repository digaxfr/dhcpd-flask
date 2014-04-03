#!/usr/bin/python
#
# dhcpd-flask-client.py
#
# Quick client for dhcpd-flask. Does not do any error handling at the moment.

import argparse
import json
import requests

DHCPD_URL       = "http://192.168.101.2:5000"
DHCPD_HR_URL    = "/HostReservations"

""" Get host reservations """
def getHostReservations(**kwargs):
    req = requests.get(DHCPD_URL + DHCPD_HR_URL)
    data = json.loads(req.json())
    return json.dumps(data, indent=4, sort_keys=True, separators=(',', ':'))

""" Add a host reservation """
def addHostReservation(host, macAddr, ipAddr):
    payload = {
        'host'      : host,
        'macAddr'   : macAddr,
        'ipAddr'    : ipAddr,
    }
    req = requests.post(DHCPD_URL + DHCPD_HR_URL, data=payload)
    response = json.loads(req.json())
    return json.dumps(response, indent=4, separators=(',', ':'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Execute basic DHCPD management.')
    parser.add_argument('--host', type=str, help='Hostname for the entry')
    parser.add_argument('--mac', type=str, help='MAC address for the host entry')
    parser.add_argument('--ip', type=str, help='IP address for the host entry')
    parser.add_argument('--get', action='store_true', help='Get all host reservations')
    parser.add_argument('--add', action='store_true', help='Add a host reservation')
    args = vars(parser.parse_args())

    host    = args['host']
    macAddr = args['mac']
    ipAddr  = args['ip']
    get     = args['get']
    add     = args['add']

    if (get):
        print getHostReservations()
    elif (add):
        print addHostReservation(host=host, macAddr=macAddr, ipAddr=ipAddr)
