import requests
import argbase as arg

# define global variables
# options as globals
usagemsg = "This program reads the Xiaomi app.mi.com store with specific app number and reports the redirection url" \
            " used to download the APK associated with the app number"
msg = arg.MSG()


def main():
    """main processing loop"""
    do = arg.MyArgs(usagemsg)
    do.processargs()
    msg.TEST("Running in test mode. Using fixed appid of 456819 (com.securespaces.spaces.apk)")
    msg.DEBUG(do)
    if arg.Flags.test:
        geturl('456819')
    else:
        if arg.Flags.appid is None:
            msg.ERROR("App ID is required")
        else:
            geturl(arg.Flags.appid)


def geturl(appid: str):
    msg.VERBOSE("Checking App ID {}".format(appid))
    actionURL = arg.Flags.configsettings['baseurl'].format(appid)
    r = requests.get(actionURL)
    print(r.url)


if __name__ == '__main__':
    main()
