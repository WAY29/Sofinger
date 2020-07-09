'''
@Description: SoFinger_cms_md5
@Author: Longlone
@LastEditors  : Longlone
@Date: 2020-01-07 16:53:27
@LastEditTime : 2020-01-10 13:42:52
'''
import asyncio
import os
import signal
from hashlib import md5
from threading import Thread
from time import sleep, time
import multiprocessing
from multiprocessing.managers import BaseManager

import requests

from general import message, requests_headers, connect, update, close

MANAGER = multiprocessing.Manager()
SUCCESS = MANAGER.list([])
TOTAL = 0
NUM = multiprocessing.Value('d', 0)
THREAD = 10
VERBOSE = False



def getmd5(s):
    '''
    @description: Md5 encoding a string
    @param s{str}
    @return: md5 string{str}
    '''
    return md5(s).hexdigest()


async def check(url, cms_tuple, timeout, NUM, SUCCESS, SESSION):  # MD5检测
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
        if (req.status_code == 200 and getmd5(req.content) == cms_match_pattern):
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


async def main(url, cms_list, loop, timeout, NUM, SUCCESS, SESSION):  # 异步主函数
    task_list = []
    for each_tuple in cms_list:
        task_list.append(loop.create_task(
            check(url, each_tuple, timeout, NUM, SUCCESS, SESSION)))
    for each_task in task_list:
        await each_task
    for each_task in task_list:  # 获取每个协程的返回
        result = each_task.result()
        if (result[0] is True):  # 返回为真
            message_tuple = result[1]
            if (message_tuple[0] not in SUCCESS):  # 去重
                SUCCESS.append(message_tuple[0])
                print('')
                message('+', '%s' % (message_tuple[0]))
                try:
                    os.kill(signal.CTRL_C_EVENT, 0)
                except Exception:
                    pass


def thread_run(url, cms_list, timeout, NUM, SUCCESS, SESSION):  # 线程主函数
    loop = asyncio.new_event_loop()
    try:
        asyncio.events.set_event_loop(loop)
        loop.run_until_complete(
            main(url, cms_list, loop, timeout, NUM, SUCCESS, SESSION))
    except Exception as e:
        print(e)
    finally:
        loop.close()


def progress_run(cms_list, url, timeout, NUM, SUCCESS, SESSION):  # 进程主函数
    try:
        for each_cms_list in cms_list:
            t = Thread(target=thread_run, args=(
                url, each_cms_list, timeout, NUM, SUCCESS, SESSION))
            t.setDaemon(True)
            t.start()
    except Exception:
        pass


class MyManager(BaseManager):
    pass


def Manager2():
    m = MyManager()
    m.start()
    return m


MyManager.register('session', requests.Session)


def run(url, cms_list, timeout, thread, verbose):
    global TOTAL, THREAD, VERBOSE, NUM, SUCCESS, MANAGER
    # --------------------------------------------
    SUCCESS = MANAGER.list([])
    manager = Manager2()
    SESSION = manager.session()
    # SESSION = requests.Session()
    SESSION.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
    SESSION.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
    TOTAL = len(cms_list)
    THREAD = thread
    VERBOSE = verbose
    unique_name = []
    unique_list = []
    other_list = []
    new_cms_list = []
    message('#', 'Started CMS_MD5')
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
    PROGRESS = 6
    POOL = multiprocessing.Pool(PROGRESS)
    final_cms_list = []
    for i in range(0, len(new_cms_list), PROGRESS):  # 把new_cms_list分成6组
        final_cms_list.append(new_cms_list[i:i+PROGRESS])
    try:
        for i in range(PROGRESS):
            POOL.apply_async(progress_run, args=(
                final_cms_list, url, timeout, NUM, SUCCESS, SESSION))
        POOL.close()
        while (len(SUCCESS) == 0 and NUM.value < TOTAL):
            print("[%s%s]%.2f%%" % ('>'*int(NUM.value*50//TOTAL), ' ' *
                                    int(50-NUM.value*50//TOTAL), float(NUM.value)*100.0/TOTAL), end="\r")
            sleep(0.2)
    except KeyboardInterrupt:
        print('Finished/Interrupt')
    finally:
        POOL.terminate()
        print('')
        message('#', 'Finished CMS_MD5')
        message('#', 'Total Time: %.2f' % (time() - now))
    # --------------------------------------------
    return SUCCESS
