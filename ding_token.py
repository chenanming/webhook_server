#!/usr/bin/python3
# -*- coding: UTF-8 -*-
'''
1.与钉钉建立连接
	→获取钉钉Access_Token(企业应用ID，corpSecret管理列表下面 企业应用的凭证密钥)

2.	→获取钉钉部门列表信息(使用Access_Token)
	→获取钉钉指定部门的全部成员信息，写入文件里
	→向指定用户发送企业通知消息（）

3.钉钉发送消息流程
    →retrofit请求
    →添加必要的request信息
    →获取部门列表季各部门下的成员信息
    →发送钉钉消息（指定成员）
'''
import time
import requests
import pymysql


# 建立python与mysql之间的连接
mydb = pymysql.connect(
	host="127.0.0.1",
	user="root",
	passwd="xxxxxxxx",
	database="xxxxxx"
)
mycursor = mydb.cursor()
appkey = 'xxxxxxxxx'
appsecret = 'xxxxxxxxxxxx'


department_list = []
# 查询所有部门的id
mycursor.execute("SELECT department_id FROM department_list")
department_id = mycursor.fetchall()
for i in department_id:
	department_list.append(i[0])
department_list = ",".join(department_list)
print(department_list)


# 获取钉钉Access_Token
def getAccessToken():
	url = "https://oapi.dingtalk.com/gettoken?corpid=%s&corpsecret=%s" % (appkey, appsecret)
	headers = {"Charset":"UTF-8", "Content-Type":"application/json"}
	r = requests.get(url, headers=headers)
	print (r.json())

	# 更新数据库中的access_token
	sql = "UPDATE dingtalk_token SET access_token = %s WHERE id = 1"
	try:
		mycursor.execute(sql, (r.json()['access_token']))
		mydb.commit()
	except:
		mydb.rollback()
	print(mycursor.rowcount, "access_token:更新成功")
#	print('更新时间：',time.time())

if __name__ == '__main__':
	getAccessToken()
