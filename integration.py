import http.client
import json
import socket
import ssl
from datetime import datetime
from base64 import b64encode
from hashlib import sha1
import hmac
import binascii



def getRouteId(routeName):
    request ='/v3/routes?route_name='+routeName
    request = request + ('&' if ('?' in request) else '?')
    raw = request+'devid={0}'.format(devId)
    key_bytes= bytes(key , 'latin-1')
    raw_bytes = bytes(raw, 'latin-1')
    hashed = hmac.new(key_bytes, raw_bytes, sha1)
    
    signature = hashed.hexdigest()
    connection.request('GET',raw+'&signature={1}'.format(devId, signature))
    response = connection.getresponse()
    routeInfo = json.loads(response.read().decode('utf-8'))
    routeId = routeInfo['routes'][0]['route_id']
    return routeId


def get_disruptions(route_id):
    #"""
    #Create some code to extract information about route disruptions from the Public Transport 
    #Victoria API. 

    #"""
    ##connection to PTV API
    #connection = http.client.HTTPConnection("timetableapi.ptv.vic.gov.au", timeout=2)
    ##http://timetableapi.ptv.vic.gov.au/v3/disruptions/route/0?devid=3000325&signature
    #devId = 3000325
    #key = 'afbed855-d243-43a1-a55a-de4631d52f38'
   

    request ='/v3/disruptions/route/'+str(route_id)
    request = request + ('&' if ('?' in request) else '?')
    raw = request+'devid={0}'.format(devId)
    key_bytes= bytes(key , 'latin-1')
    raw_bytes = bytes(raw, 'latin-1')
    hashed = hmac.new(key_bytes, raw_bytes, sha1)
    
    signature = hashed.hexdigest()
    #print('pre: ',raw+'&signature={1}'.format(devId, signature))
    connection.request('GET',raw+'&signature={1}'.format(devId, signature))
    
    #calculate the number of members returned by the first request
    response = connection.getresponse()
    membersInfo = json.loads(response.read().decode('utf-8'))
    #print('result = ',membersInfo)
    res1 = membersInfo['disruptions']['metro_train'][0]['disruption_status']
    #print(membersInfo['disruptions']['metro_train'][0]['disruption_type'])
    #print(membersInfo['disruptions']['metro_train'][0]['disruption_status'])
    res2=membersInfo['disruptions']['metro_train'][0]['title']
    return [res1,res2]

 





##!/usr/bin/env python
#get_disruptions(2)

    #"metro_tram": [],
    #"metro_bus": [],
    #"regional_train": [],
    #"regional_coach": [],
    #"regional_bus": []

   #raw = '/v2/healthcheck'+'devid={0}'.format(devId)
   #hashed = hmac.new(key, raw, sha1)
   #signature = hashed.hexdigest()
   #return 'http://tst.timetableapi.ptv.vic.gov.au'+raw+'&signature={1}'.format(devId, signature)



import argparse
import json
import os
import sys

import requests 

def sendMessageInSlack(text,channel):
	payload={'username': 'disruption', 'text':text, 'channel': '@'+channel}

	try:
		res = requests.post('https://hooks.slack.com/services/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', data=json.dumps(payload))
	except Exception as e:
		sys.stderr.write('An error occurred when trying to deliver the message:\n  {0}'.format(e.message))
		return 2

	if not res.ok:
		sys.stderr.write('Could not deliver the message. Slack says:\n  {0}'.format(res.text))
	return 0






connection = http.client.HTTPConnection("timetableapi.ptv.vic.gov.au", timeout=2)
devId = XXXXX
key = 'XXXXX' 

customerRoute=[('Barry','Belgrave'),('Harry','Hurstbridge'),('Wally','Werribee'),('Freddy','Frankston')]
customerRoute=[('jules','Belgrave'),('anna','Werribee')]


def main():
    route = []
    for i in range(0,len(customerRoute)):
        if customerRoute[i][1] not in route:
           route.append(customerRoute[i][1])

    for i in route:
        routeId=getRouteId(i)
        res=get_disruptions(routeId)
        for j in range(0,len(customerRoute)):
             if(res[0]=='Current')and(customerRoute[j][1]==i): sendMessageInSlack(res[1],customerRoute[j][0])
    
    return res

main()
connection.close()