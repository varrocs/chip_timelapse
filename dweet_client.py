
import urllib2
import json


UNIQUE_NAME="varrocs-chip-timelapse"
DWEET_URL="https://dweet.io/dweet/for/{name}"


def send_status_message(messageDict):
    url =  DWEET_URL.format(name=UNIQUE_NAME)
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, json.dumps(messageDict))