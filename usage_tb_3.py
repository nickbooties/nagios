#!/usr/bin/python
#usage.py
#Nick Booth 2FEB2014
#nicbooth@gmail.com
import urllib2, re, cookielib

username = ""
password = ""
limits = {'warning': 75,'critical': 90}

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

#toolbox works in 3 requests just to login now. bit of a pita right?
#first one is a post request to https://toolbox3.iinet.net.au/login with our login details
#from this we recieve the 'payload' variable to post to the next request
url_a = "https://toolbox3.iinet.net.au/login"
params = ({"username": username, "password": password, "action:LoginVintageToolbox":"","ReturnUrl":"/"})

req = urllib2.Request(url_a,urllib.urlencode(params))
response = opener.open(req)
response_text = response.read().split("\n")
payload = ""

for line in response_text:
        if "authPayload" in line:
                payload = re.search("(?<= \").+(?=\",)",line).group(0)


params = ({"payload": payload})
url_b = "https://toolbox.iinet.net.au/cgi-bin/tb3api.cgi"
req = urllib2.Request(url_b,urllib.urlencode(params))
response = opener.open(req)
response_text = response.read().split("\n")

# sessionid is actually sent back as a cookie so lets use that instead
#sessionid = ""
#for line in response_text:
#        if "sessionId" in line:
#                sessionid = re.search("(?<=ionId\":\").+(?=\")",line).group(0)
#print sessionid

#this returns us our session cookie which we use to fetch our usage
#url_c = "https://toolbox.iinet.net.au/cgi-bin/new/volume_usage_xml.cgi?r=0454778509199954"
url_c = "https://toolbox.iinet.net.au"
req = urllib2.Request(url_c)
response = opener.open(req)
response_text = response.read().split("\n")

quota = ""
usage = ""

for line in response_text:
        if "usage_text" in line:
                line = re.sub('\,', '', line)
                usage = float(re.search("(?<=text\">).+(?=MB )",line).group(0))
                quota = float(re.search("(?<=of ).+(?=MB)",line).group(0))


percent_used = int((usage/quota) * 100)

if percent_used >= 0:
    if percent_used < limits['warning']:
        print "OK -", str(percent_used)+"% used."
        exit(0)
    # 75 - 90
    elif percent_used < limits['critical']:
        print "WARNING -",str(percent_used)+"% used."
        exit(1)
    #90+
    elif percent_used >= limits['critical']:
        print "CRITICAL -",str(percent_used)+"% used."
        exit(2)
    else:
        print "UNKNOWN - unable to determine use: ",percent_used
        exit(3)
else:
        print "UNKNOWN - unable to determine use: ",percent_used
        exit(3)
