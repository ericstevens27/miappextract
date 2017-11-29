from bs4 import BeautifulSoup
import httplib2
import json
import re
import readbase as rb
import argbase as arg
import requests

# define global variables
# options as globals
usagemsg = "This program reads the Xiaomi Mi Store Application site, extracts the list of applications and then" \
           "writes the download and icon urls to a file. " \
           "The URLS are written to a json file."
msg = arg.MSG()


def main():
    """main processing loop"""
    do = arg.MyArgs(usagemsg)
    do.processargs()
    msg.TEST("Running in test mode. Using http://app.mi.com/hotCatApp/12")
    # msg.DEBUG(do)

    writefile = rb.WriteJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                             arg.Flags.configsettings['urlout'])
    foundmatch = False

    http = httplib2.Http()
    if arg.Flags.test:
        appURL = "http://app.mi.com/hotCatApp/12"
    else:
        appURL = arg.Flags.configsettings['appurl']
    status, response = http.request(appURL)
    soup = BeautifulSoup(response, 'html.parser')

    re_applist = r"(^<ul class=\"applist\">)"
    re_divdown = r"(^<div class=\"app-info-down\">)"
    re_hrefid = r"details\?id=(.*?)$"
    re_download = r"download/(.*?)$"

    # (pkgname, iconurl, pkgdesc) = ("", "", "")
    packagedata = {}
    #
    data = soup.find_all("ul")
    for e in data:
        divcheck = extractgroup(re.search(re_applist, str(e)))
        if divcheck is not None:
            msg.DEBUG("Found applist in {}".format(e))
            ulsoup = BeautifulSoup(str(e), 'html.parser')
            lidata = ulsoup.find_all("li")
            for child in lidata:
                # print("Child in li {}".format(child))
                lisoup = BeautifulSoup(str(child), 'html.parser')
                linkdata = lisoup.find_all('a')
                packagename = extractgroup(re.search(re_hrefid, linkdata[1].get('href')))
                imgdata = lisoup.find_all('img')
                src = imgdata[0].get('data-src')
                desc = imgdata[0].get('alt')
                msg.DEBUG("I found package {} ({}) with icon url of {}".format(packagename, desc, src))
                packagedata[packagename] = {'description': desc, 'iconurl': src}

    for pkgkey in packagedata:
        # go pull each page for each package
        detailsURL = arg.Flags.configsettings['appdetailsbaseurl'].format(pkgkey)
        status, response = http.request(detailsURL)
        detailsoup = BeautifulSoup(response, 'html.parser')
        data = detailsoup.find_all("div")
        for e in data:
            divcheck = extractgroup(re.search(re_divdown, str(e)))
            if divcheck is not None:
                msg.DEBUG("Found div download in {}".format(e))
                divsoup = BeautifulSoup(str(e), 'html.parser')
                linkdata = divsoup.find_all('a')
                appid = extractgroup(re.search(re_download, linkdata[0].get('href')))
                directURL = geturl(appid)
                msg.DEBUG("I found {} for package {} and direct url of {}".format(appid, pkgkey, directURL))
                packagedata[pkgkey].update({'appid': appid, 'directurl': directURL})

    writefile.data = packagedata
    writefile.writeoutput()


def geturl(appid: str):
    actionURL = arg.Flags.configsettings['baseurl'].format(appid)
    r = requests.get(actionURL)
    return r.url


def extractgroup(match):
    """extract the group (index: 1) from the match object"""
    if match is None:
        return None
    return match.group(1)


def extractgroups(match):
    """extract all of the matching groups from the regex object"""
    if match is None:
        return None
    return match.groups()




if __name__ == '__main__':
    main()
