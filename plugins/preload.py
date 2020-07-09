'''
@Description: SoFinger_cms_md5
@Author: Longlone
@LastEditors  : Longlone
@Date: 2020-01-07 16:53:27
@LastEditTime : 2020-01-13 16:30:15
'''
import asyncio
from threading import enumerate
from time import sleep, time

import requests
from func_timeout.StoppableThread import StoppableThread

from general import message, requests_headers

SUCCESS = {}
TOTAL = 0
NUM = 0
THREAD = 10
SILENCE = False
STOP = False
SESSION = None


async def check(url, cms_tuple, timeout):
    global SESSION, SUCCESS, NUM
    cms_path = cms_tuple[0]
    cms_option = cms_tuple[1]
    target_url = url + cms_path
    return_list = ['', '', '']
    try:
        if (cms_path not in SUCCESS):
            req = SESSION.get(
                target_url, headers=requests_headers(),  timeout=timeout)
            if (req.status_code == 200):
                return_list[0] = cms_path
                return_list[2] = str(req.headers)
                if (cms_option == 'md5'):
                    return_list[1] = req.content
                    return (True, return_list)
                else:
                    return_list[1] = req.text
                    return (True, return_list)
            else:
                return (False, return_list)
        else:
            return (False, return_list)
    except Exception:
        return (False, return_list)
    finally:
        NUM += 1


async def main(url, cms_list, loop, timeout):  # 异步主函数
    global SUCCESS
    task_list = []
    for each_tuple in cms_list:
        task_list.append(loop.create_task(check(url, each_tuple, timeout)))
    for each_task in task_list:
        try:
            await asyncio.wait_for(each_task, timeout=timeout)
        except asyncio.TimeoutError:
            pass
    for each_task in task_list:  # 获取每个协程的返回
        result = each_task.result()
        if (result is not None and result[0] is True):  # 返回为真
            return_list = result[1]
            path = return_list[0]
            text = return_list[1]
            if (path != '' and text != ''):
                SUCCESS[path] = text
                if (path == '/'):
                    SUCCESS['headers'] = return_list[2]


def thread_run(url, cms_list, timeout):
    loop = asyncio.new_event_loop()
    try:
        asyncio.events.set_event_loop(loop)
        loop.run_until_complete(main(url, cms_list, loop, timeout))
    except Exception as e:
        print(e)
    finally:
        loop.close()


def run(url, cms_list, arg_dict, return_dict=None):
    global TOTAL, THREAD, SILENCE, NUM, SUCCESS, SESSION, STOP
    # --------------------------------------------
    SUCCESS = {}
    NUM = 0
    TOTAL = len(cms_list)
    timeout = arg_dict['timeout']
    retry = arg_dict['retry']
    THREAD = arg_dict['thread']
    SILENCE = arg_dict['silence']
    SESSION = requests.Session()
    if (retry > 0):
        SESSION.mount(
            'http://', requests.adapters.HTTPAdapter(max_retries=retry))
        SESSION.mount(
            'https://', requests.adapters.HTTPAdapter(max_retries=retry))
    new_cms_list = [list() for x in range(THREAD)]
    now = time()
    if (SILENCE is False):
        message('#', 'Started CMS_PRELOAD')
    it = 0
    while(len(cms_list) > 0):
        new_cms_list[it].append(cms_list.pop())
        it += 1
        if (it == THREAD):
            it = 0
    try:
        thread_list = []
        count = 0
        for each_cms_list in new_cms_list:
            if (len(each_cms_list) > 0):
                t = StoppableThread(target=thread_run, args=(
                    url, each_cms_list, timeout))
                t.setDaemon(True)
                t.start()
                thread_list.append(t)
        while (NUM < TOTAL and len(enumerate()) > 1):
            if (SILENCE is False):
                print("[%s%s]%.2f%%" % ('>'*int(NUM*50//TOTAL), ' ' *
                                        int(50-NUM*50//TOTAL), float(NUM)*100.0/TOTAL), end="\r")
            sleep(0.2)
            count += 1
            if (count >= 1000):  # 超时200秒
                for each in thread_list:
                    each.stop(TimeoutError)
                STOP = True
                SUCCESS['STOP'] = True
                print()
                break
    except KeyboardInterrupt:
        if (SILENCE is False):
            print()
            message('!', 'Interrupt')
        SUCCESS['STOP'] = True
    finally:
        if (STOP not in SUCCESS and STOP is False):  # 正常结束
            print()
        if (SILENCE is False):
            message('#', 'Finished CMS_PRELOAD')
            message('#', '[PRELOAD] Total Time: %.2f' % (time() - now))
        if (STOP is True):
            exit(1)
    # --------------------------------------------
    if (return_dict is not None):
        return_dict.update(SUCCESS)
    return SUCCESS
