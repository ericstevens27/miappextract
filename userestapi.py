import json
import urllib.request

s = {}

urlData = "http://api.openweathermap.org/data/2.5/forecast?id=6094817&APPID=b34cbd68201ad49a3396353ebb8b2105"
try:
    webURL = urllib.request.urlopen(urlData)
    data = webURL.read()
    encoding = webURL.info().get_content_charset('utf-8')
    s = json.loads(data.decode(encoding))
except urllib.request.URLError as e:
    print(e.reason)

print(s)
temp = s['list'][0]['main']['temp']
print("Temperature is {} K".format(temp))
