'''
@Description: SoFinger_cms_md5
@Author: Longlone
@LastEditors  : Longlone
@Date: 2020-01-07 16:53:27
@LastEditTime : 2020-01-12 18:33:12
'''
import asyncio
from hashlib import md5
from threading import Thread
from time import time

import re

from general import message, connect, select_cms_hit, update_cms

SUCCESS = []
REQUEST_DICT = {}
THREAD = 10
VERBOSE = False
SILENCE = False
RULE_NAME = ''


def getmd5(s):
    '''
    @description: Md5 encoding a string
    @param s{str}
    @return: md5 string{str}
    '''
    return md5(s).hexdigest()


def rule(rule_name, pattern, data):
    if (rule_name == 'md5'):
        if (getmd5(data) == pattern):
            return True
    elif (rule_name == 'keyword'):
        if (pattern.lower() in data.lower()):
            return True
    elif (rule_name == 'regx'):
        if (re.search(pattern, data) is not None):
            return True
    return False


async def check(url, cms_tuple):  # 检测主函数
    global SESSION, SUCCESS, REQUEST_DICT
    if (len(SUCCESS) > 0):
        return (False, tuple())
    cms_name = cms_tuple[0]
    cms_path = cms_tuple[1]
    cms_match_pattern = cms_tuple[2]
    cms_id = cms_tuple[3]
    message_list = []
    try:
        if (cms_path in REQUEST_DICT):
            data = REQUEST_DICT[cms_path]
            if (rule(RULE_NAME, cms_match_pattern, data)):
                message_list.append(cms_name)
                try:
                    CONN, CURSOR = connect()
                    cms_hit = select_cms_hit(CURSOR, cms_id)
                    update_cms(CONN, CURSOR, cms_hit, cms_id)  # hit++
                    CONN.close()
                except Exception:
                    pass
                return (True, tuple(message_list))
            else:
                return (False, tuple(message_list))
        else:
            return (False, tuple(message_list))
    except Exception:
        return (False, tuple(message_list))


async def main(url, cms_list, loop):  # 异步主函数
    global SUCCESS, VERBOSE, SILENCE
    task_list = []
    for each_tuple in cms_list:
        task_list.append(loop.create_task(check(url, each_tuple)))
    for each_task in task_list:
        try:
            await asyncio.wait_for(each_task, timeout=2.0)
        except asyncio.TimeoutError:
            pass
    for each_task in task_list:  # 获取每个协程的返回
        result = each_task.result()
        if (result[0] is True):  # 返回为真
            message_tuple = result[1]
            if (message_tuple[0] not in SUCCESS):  # 去重
                SUCCESS.append(message_tuple[0])
                if (VERBOSE is True and SILENCE is False):
                    message('+', '%s' % (message_tuple[0]))


def thread_run(url, cms_list):
    loop = asyncio.new_event_loop()
    try:
        asyncio.events.set_event_loop(loop)
        loop.run_until_complete(main(url, cms_list, loop))
    except Exception as e:
        print(e)
    finally:
        loop.close()


def run(url, cms_list, rule, request_dict, arg_dict, return_list=None):
    global TOTAL, THREAD, VERBOSE, SILENCE, NUM, SUCCESS, RULE_NAME, REQUEST_DICT
    # --------------------------------------------
    SUCCESS = []
    REQUEST_DICT = request_dict
    THREAD = arg_dict['thread']
    VERBOSE = arg_dict['verbose']
    SILENCE = arg_dict['silence']
    RULE_NAME = rule
    unique_name = []
    unique_list = []
    other_list = []
    new_cms_list = [list() for x in range(THREAD)]
    now = time()
    if (SILENCE is False):
        message('#', 'Started CMS_%s' % rule.upper())
    # --------------------------------------------
    for each in cms_list:  # 分开,不同CMS优先跑
        if (each[0][0] not in unique_name):
            unique_name.append(each[0][0])
            unique_list.append(each)
        else:
            other_list.append(each)
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
        thread_list = []
        for each_cms_list in new_cms_list:
            t = Thread(target=thread_run, args=(url, each_cms_list))
            t.setDaemon(True)
            t.start()
            thread_list.append(t)
        for each_thread in thread_list:
            t.join(2)
    except KeyboardInterrupt:
        if (VERBOSE is True and SILENCE is False):
            message('!', 'Finished/Interrupt')
    finally:
        if (SILENCE is False):
            message('#', 'Finished CMS_%s' % rule.upper())
        if (VERBOSE is True and SILENCE is False):
            message('#', '[%s] Total Time: %.2f' % (rule, time() - now))
    # --------------------------------------------
    if (return_list is not None):
        return_list.extend(SUCCESS)
    return SUCCESS
