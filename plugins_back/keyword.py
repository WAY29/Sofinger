'''
@Description: SoFinger_cms_md5
@Author: Longlone
@LastEditors  : Longlone
@Date: 2020-01-07 16:53:27
@LastEditTime : 2020-01-10 13:18:50
'''
import asyncio
import os
import signal
from threading import Thread
from time import sleep, time

import requests

from general import message, requests_headers, connect, update, close
from Global import get

SUCCESS = []
TOTAL = 0
NUM = 0
THREAD = 10
VERBOSE = False
SESSION = requests.Session()
SESSION.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
SESSION.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))


async def check(url, cms_tuple, timeout):  # MD5检测
    global SESSION, NUM
    if (len(SUCCESS) > 0):
        return (False, tuple())
    cms_name = cms_tuple[0]
    cms_path = cms_tuple[1]
    cms_match_pattern = cms_tuple[2]
    cms_id = cms_tuple[3]
    cms_hit = cms_tuple[4]
    message_list = []
    target_url = url + cms_path
    if (VERBOSE is True):
        message('#', 'target:%s' % target_url)
    try:
        req = SESSION.get(
            target_url, headers=requests_headers(),  timeout=timeout)
        if (req.status_code == 200 and cms_match_pattern.lower() in req.text.lower()):
            message_list.append(cms_name)
            try:
                CONN, CURSOR = connect()
                update(CONN, CURSOR, cms_hit, cms_id)  # hit++
                close(CONN)
            except Exception:
                pass
            return (True, tuple(message_list))
        else:
            return (False, tuple(message_list))
    except Exception:
        return (False, tuple(message_list))
    finally:
        NUM += 1


async def main(url, cms_list, loop, timeout):  # 异步主函数
    global SUCCESS, VERBOSE
    task_list = []
    flag = False
    for each_tuple in cms_list:
        task_list.append(loop.create_task(check(url, each_tuple, timeout)))
    for each_task in task_list:
        await each_task
    for each_task in task_list:  # 获取每个协程的返回
        result = each_task.result()
        if (result[0] is True):  # 返回为真
            message_tuple = result[1]
            if (message_tuple[0] not in SUCCESS):  # 去重
                SUCCESS.append(message_tuple[0])
                if (VERBOSE is True):
                    print('')
                    message('+', '%s' % (message_tuple[0]))
                try:
                    if (flag is False):
                        flag = True
                        os.kill(signal.CTRL_C_EVENT, 0)
                except Exception:
                    pass


def thread_run(url, cms_list, timeout):
    loop = asyncio.new_event_loop()
    try:
        asyncio.events.set_event_loop(loop)
        loop.run_until_complete(main(url, cms_list, loop, timeout))
    except Exception as e:
        print(e)
    finally:
        loop.close()


def run(url, cms_list):
    global TOTAL, THREAD, VERBOSE, NUM, SUCCESS, SESSION
    # --------------------------------------------
    SUCCESS = []
    SESSION = requests.Session()
    TOTAL = len(cms_list)
    timeout = get('timeout')
    THREAD = get('thread')
    VERBOSE = get('verbose')
    unique_name = []
    unique_list = []
    other_list = []
    new_cms_list = []
    message('#', 'Started CMS_KEYWORD')
    now = time()
    for each in cms_list:  # 分开,不同CMS优先跑
        if (each[0][0] not in unique_name):
            unique_name.append(each[0][0])
            unique_list.append(each)
        else:
            other_list.append(each)
    for x in range(THREAD):
        new_cms_list.append(list())
    it = 0
    while(len(unique_list) > 0):
        new_cms_list[it].append(unique_list.pop())
        it += 1
        if (it == THREAD):
            it = 0
    it = 0
    while(len(other_list) > 0):
        new_cms_list[it].append(other_list.pop())
        it += 1
        if (it == THREAD):
            it = 0
    # --------------------------------------------
    try:
        for each_cms_list in new_cms_list:
            t = Thread(target=thread_run, args=(url, each_cms_list, timeout))
            t.setDaemon(True)
            t.start()
        while (len(SUCCESS) == 0 and NUM < TOTAL):
            print("[%s%s]%.2f%%" % ('>'*int(NUM*50//TOTAL), ' ' *
                                    int(50-NUM*50//TOTAL), float(NUM)*100.0/TOTAL), end="\r")
            sleep(0.2)
    except KeyboardInterrupt:
        if (VERBOSE is True):
            message('!', 'Finished/Interrupt')
    finally:
        message('#', 'Finished CMS_KEYWORD')
        if (VERBOSE is True):
            message('#', '[%s] Total Time: %.2f' % (__name__, time() - now))
    # --------------------------------------------
    return SUCCESS
