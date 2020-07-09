'''
@Description: bar
@Author: Longlone
@LastEditors  : Longlone
@Date: 2020-01-13 08:42:08
@LastEditTime : 2020-01-13 09:08:34
'''


def run(SUM, arg_dict):
    SILENCE = arg_dict['silence']
    while (SUM[0] < SUM[1]):
        if (SILENCE is False):
            print("[%s%s]%.2f%%" % ('>'*int(SUM[0]*50//SUM[1]), ' ' *
                                    int(50-SUM[0]*50//SUM[1]), float(SUM[0])*100.0/SUM[1]), end="\r")
