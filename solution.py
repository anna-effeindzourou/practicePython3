import http.client
import json
import socket
import ssl
from datetime import datetime
from base64 import b64encode

def sort_list(l):
    """Takes a list and returns a sorted version"""
    l.sort()
    return l

def rgb_to_hex(red, green, blue):
    """
    Convert red, green, blue values into a HTML hex representation

    The short syntax should (#fff) be used where possible.
    """
    #check if the values are between 0 and 255 for each color
    for var in [red,green, blue]:
        if (var < 0 or var > 255): raise NameError('Each value has to be ranging from 0 to 255')
	  
    #convert rgb colors to hexadecimal 
    hexa = '%02x%02x%02x' % (red,green,blue)
    
    #identify if the use shorthand hexadecimal colors is required
    hexaList = list(hexa)
    if(hexaList[0] == hexaList[1]) and (hexaList[2] == hexaList[3]) and (hexaList[4] == hexaList[5]):
	     hexa = str(hexaList[0]) + str(hexaList[2]) + str(hexaList[4])

    return '#'+hexa
 
def get_github_members(org_name):
    """
    Get the number of (public) members belonging to the specified Github
    organisation
    """
    #connection to GitHub API
    connection = http.client.HTTPSConnection("api.github.com", timeout=2)
    
    #header for basic authentication to access GitHub API
    #userAndPass = b64encode(b"userID:password").decode("ascii")    
    #headerRequest = {"User-Agent":"CommonCodeApp", 'Authorization' : 'Basic %s' %  userAndPass }
    
    #header with no authentication, works if number of request is under the unauthenticated rate limit 
    headerRequest = {"User-Agent":"CommonCodeApp"}
    
    params = {}
    connection.request('GET', '/orgs/'+org_name+'/members', params, headerRequest)
    
    #calculate the number of members returned by the first request
    response = connection.getresponse()
    membersInfo = json.loads(response.read().decode('utf-8'))
    nbOfMembers = len(membersInfo)
    
    #verify if more requests are required
    headerResponse = response.msg
    if 'link' in  headerResponse:
        links = headerResponse['link']
        #print('number of page: ',links[links.rfind('>; rel="last"') - 1])
        nbOfPages = int(links[links.rfind('>; rel="last"') - 1])
    else:
        connection.close()
        return nbOfMembers
    
    #make more requests to obtain the rest of the members
    for i in range(2,nbOfPages + 1):
       #other alternative would be to directly get the adress of the next page that can be found in links
       connection.request('GET', '/orgs/'+org_name+'/members?page='+str(i), params,headerRequest)
       response = connection.getresponse()
       nbOfMembers += len(json.loads(response.read().decode('utf-8'))) 
    
    connection.close()
    return nbOfMembers
 
def get_ssl_expiry(domain):
    """
    Takes a domain and returns a date that represents when the SSL certificate
    will expire.
    """
    context = ssl.create_default_context()
    connection = context.wrap_socket(sock = socket.socket(socket.AF_INET),server_hostname = domain)
    
    #connection to the domain using port 443
    connection.connect((domain, 443))
    
    #get the SSL certificate   
    certificateInfo = connection.getpeercert()
    connection.close()
    
    #parse the string from the certificate into a date
    dateFormat = r'%b %d %H:%M:%S %Y %Z'
    return datetime.strptime(certificateInfo['notAfter'], dateFormat).date()
