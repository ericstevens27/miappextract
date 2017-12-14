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
        self.nameprefix = "Xiaomi_"
        self.data = {
            "adName": "Xiaomi_example.app.ad",
            "content": [
                {
                    "title": "Xiaomi Example App Ad",
                    "category": "Demo and Testing",
                    "description": "An app ad example for documentation",
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
            "packageName": "com.securespaces.package.name"
        }
        self.actiondesc = {
            "gettoken": "Get session token",
            "getsession": "get session info",
            "logout": "Logout",
            "list": "List app ads",
            "create": "Create app ad",
            "update": "Update app ad"
        }
        self.errcodes = {
            "200": {
                "gettoken": "Success",
                "getsession": "Success",
                "logout": "Success",
                "list": "Success",
                "create": "Success",
                "update": "Success"
            },
            "400": {
                "gettoken": "Bad request (Invalid JSON)",
                "getsession": "Unknown error",
                "logout": "Unknown error",
                "list": "Bad request (Invalid parameters)",
                "create": "Bad request (Invalid JSON or Duplicate ad name)",
                "update": "Bad request (Invalid JSON, invalid ad-key or Duplicate ad name)"
            },
            "401": {
                "gettoken": "Unauthorized request (Invalid username or password)",
                "getsession": "Unauthorized request (Invalid XSRF-TOKEN)",
                "logout": "Unauthorized request (Invalid XSRF-TOKEN)",
                "list": "Unauthorized request (Invalid XSRF-TOKEN)",
                "create": "Unauthorized request (Invalid XSRF-TOKEN)",
                "update": "Unauthorized request (Invalid XSRF-TOKEN)"
            },
            "other": {
                "gettoken": "Unknown error",
                "getsession": "Unknown error",
                "logout": "Unknown error",
                "list": "Unknown error",
                "create": "Unknown error",
                "update": "Unknown error"
            }
        }

    def gettoken(self) -> bool:
        """get the session token - required for all other calls"""
        action = "gettoken"
        actionurl = self.ssrm + "security/login"
        authjson = {"username": self.user, "password": self.password}
        header = {'content-type': 'application/json'}
        msg.DEBUG("\n\tURL: {}\n\tjson: {}\n\tHeaders: {}".format(actionurl, authjson, header))
        # msg.VERBOSE("{}".format(self.actiondesc[action]))
        r = requests.post(actionurl, json=authjson, headers=header)
        if self.checkstatus(r, action):
            rj = json.loads(r.content.decode('utf-8'))
            self.xsrf_token = r.json()['xsrfToken']
            return True
        else:
            return False

    def getsession(self):
        """get the session info"""
        action = "getsession"
        actionurl = self.ssrm + "security/currentSessionInfo"
        header = {'content-type': 'application/json', 'X-XSRF-TOKEN': self.xsrf_token}
        msg.DEBUG("\n\tURL: {}\n\tHeaders: {}".format(actionurl, header))
        # msg.VERBOSE("{}".format(self.actiondesc[action]))
        r = requests.get(actionurl, headers=header)
        if self.checkstatus(r, action):
            rj = json.loads(r.content.decode('utf-8'))
            msg.DEBUG("User name is {}".format(rj['username']))
            return rj
        else:
            return None

    def logoutsession(self):
        """logout of the session"""
        action = "logout"
        actionurl = self.ssrm + "security/logout"
        header = {'content-type': 'application/json', 'X-XSRF-TOKEN': self.xsrf_token}
        msg.DEBUG("\n\tURL: {}\n\tHeaders: {}".format(actionurl, header))
        # msg.VERBOSE("{}".format(self.actiondesc[action]))
        r = requests.post(actionurl, headers=header)
        if self.checkstatus(r, action):
            rj = json.loads(r.content.decode('utf-8'))
            return rj
        else:
            return None

    def listappads(self, name: str, field: str):
        """returns a list of all ads based on the filter field search"""
        action = "list"
        actionurl = self.ssrm + "app-ads?offset=0&limit=10"
        if name is not None:
            actionurl = actionurl + "&filter={}&filterField={}".format(name, field)
            msg.VERBOSE("Searching for {} in {}".format(name, field))
        header = {'content-type': 'application/json', 'X-XSRF-TOKEN': self.xsrf_token}
        msg.DEBUG("\n\tURL: {}\n\tHeaders: {}".format(actionurl, header))
        msg.VERBOSE("{}".format(self.actiondesc[action]))
        r = requests.get(actionurl, headers=header)
        if self.checkstatus(r, action):
            rj = json.loads(r.content.decode('utf-8'))
            return rj
        else:
            return None

    def makeappad(self, pname, pdet):
        """forms up the data fields needed to construct or update the ad"""
        # Name is the prefix 'Xiaomi_' plus to package name to be unique
        self.data['adName'] = self.nameprefix + pname
        self.data['category'] = pdet['category_en']
        self.data['advertiser'] = pdet['company']
        self.data['packageName'] = pname
        self.data['content'][0]['title'] = pname[:30]   # title is limited to 30 characters
        self.data['content'][0]['category'] = pdet['category_en']
        self.data['content'][0]['description'] = pname
        self.data['content'][0]['appStoreUris'][0]['uri'] = pdet['directurl']
        self.data['content'][0]['images'][2]['imageUri'] = pdet['iconurl']
        self.data['content'][1]['title'] = pdet['description'][:30]     # title is limited to 30 characters
        self.data['content'][1]['category'] = pdet['category_zh']
        self.data['content'][1]['description'] = pdet['description']
        self.data['content'][1]['appStoreUris'][0]['uri'] = pdet['directurl']
        self.data['content'][1]['images'][2]['imageUri'] = pdet['iconurl']
        # print(json.dumps(self.data, indent=4))
        self.pushappad()

    def pushappad(self):
        """Checks for an ad with the same packname and if not then creates the ad"""
        msg.VERBOSE("Processing ad {}".format(self.data['adName']))
        adkey = self.getad(self.data['adName'])
        if adkey is not None:
            if arg.Flags.update:
                # Update this ad
                self.updatead(adkey)
            else:
                msg.VERBOSE("An ad for {} exists ({}). Update flag is false. Skipping creation".format(self.data['adName'], adkey))
        else:
            self.createad()

    def createad(self):
        """Creates the ad using the values in data"""
        action = "create"
        actionurl = self.ssrm + "app-ads"
        header = {'content-type': 'application/json', 'X-XSRF-TOKEN': self.xsrf_token}
        msg.DEBUG("\n\tURL: {}\n\tjson: {}\n\tHeaders: {}".format(actionurl, self.data, header))
        msg.DEBUG("{} {}".format(self.actiondesc[action], self.data['adName']))
        r = requests.post(actionurl, json=self.data, headers=header)
        self.checkstatus(r, action)

    def updatead(self, key):
        """Updates the ad using the key with values in data"""
        action = "update"
        actionurl = self.ssrm + "app-ads/" + key
        header = {'content-type': 'application/json', 'X-XSRF-TOKEN': self.xsrf_token}
        msg.DEBUG("\n\tURL: {}\n\tjson: {}\n\tHeaders: {}".format(actionurl, self.data, header))
        msg.DEBUG("{} {}".format(self.actiondesc[action], self.data['adName']))
        r = requests.put(actionurl, json=self.data, headers=header)
        self.checkstatus(r, action)

    def checkstatus(self, r, action) -> bool:
        if str(r.status_code) in self.errcodes:
            if r.status_code == 200:
                msg.VERBOSE("{} {}".format(self.actiondesc[action],
                                           self.errcodes[str(r.status_code)][action]))
            else:
                msg.VERBOSE("{} {} [HTTP Response: {}]".format(self.actiondesc[action],
                                                               self.errcodes[str(r.status_code)][action],
                                                               r.status_code))
        else:
            msg.VERBOSE("{} {} [HTTP Response: {}]".format(self.actiondesc[action],
                                                           self.errcodes['other'][action],
                                                           r.status_code))
        if r.status_code == 200:
            return True
        else:
            return False

    def checkadexist(self, name: str) -> bool:
        """searches for an ad by the adName field which must be unique"""
        actionurl = self.ssrm + "app-ads?offset=0&limit=10&filter={}&filterField={}".format(name, 'adName')
        header = {'content-type': 'application/json', 'X-XSRF-TOKEN': self.xsrf_token}
        msg.DEBUG("Checking for ad\n\tURL: {}\n\tHeaders: {}".format(actionurl, header))
        r = requests.get(actionurl, headers=header)
        if r.status_code == 200:
            result = json.loads(r.content.decode('utf-8'))
            if result['count'] != 1:
                # if we get 0 then no record. If we get more than one then we cannot update
                return False
            else:
                return True
        else:
            return False

    def getad(self, name: str):
        """searches for an ad by the adName field which must be unique"""
        actionurl = self.ssrm + "app-ads?offset=0&limit=10&filter={}&filterField={}".format(name, 'adName')
        header = {'content-type': 'application/json', 'X-XSRF-TOKEN': self.xsrf_token}
        msg.DEBUG("Checking for ad\n\tURL: {}\n\tHeaders: {}".format(actionurl, header))
        r = requests.get(actionurl, headers=header)
        if r.status_code == 200:
            result = json.loads(r.content.decode('utf-8'))
            if result['count'] != 1:
                # if we get 0 then no record. If we get more than one then we cannot update
                return None
            else:
                # print(result)
                return result['items'][0]['key']
        else:
            return None


def main():
    """main processing loop"""
    do = arg.MyArgs(usagemsg)
    do.processargs()
    msg.TEST("Running in test mode. Using http://app.mi.com/hotCatApp/12")
    # msg.DEBUG(do)

    applistfile = arg.Flags.configsettings['urlout'].format(arg.Flags.configsettings['applistnumber'])
    rd = rb.ReadJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'], applistfile)
    rd.readinput()
    ad = SSRMApi(arg.Flags.configsettings['username'], arg.Flags.configsettings['password'], arg.Flags.configsettings['serverurl'])
    msg.VERBOSE("Starting Processing")
    if ad.gettoken():
        for pgkname in rd.data:
            ad.makeappad(pgkname, rd.data[pgkname])
        ad.logoutsession()


if __name__ == '__main__':
    main()
