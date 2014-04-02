#/usr/bin/python
#
# dhcpd-flask.py
#
# A simple web service that will do dhcpd management tasks.
#
# Host reservations must be in its own dedicated file, one host entry per line, 
# and in a specific format.
# Example : host digaxfr.us { hardware ethernet 12:34:56:78:9A:BC; fixed-address 192.168.101.2; }
#
# Usage (client):
#   curl - http://dhcpd-flask-host:5000/HostReservations -d "host=deploy-01&macAddr=52:54:d5:d8:df:31&ipAddr=192.168.101.50 -X POST"
#
# Work-in-progress/for fun.

from flask import Flask
from flask.ext.restful import reqparse, abort, Api, Resource
import json
import pprint
import re
import sys

""" Global Variables """
dhcpdPath       = "/etc/dhcp/"
dhcpdResFile    = "dhcpd-reservations.conf"

""" Global Objects """
app         = Flask(__name__)
api         = Api(app)
app.debug   = False

""" Check for a user defined config. """
def checkUserDefinedConfig(**kwargs):
    out = dhcpdResFile
    try:
        out = kwargs['dhcpdResFile']
    except KeyError:
        sys.exc_clear()
    return out

""" Read the host reservations conf file, and return a dictionary. """
def readHostReservationsConfig(**kwargs):
    dhcpdResFile = checkUserDefinedConfig(**kwargs)
    hosts = {}
    with open(dhcpdPath + dhcpdResFile, 'r') as file:
        for entry in file:
            if entry == "\n":
                continue
            entry = re.sub('\n', '', entry)
            entryList = entry.split(' ')
            hosts[entryList[1]] = {
                'hardware' : {
                    'ethernet' : re.sub(';', '', entryList[5]),
                 },
                'fixed-address' : re.sub(';', '', entryList[7]),
            }
    return hosts

""" Checks to see if either the host, MAC, or IP exists currently. """
def checkExists(**kwargs):
    status  = {}

    """ First, let's see if there's a custom config file specified. """
    try: 
        hosts = readHostReservationsConfig(kwargs['dhcpdResFile'])
    except KeyError:
        hosts = readHostReservationsConfig()

    """ Do test cases for each item. """
    for k, v in kwargs.iteritems():
        if k == "host":
            for i in hosts.keys():
                if v == i:
                    status['host'] = v
        if k == "macAddr":
            for i in hosts.keys():
                if v == hosts[i]['hardware']['ethernet']:
                    status['macAddr'] = v
        if k == "ipAddr":
            for i in hosts.keys():
                if v == hosts[i]['fixed-address']:
                    status['ipAddr'] = v
    return status

""" Web services portion. """
class HostReservations(Resource):
    
    """ Retrieve the host reservations from the specified host reservation 
    file. """
    def get(self):
        return json.dumps(readHostReservationsConfig())
    
    """ Add a new entry """
    def post(self):
        """ Parser """
        parser = reqparse.RequestParser()
        parser.add_argument('host',         type=str, required=True)
        parser.add_argument('macAddr',      type=str, required=True)
        parser.add_argument('ipAddr',       type=str, required=True)
        parser.add_argument('dhcpdResFile', type=str)
        
        args            = parser.parse_args()
        host            = args['host']
        macAddr         = args['macAddr']
        ipAddr          = args['ipAddr']
        confFile        = args['dhcpdResFile']
        
        if confFile is None:
            confFile = dhcpdResFile

        """ Check that there are no duplicates. A response back with a JSON 
        object means a duplicate was found."""
        check = checkExists(host=host, macAddr=macAddr, ipAddr=ipAddr)
        if len(check) > 0:
            return json.dumps(check)

        """ All is good. Dump the new host entry. """
        hostEntry = "host " + host + " { hardware ethernet " + macAddr + \
        "; fixed-address " + ipAddr + "; }\n"
        
        try:
            with open(dhcpdPath + confFile, 'a') as file:
                file.write(hostEntry)
                return json.dumps(["Info", "Host entry added."])
        except IOError:
            return json.dumps(["Error","Invalid host reservation file."])

api.add_resource(HostReservations, '/HostReservations')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
