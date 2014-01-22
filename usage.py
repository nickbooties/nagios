import httplib, urllib, urllib2, re, time
from HTMLParser import HTMLParser

username = "username"
password = "password"

# define usage alert borders
limits = {'warning': 75,'critical': 90}

curmonth = time.strftime("%Y%m%d")

params = ({"username": username, "password": password, "action": "login","period": curmonth})
usage_url = "https://toolbox.iinet.net.au/cgi-bin/new/volumeusage.cgi"

opener = urllib2.build_opener()
req = urllib2.Request(usage_url,urllib.urlencode(params))
response = opener.open(req)

class MyParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.inUsage = False
        self.recording = False
        self.data = []

    def handle_starttag(self, tag, attributes):
        if self.inUsage:
            for name, value in attributes:
                if name == 'class' and value == 'usage_text':
                    self.recording = True
                else:
                    return
        else:
            for name, value in attributes:
                if name == 'id' and value == 'usage_div':
                    self.inUsage = True
                else:
                    return

    def handle_endtag(self, tag):
        if tag == 'td' and self.inUsage:
           self.inUsage = False
        
        if tag == 'div' and self.recording:
            self.recording = False
  
    def handle_data(self, data):
        if self.recording and self.inUsage:
            self.data.append(data)

parser = MyParser()
parser.feed(response.read())

raw = parser.data

if len(raw) > 1:
    usage_array = raw[0].replace("MB","").split()
    usage = float(usage_array[0].replace(",",""))
    quota = float(usage_array[3].replace(",",""))

    percent_used = int((usage/quota) * 100)
else:
    percent_used = -1

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
