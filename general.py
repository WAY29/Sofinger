'''
@Description: SoFinger_general
@Author: Longlone
@LastEditors  : Longlone
@Date: 2020-01-09 10:07:00
@LastEditTime : 2020-01-12 14:13:48
'''
import random
import sqlite3
from colorama import init, Fore, Back

init(autoreset=True)


class Colored(object):

    #  前景色:红色  背景色:默认
    def red(self, s):
        return Fore.RED + s + Fore.RESET

    #  前景色:绿色  背景色:默认
    def green(self, s):
        return Fore.GREEN + s + Fore.RESET

    #  前景色:黄色  背景色:默认
    def yellow(self, s):
        return Fore.YELLOW + s + Fore.RESET

    #  前景色:蓝色  背景色:默认
    def blue(self, s):
        return Fore.BLUE + s + Fore.RESET

    #  前景色:洋红色  背景色:默认
    def magenta(self, s):
        return Fore.MAGENTA + s + Fore.RESET

    #  前景色:青色  背景色:默认
    def cyan(self, s):
        return Fore.CYAN + s + Fore.RESET

    #  前景色:白色  背景色:默认
    def white(self, s):
        return Fore.WHITE + s + Fore.RESET

    #  前景色:黑色  背景色:默认
    def black(self, s):
        return Fore.BLACK

    #  前景色:白色  背景色:绿色
    def white_green(self, s):
        return Fore.WHITE + Back.GREEN + s + Fore.RESET + Back.RESET


color = Colored()


def connect():
    try:
        CONN = sqlite3.connect('cms_finger.db')
        CURSOR = CONN.cursor()
        return CONN, CURSOR
    except Exception:
        return None, None


def select_cms_hit(CURSOR, id):
    sql = "SELECT hit from cms WHERE finger_id=%s" % (id)
    try:
        return CURSOR.execute(sql).fetchone()[0]
    except Exception as e:
        print(e)


def select_fofa_hit(CURSOR, id):
    sql = "SELECT hit from fofa WHERE id=%s" % (id)
    try:
        return CURSOR.execute(sql).fetchone()[0]
    except Exception as e:
        print(e)


def update_cms(CONN, CURSOR, hit, id):
    sql = "UPDATE cms SET hit=%s WHERE finger_id=%s" % (hit + 1, id)
    try:
        CURSOR.execute(sql)
        CONN.commit()
    except Exception as e:
        print(e)


def update_fofa(CONN, CURSOR, hit, id):
    sql = "UPDATE fofa SET hit=%s WHERE id=%s" % (hit + 1, id)
    try:
        CURSOR.execute(sql)
        CONN.commit()
    except Exception as e:
        print(e)


def requests_headers():
    user_agent = ['Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.8.1) Gecko/20061010 Firefox/2.0',
                  'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.6 Safari/532.0',
                  'Mozilla/5.0 (Windows; U; Windows NT 5.1 ; x64; en-US; rv:1.9.1b2pre) Gecko/20081026 Firefox/3.1b2pre',
                  'Opera/10.60 (Windows NT 5.1; U; zh-cn) Presto/2.6.30 Version/10.60', 'Opera/8.01 (J2ME/MIDP; Opera Mini/2.0.4062; en; U; ssr)',
                  'Mozilla/5.0 (Windows; U; Windows NT 5.1; ; rv:1.9.0.14) Gecko/2009082707 Firefox/3.0.14',
                  'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36',
                  'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                  'Mozilla/5.0 (Windows; U; Windows NT 6.0; fr; rv:1.9.2.4) Gecko/20100523 Firefox/3.6.4 ( .NET CLR 3.5.30729)',
                  'Mozilla/5.0 (Windows; U; Windows NT 6.0; fr-FR) AppleWebKit/528.16 (KHTML, like Gecko) Version/4.0 Safari/528.16',
                  'Mozilla/5.0 (Windows; U; Windows NT 6.0; fr-FR) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5']
    UA = random.choice(user_agent)
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': UA,
        'Upgrade-Insecure-Requests': '1', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0',
        'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'zh-CN,zh;q=0.8',
        "Referer": "http://www.baidu.com/link?url=www.so.com&url=www.soso.com&&url=www.sogou.com",
        'Cookie': "PHPSESSID=gljsd5c3ei5n813roo4878q203"}
    return headers


def message(sign, mes):
    if (sign == '-'):
        print(color.red('[-]'), mes)
    elif (sign == '+'):
        print(color.green('[+]'), mes)
    elif (sign == '#'):
        print(color.cyan('[#]'), mes)
    elif (sign == '!'):
        print(color.yellow('[!]'), mes)
