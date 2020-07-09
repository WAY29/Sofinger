'''
@Description: 
@Author: Longlone
@LastEditors  : Longlone
@Date: 2020-01-10 14:14:07
@LastEditTime : 2020-01-10 14:24:26
'''
import sqlite3


n_conn = sqlite3.connect('new_cms_finger.db')
n_cur = n_conn.cursor()
o_conn = sqlite3.connect('old_cms_finger.db')
o_cur = o_conn.cursor()
# 合并cms中的hit
o_data = o_cur.execute('SELECT finger_id, hit from cms').fetchall()
for each in o_data:
    o_id = each[0]
    o_hit = each[1]
    n_data = n_cur.execute('SELECT hit from cms where finger_id=%s' % o_id).fetchone()
    n_hit = n_data[0]
    sql = "UPDATE cms SET hit=%s WHERE finger_id=%s" % (o_hit + n_hit, o_id)
    n_cur.execute(sql)
n_conn.commit()
# 合并fofa中的hit
o_data = o_cur.execute('SELECT id, hit from fofa').fetchall()
for each in o_data:
    o_id = each[0]
    o_hit = each[1]
    n_data = n_cur.execute('SELECT hit from fofa where id=%s' % o_id).fetchone()
    n_hit = n_data[0]
    sql = "UPDATE fofa SET hit=%s WHERE id=%s" % (o_hit + n_hit, o_id)
    n_cur.execute(sql)
n_conn.commit()
# 关闭数据库
n_conn.close()
o_conn.close()