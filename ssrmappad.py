import readbase as rb
import argbase as arg
import json
import requests

# define global variables
# options as globals
usagemsg = "This program reads the JSON file that contains the list of applications extracted fromt he Mi app Store " \
           "and then pushes the data to the SSRM"
msg = arg.MSG()


class SSRMApi:
    def __init__(self, user: str, password: str, ssrmpath: str):
        self.user = user
        self.password = password
        self.ssrm = ssrmpath + '/api/v2/web/'
        self.xsrf_token = ''
        self.data = {
            "adName": "Example App add",
            "content": [
                {
                    "title": "Example App",
                    "category": "Demo and Testing",
                    "description": "An app example for documentation",
                    "appStoreUris": [
                        {
                            "code": "thirdParty",
                            "uri": "http://example.com/third-party-us"
                        }
                    ],
                    "buttonText": "Install",
                    "visitedButtonText": "Added",
                    "images": [
                        {
                            "typeName": "BANNER",
                            "imageUri": "/dynamicAssets/f29e3843-f4c0-4fbd-80cd-d31d4c091ccc-Wechat-in-the-world.jpg",
                            "colspan": 1,
                            "rowspan": 1
                        },
                        {
                            "typeName": "SMALL_BANNER",
                            "imageUri": "/dynamicAssets/663d14a8-3fc7-4907-912d-6e6af1e75d7b-Wechat-in-the-world.jpg",
                            "colspan": 1,
                            "rowspan": 1
                        },
                        {
                            "typeName": "ICON",
                            "imageUri": "/dynamicAssets/c6655851-bdd7-473f-a78d-f2dc8a611d09-bunny.jpg",
                            "colspan": 1,
                            "rowspan": 1
                        }
                    ],
                    "language": "en_US"
                },
                {
                    "title": "演示测试",
                    "category": "演示测试",
                    "description": "演示测试",
                    "appStoreUris": [
                        {
                            "code": "thirdParty",
                            "uri": "http://example.com/third-party-cn"
                        }
                    ],
                    "buttonText": "安装",
                    "visitedButtonText": "添加",
                    "images": [
                        {
                            "typeName": "BANNER",
                            "imageUri": "/dynamicAssets/f29e3843-f4c0-4fbd-80cd-d31d4c091ccc-Wechat-in-the-world.jpg",
                            "colspan": 1,
                            "rowspan": 1
                        },
                        {
                            "typeName": "SMALL_BANNER",
                            "imageUri": "/dynamicAssets/663d14a8-3fc7-4907-912d-6e6af1e75d7b-Wechat-in-the-world.jpg",
                            "colspan": 1,
                            "rowspan": 1
                        },
                        {
                            "typeName": "ICON",
                            "imageUri": "/dynamicAssets/42efa74e-d401-4ce9-9040-61e1a9ff069c-bunny.jpg",
                            "colspan": 1,
                            "rowspan": 1
                        }
                    ],
                    "language": "zh_CN"
                }
            ],
            "category": "Documentation",
            "advertiser": "Graphite software",
            "packageName": "com.securespaces.package"
        }

    def gettoken(self):
        actionURL = self.ssrm + "security/login"
        authjson = { "username": self.user, "password": self.password }
        params = json.dumps(authjson).encode('utf8')
        header = {'content-type': 'application/json'}
        msg.DEBUG("\n\tURL: {}\n\tjson: {}\n\tdata: {}\n\tHeaders: {}".format(actionURL, authjson, params, header))
        msg.VERBOSE("Logging in")
        r = requests.post(actionURL, json=authjson, headers=header)
        if r.status_code != 200:
            if r.status_code == 401:
                msg.VERBOSE("Username and password not valid [HTTP Response: {}]".format(r.status_code))
            else:
                msg.VERBOSE("Bad request (invalid JSON) [HTTP Response: {}]".format(r.status_code))
        else:
            msg.VERBOSE("Login successful [HTTP Response: {}]".format(r.status_code))
            self.xsrf_token = r.json()['xsrfToken']

    def getsession(self):
        actionURL = self.ssrm + "security/currentSessionInfo"
        header = {'content-type': 'application/json', 'X-XSRF-TOKEN': self.xsrf_token}
        msg.DEBUG("\n\tURL: {}\n\tHeaders: {}".format(actionURL, header))
        msg.VERBOSE("Getting Session Info")
        r = requests.get(actionURL, headers=header)
        if r.status_code != 200:
            if r.status_code == 401:
                msg.VERBOSE("Unauthorized Request (invalid XSRF-TOKEN) [HTTP Response: {}]".format(r.status_code))
            else:
                msg.VERBOSE("Bad request (invalid JSON) [HTTP Response: {}]".format(r.status_code))
        else:
            msg.VERBOSE("Get Session Info successful [HTTP Response: {}]".format(r.status_code))
        rj = json.loads(r.content.decode('utf-8'))
        msg.DEBUG("User name is {}".format(rj['username']))

    def logoutsession(self):
        actionURL = self.ssrm + "security/logout"
        header = {'content-type': 'application/json', 'X-XSRF-TOKEN': self.xsrf_token}
        msg.DEBUG("\n\tURL: {}\n\tHeaders: {}".format(actionURL, header))
        msg.VERBOSE("Logging Out")
        r = requests.post(actionURL, headers=header)
        if r.status_code != 200:
            if r.status_code == 401:
                msg.VERBOSE("Unauthorized Request (invalid XSRF-TOKEN) [HTTP Response: {}]".format(r.status_code))
            else:
                msg.VERBOSE("Bad request (invalid JSON) [HTTP Response: {}]".format(r.status_code))
        else:
            msg.VERBOSE("Logout Successful [HTTP Response: {}]".format(r.status_code))
        rj = json.loads(r.content.decode('utf-8'))

    def listappads(self, name: str, field: str):
        actionURL = self.ssrm + "app-ads?offset=0&limit=10"
        if name is not None:
            actionURL = actionURL + "&filter={}&filterField={}".format(name, field)
            msg.VERBOSE("Searching for {} in {}".format(name, field))
        header = {'content-type': 'application/json', 'X-XSRF-TOKEN': self.xsrf_token}
        msg.DEBUG("\n\tURL: {}\n\tHeaders: {}".format(actionURL, header))
        msg.VERBOSE("Getting List of App Ads")
        r = requests.get(actionURL, headers=header)
        if r.status_code != 200:
            if r.status_code == 401:
                msg.VERBOSE("Unauthorized Request (invalid XSRF-TOKEN) [HTTP Response: {}]".format(r.status_code))
            else:
                msg.VERBOSE("Bad request (invalid JSON) [HTTP Response: {}]".format(r.status_code))
        else:
            msg.VERBOSE("Get List of Ads successful [HTTP Response: {}]".format(r.status_code))
        rj = json.loads(r.content.decode('utf-8'))
        return rj

    def makeappad(self, pname, pdet):
        self.data['adName'] = pname
        self.data['category'] = pdet['category_en']
        self.data['advertiser'] = pdet['company']
        self.data['packageName'] = pname
        self.data['content'][0]['title'] = pname
        self.data['content'][0]['category'] = pdet['category_en']
        self.data['content'][0]['description'] = pname
        self.data['content'][0]['appStoreUris'][0]['uri'] = pdet['directurl']
        self.data['content'][0]['images'][2]['imageUri'] =  pdet['iconurl']
        self.data['content'][1]['title'] = pdet['description']
        self.data['content'][1]['category'] = pdet['category_zh']
        self.data['content'][1]['description'] = pdet['description']
        self.data['content'][1]['appStoreUris'][0]['uri'] = pdet['directurl']
        self.data['content'][1]['images'][2]['imageUri'] =  pdet['iconurl']
        # print(json.dumps(self.data, indent=4))
        self.pushappad()

    def pushappad(self):
        msg.VERBOSE("Pushing ad {}".format(self.data['adName']))
        if self.checkadexist(self.data['packageName']):
            # TODO insert Update code here
            msg.VERBOSE("An ad for {} exists. Skipping creation".format(self.data['packageName']))
        else:
            actionURL = self.ssrm + "app-ads"
            header = {'content-type': 'application/json', 'X-XSRF-TOKEN': self.xsrf_token}
            msg.DEBUG("\n\tURL: {}\n\tjson: {}\n\tHeaders: {}".format(actionURL, self.data, header))
            msg.VERBOSE("Logging in")
            r = requests.post(actionURL, json=self.data, headers=header)
            if r.status_code != 200:
                if r.status_code == 401:
                    msg.VERBOSE("Unauthorized Request (invalid XSRF-TOKEN) [HTTP Response: {}]".format(r.status_code))
                else:
                    msg.VERBOSE("Bad request (invalid JSON) [HTTP Response: {}]".format(r.status_code))
            else:
                msg.VERBOSE("Create successful [HTTP Response: {}]".format(r.status_code))
                print("Create of {} sucessful, key: {}".format(self.data['adName'], r.json()['key']))


    def checkadexist(self, name: str):
        actionURL = self.ssrm + "app-ads?offset=0&limit=10&filter={}&filterField={}".format(name, 'packageName')
        header = {'content-type': 'application/json', 'X-XSRF-TOKEN': self.xsrf_token}
        msg.DEBUG("Checking for ad\n\tURL: {}\n\tHeaders: {}".format(actionURL, header))
        r = requests.get(actionURL, headers=header)
        if r.status_code == 200:
            return True
        else:
            return False




def main():
    """main processing loop"""
    do = arg.MyArgs(usagemsg)
    do.processargs()
    msg.TEST("Running in test mode. Using http://app.mi.com/hotCatApp/12")
    # msg.DEBUG(do)

    applistfile = arg.Flags.configsettings['urlout'].format(arg.Flags.configsettings['applistnumber'])
    rd = rb.ReadJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'], applistfile)
    rd.readinput()

    # msg.DEBUG(json.dumps(rd.data, indent=4, ensure_ascii=False))

    ad = SSRMApi("admin", "Apple1995!", "https://ssrm-dev.securespaces.net")
    ad.gettoken()
    ad.getsession()

    # adlist = ad.listappads('com.v.study', 'packageName')
    # print("Count of ads: {}".format(adlist['count']))
    # for a in adlist['items']:
    #     print(json.dumps(a, indent=4, ensure_ascii=False))

    for pgkname in rd.data:
        ad.makeappad(pgkname, rd.data[pgkname])

    ad.logoutsession()






if __name__ == '__main__':
    main()