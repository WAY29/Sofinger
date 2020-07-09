'''
@Description: 
@Author: Longlone
@LastEditors  : Longlone
@Date: 2020-01-14 10:14:50
@LastEditTime : 2020-01-14 10:21:19
'''
import os


if (__name__ == '__main__'):
    try:
        while True:
            url = input('Target URL:')
            for root, dirs, files in os.walk("./Results"):
                for each_dir in dirs:
                    if (each_dir in url):
                        try:
                            with open('./Results/'+each_dir+'/results.txt', 'r') as f:
                                lines = f.readlines()
                                for line in lines:
                                    print(line.strip())
                        except Exception:
                            pass
                        break
    except KeyboardInterrupt:
        pass
