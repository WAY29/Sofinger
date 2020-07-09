'''
@Description: print logo
@Author: Longlone
@LastEditors  : Longlone
@Date: 2020-01-14 15:57:01
@LastEditTime : 2020-01-14 15:57:38
'''
from random import randint


logo = randint(1, 3)
if (logo == 1):
    print(r"""

  ______             ________  __
 /      \           |        \|  \
|  $$$$$$\  ______  | $$$$$$$$ \$$ _______    ______    ______    ______
| $$___\$$ /      \ | $$__    |  \|       \  /      \  /      \  /      \
 \$$    \ |  $$$$$$\| $$  \   | $$| $$$$$$$\|  $$$$$$\|  $$$$$$\|  $$$$$$\
 _\$$$$$$\| $$  | $$| $$$$$   | $$| $$  | $$| $$  | $$| $$    $$| $$   \$$
|  \__| $$| $$__/ $$| $$      | $$| $$  | $$| $$__| $$| $$$$$$$$| $$
 \$$    $$ \$$    $$| $$      | $$| $$  | $$ \$$    $$ \$$     \| $$
  \$$$$$$   \$$$$$$  \$$       \$$ \$$   \$$ _\$$$$$$$  \$$$$$$$ \$$
                                            |  \__| $$
                                             \$$    $$
                                              \$$$$$$
""")
elif (logo == 2):
    print(r"""

   _____       _______
  / ___/____  / ____(_)___  ____ ____  _____
  \__ \/ __ \/ /_  / / __ \/ __ `/ _ \/ ___/
 ___/ / /_/ / __/ / / / / / /_/ /  __/ /
/____/\____/_/   /_/_/ /_/\__, /\___/_/
                         /____/

""")
elif (logo == 3):
    print(r"""
  ____            ________
 6MMMMb\          `MMMMMMM 68b
6M'    `           MM    \ Y89
MM         _____   MM      ___ ___  __     __      ____  ___  __
YM.       6MMMMMb  MM   ,  `MM `MM 6MMb   6MMbMMM 6MMMMb `MM 6MM
 YMMMMb  6M'   `Mb MMMMMM   MM  MMM9 `Mb 6M'`Mb  6M'  `Mb MM69 "
     `Mb MM     MM MM   `   MM  MM'   MM MM  MM  MM    MM MM'
      MM MM     MM MM       MM  MM    MM YM.,M9  MMMMMMMM MM
      MM MM     MM MM       MM  MM    MM  YMM9   MM       MM
L    ,M9 YM.   ,M9 MM       MM  MM    MM (M      YM    d9 MM
MYMMMM9   YMMMMM9 _MM_     _MM__MM_  _MM_ YMMMMb. YMMMM9 _MM
                                         6M    Yb
                                         YM.   d9
                                          YMMMM9
""")
