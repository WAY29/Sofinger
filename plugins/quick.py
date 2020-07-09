'''
@Description: SoFinger_cms_quick
@Author: Longlone
@LastEditors  : Longlone
@Date: 2020-01-09 13:13:10
@LastEditTime : 2020-01-13 08:38:45
'''
import asyncio
import re

from urllib3 import disable_warnings

from general import message, connect, select_fofa_hit, update_fofa

retitle = re.compile(r'<title>(.*?)<\/title>')
rtitle = re.compile(r'title="(.*)"')
rntitle = re.compile(r'title!="(.*)"')
rheader = re.compile(r'header="(.*)"')
rnheader = re.compile(r'header!="(.*)"')
rbody = re.compile(r'body="(.*)"')
rnbody = re.compile(r'body!="(.*)"')
rbracket = re.compile(r'\((.*)\)')
SUCCESS = []
ARG_DICT = {}
INDEX = ''
HEADERS = ''
TIMTOUT = 3

disable_warnings()


def get_title(content):  # 获取web信息
    global retitle
    try:
        title = retitle.search(content).group(1).strip()
        return title
    except Exception:
        return ''


def check_rule(key, header, body, title):  # 指纹识别核心
    try:
        if 'title' in key:
            if ('!=' in key):
                if re.findall(rntitle, key)[0].lower() not in title.lower():
                    return True
            else:
                if re.findall(rtitle, key)[0].lower() in title.lower():
                    return True
        elif 'body' in key:
            if ('!=' in key):
                if re.findall(rnbody, key)[0] not in body:
                    return True
            else:
                if re.findall(rbody, key)[0] in body:
                    return True
        else:
            if ('!=' in key):
                if(re.findall(rnheader, key)[0] not in header):
                    return True
            else:
                if(re.findall(rheader, key)[0] in header):
                    return True
    except Exception:
        pass


def handle(name, key, cms_id, header, body, title):  # 对数据库取出的信息进行拆分并开始指纹识别
    # 满足一个条件即可的情况
    success_list = []
    if ('||' in key and '&&' not in key and '(' not in key):
        for rule in key.split('||'):
            if check_rule(rule, header, body, title):
                success_list.append(name)
                break
    # 只有一个条件的情况
    elif ('||' not in key and '&&' not in key and '(' not in key):
        if check_rule(key, header, body, title):
            success_list.append(name)
    # 需要同时满足条件的情况
    elif ('&&' in key and '||' not in key and '(' not in key):
        num = 0
        for rule in key.split('&&'):
            if check_rule(rule.strip(), header, body, title):
                num += 1
        if (num == len(key.split('&&'))):
            success_list.append(name)
    else:
        # 与条件下存在并条件: 1||2||(3&&4)
        if ('&&' in re.findall(rbracket, key)[0]):
            for rule in key.split('||'):
                if ('&&' in rule):
                    num = 0
                    for _rule in rule.split('&&'):
                        if (check_rule(_rule, header, body, title)):
                            num += 1
                    if (num == len(rule.split('&&'))):
                        success_list.append(name)
                        break
                else:
                    if (check_rule(rule, header, body, title)):
                        success_list.append(name)
                        break
        else:
            # 并条件下存在与条件： 1&&2&&(3||4)
            for rule in key.split('&&'):
                num = 0
                if '||' in rule:
                    for _rule in rule.split('||'):
                        if (check_rule(_rule, title, body, header)):
                            num += 1
                            break
                else:
                    if (check_rule(rule, title, body, header)):
                        num += 1
            if (num == len(key.split('&&'))):
                success_list.append(name)
    for each in success_list:
        try:
            CONN, CURSOR = connect()
            hit = select_fofa_hit(CURSOR, cms_id)
            update_fofa(CONN, CURSOR, hit, cms_id)  # hit++
            CONN.close()
        except Exception:
            pass
    return success_list


async def check(url, cms_tuple, header, body, title):  # 检测主函数
    message_list = []
    cms_name = cms_tuple[0]
    cms_keys = cms_tuple[1]
    cms_id = cms_tuple[2]
    success_flag = False
    try:
        cms_list = handle(cms_name, cms_keys, cms_id, header, body, title)  # 处理信息
        if (len(cms_list) > 0):
            success_flag = True
        message_list.append(tuple(cms_list))
    except Exception:
        pass
    finally:
        return (success_flag, tuple(message_list))


async def main(url, cms_list, loop):  # 异步主函数
    global SUCCESS, ARG_DICT, HEADERS, INDEX
    VERBOSE = ARG_DICT['verbose']
    SILENCE = ARG_DICT['silence']
    if (SILENCE is False):
        message('#', 'Started FOFA_BANNER')
    task_list = []
    header = HEADERS
    body = INDEX
    title = get_title(body)  # 获得标题信息
    for each_tuple in cms_list:
        task_list.append(loop.create_task(
            check(url, each_tuple, header, body, title)))
    for each_task in task_list:
        await each_task
    for each_task in task_list:  # 获取每个任务的返回
        result = each_task.result()
        if (result[0] is True):  # 返回为真
            message_tuple = result[1]
            for each in message_tuple[0]:
                if (each not in SUCCESS):
                    SUCCESS.append(each)
                    if (SILENCE is False and VERBOSE is True):
                        message('+', '%s' % (each))
    if (SILENCE is False):
        message('#', 'Finished FOFA_BANNER')


def run(url, index, headers, cms_list, arg_dict, return_list=None):
    global SUCCESS, ARG_DICT, TIMEOUT, INDEX, HEADERS
    ARG_DICT = arg_dict
    INDEX = index
    HEADERS = headers
    TIMEOUT = arg_dict['timeout']
    SUCCESS = []
    loop = asyncio.new_event_loop()
    try:
        asyncio.events.set_event_loop(loop)
        loop.run_until_complete(main(url, cms_list, loop))
    finally:
        loop.close()
    if (return_list is not None):
        return_list.extend(SUCCESS)
    return SUCCESS
