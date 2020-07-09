
from hashlib import md5

import requests
import _thread as thread
import time

from general import message, requests_headers

SUCCESS = []
CHECKED = []
FIRSTCMSLIST = []
CMS_NAME = []

totalnum = 0
finished = 1


def getmd5(s):
    '''
    @description: Md5 encoding a string
    @param s{str}
    @return: md5 string{str}
    '''
    return md5(s).hexdigest()


def check(url, cms_tuple):  # MD5检测
    global SUCCESS, FAILS, CHECKED, finished
    cms_match_pattern = cms_tuple[2]
    target_url = url + cms_tuple[1]
    # print("%s %s %s"%(cms_tuple[0], target_url, cms_tuple[2]))
    # message('#', 'target:%s' % target_url)
    for i in range(3):
        try:
            req = requests.get(
                target_url, headers=requests_headers(),  timeout=3)
            if cms_tuple[1] not in CHECKED:
                CHECKED.append(cms_tuple[1])
            if (getmd5(req.content) == cms_match_pattern):
                if cms_tuple[0] not in SUCCESS:
                    SUCCESS.append(cms_tuple[0])
                    print()
                    print("[+] [%s] %s" % (url, cms_tuple[0]))
                break
            else:
                break
        except Exception as e:
            if e is KeyboardInterrupt:
                exit()
            pass
    finished += 1


def run(url, cms_list):
    print("[#] Started md5_leo.")
    global SUCCESS, FAILS, CHECKED, totalnum, finished
    for cms_tuple in cms_list:
        if cms_tuple[0] not in CMS_NAME:
            FIRSTCMSLIST.append(cms_tuple)
            CMS_NAME.append(cms_tuple[0])
    for cms_tuple in FIRSTCMSLIST:
        totalnum += 1
        thread.start_new_thread(check, (url, cms_tuple,))
    while (totalnum - finished > 0):
        time.sleep(1)
        print("\r[%s%s]%d/%d" % ('='*int(finished*50/totalnum),
                                 '-'*int(50-finished*50/totalnum), finished, totalnum), end="")
    totalnum = 0
    finished = 1
    print()
    for cms_tuple in cms_list:
        if cms_tuple[1] not in CHECKED and cms_tuple[0] not in SUCCESS:
            totalnum += 1
            thread.start_new_thread(check, (url, cms_tuple,))
    while (totalnum - finished > 0):
        time.sleep(1)
        print("\r[%s%s]%.2f%%" % ('='*int(finished*50/totalnum),
                                '-'*int(50-finished*50/totalnum), float(finished)/totalnum), end="")
    print()
    print("[#] md5_leo Finished.")
    return SUCCESS
