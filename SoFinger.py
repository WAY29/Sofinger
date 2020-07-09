'''
@Description: SoFinger
@Author: Longlone
@LastEditors  : Longlone
@Supported By  : TideSec/TideFinger zerokeeper/WebEye
@Version : V0.1 Beta
@Date: 2020-01-09 09:20:34
@LastEditTime : 2020-01-14 16:00:21
'''
# TODO config.txt 添加banner

import argparse
from os import path, makedirs
from time import time
import multiprocessing

from general import connect, message, color
from Myplugin import Platform

CURSOR = None
CONN = None


def select(sql):
    global CURSOR
    try:
        CURSOR.execute(sql)
        return CURSOR.fetchall()
    except Exception:
        return None


if (__name__ == '__main__'):
    # --------------------------------------------
    CONN, CURSOR = connect()
    if (CONN is None and CURSOR is None):
        message('-', ' Connect database failed')
        exit(1)

    # --------------------------------------------
    parser = argparse.ArgumentParser(
        description='Check CMS for website(s).', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'url', nargs='+', help='The website URL/ The URLs File')
    parser.add_argument(
        '--version', action='version', version='SoFinger Version: 0.1 Beta', help='Show version and exit')
    parser.add_argument('--time', nargs='?', type=int,
                        default=3, const=1, help=' Timeout of requests')
    parser.add_argument('--thread', nargs='?', type=int,
                        default=20, const=1, help=' Thread number for tasks')
    parser.add_argument('--retry', nargs='?', type=int,
                        default=1, const=1, help='Maximum number of attempts per link')
    parser.add_argument(
        '--verbose', help='Verbose output', action='store_true')
    parser.add_argument('-s', '--silence',
                        help='Keep slience when running', action='store_true')
    parser.add_argument(
        '-f', '--fast', help='Use silence mode, and all plugins will be run at the same time by multiprocessing.', action='store_true')
    args = parser.parse_args()
    urls = args.url
    if (len(urls) == 1 and path.isfile(urls[0])):
        f = open(urls[0], 'r')
        urls = f.readlines()
        urls = [s.strip() for s in urls]
        f.close()
    fast = True if (args.fast) else False
    silence = True if (args.silence or fast is True) else False
    verbose = True if (args.verbose) else False
    # --------------------------------------------
    # if (silence is False):
    #     import logo
    # --------------------------------------------
    pf = Platform('plugins', required='run', message=True)
    # for each in pf.get_messages():
    #     message('#', each)
    preload_cms = select(
        "SELECT distinct path, options FROM cms ORDER BY hit DESC")
    quick_cms = select(
        "SELECT name, keys, id, hit FROM fofa ORDER BY hit DESC")
    md5_cms = select(
        "SELECT cms_name, path, match_pattern, finger_id FROM cms WHERE options='md5' ORDER BY hit DESC")
    keyword_cms = select(
        "SELECT cms_name, path, match_pattern, finger_id FROM cms WHERE options='keyword' ORDER BY hit DESC")
    regx_cms = select(
        "SELECT cms_name, path, match_pattern, finger_id FROM cms WHERE options='regx' ORDER BY hit DESC")
    # --------------------------------------------
    for each_url in urls:
        each_url = each_url.strip()
        if ('//' in each_url):
            store_path = 'Results/' + each_url.split('//')[1].replace('/', '')
        else:
            store_path = 'Results/' + each_url.replace('/', '')
        if (not path.isdir(store_path)):
            makedirs(store_path)
        now = time()
        message('!', 'Target URL: %s' % each_url)
        # --------------------------------------------
        if (fast is True):
            MANAGER = multiprocessing.Manager()
            ARG_DICT = MANAGER.dict()
            REQUEST_DICT = MANAGER.dict()
            CMS_SUCCESS = MANAGER.list()
        else:
            ARG_DICT = dict()
            REQUEST_DICT = dict()
            CMS_SUCCESS = list()
            QUICK_SUCCESS = list()
        ARG_DICT['timeout'] = args.time
        ARG_DICT['retry'] = args.retry
        ARG_DICT['thread'] = args.thread
        ARG_DICT['silence'] = silence
        ARG_DICT['verbose'] = verbose
        ARG_DICT['fast'] = fast
        # --------------------------------------------
        if (fast is True):  # 快速模式
            process_list = []
            QUICK_SUCCESS = MANAGER.list()
            preload_p = multiprocessing.Process(target=pf['preload'].run, args=(each_url, preload_cms,  ARG_DICT, REQUEST_DICT))
            preload_p.start()
            try:
                preload_p.join()  # 等待preload结束
            except KeyboardInterrupt:
                exit(1)
            if ('/' in REQUEST_DICT):
                quick_p = multiprocessing.Process(target=pf['quick'].run, args=(each_url, REQUEST_DICT['/'], REQUEST_DICT['headers'], quick_cms,  ARG_DICT, QUICK_SUCCESS))
                process_list.append(quick_p)
            cms_p1 = multiprocessing.Process(target=pf['cms'].run, args=(each_url, md5_cms, 'md5', REQUEST_DICT, ARG_DICT, CMS_SUCCESS))  # MD5检测
            process_list.append(cms_p1)
            cms_p2 = multiprocessing.Process(target=pf['cms'].run, args=(each_url, keyword_cms, 'keyword', REQUEST_DICT, ARG_DICT, CMS_SUCCESS))    # regx检测
            process_list.append(cms_p2)
            cms_p3 = multiprocessing.Process(target=pf['cms'].run, args=(each_url, regx_cms, 'regx', REQUEST_DICT, ARG_DICT, CMS_SUCCESS))    # keyword检测
            process_list.append(cms_p3)
            for each in process_list:
                each.start()
            for each in process_list:
                each.join()
        else:
            REQUEST_DICT = pf['preload'].run(each_url, preload_cms, ARG_DICT)
            if ('STOP' in REQUEST_DICT):
                exit(1)
            if ('/' in REQUEST_DICT):
                QUICK_SUCCESS = pf['quick'].run(each_url, REQUEST_DICT['/'], REQUEST_DICT['headers'], quick_cms, ARG_DICT)
            CMS_SUCCESS.extend(pf['cms'].run(
                each_url, md5_cms, 'md5', REQUEST_DICT, ARG_DICT))  # MD5检测
            CMS_SUCCESS.extend(pf['cms'].run(
                each_url, regx_cms, 'regx', REQUEST_DICT, ARG_DICT))  # regx检测
            CMS_SUCCESS.extend(pf['cms'].run(
                each_url, keyword_cms, 'keyword', REQUEST_DICT, ARG_DICT))  # keyword检测
        # --------------------------------------------
        print()
        QUICK_SUCCESS = set(QUICK_SUCCESS)
        CMS_SUCCESS = set(CMS_SUCCESS)
        message('+', '%s %s (Check: %s)' % ('Current Task:',
                                            color.cyan(each_url), color.yellow(store_path + '/')))
        print('-' * 50)
        message('+', '%s %s' % (color.red('fofa_banner:'),
                                color.green(' '.join(QUICK_SUCCESS))))
        message('+', '%s %s' % (color.red('cms_finger:'),
                                color.green(' '.join(CMS_SUCCESS))))
        interval = str(round(time() - now, 2))
        message('+', '%s %s' %
                (color.red('Total Time:'), color.blue(interval)))
        print('-' * 50)
        with open(store_path + '/results.txt', 'w') as f:
            f.write('fofa_banner: ' + ' '.join(QUICK_SUCCESS) + '\n')
            f.write('cms_finger: ' + ' '.join(CMS_SUCCESS))
    CONN.close()
