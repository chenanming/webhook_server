from flask import Flask, request
import time
import json
import threading
import pymysql
import requests

app = Flask(__name__)

# 建立python与mysql之间的连接
mydb = pymysql.connect(
	host="127.0.0.1",
	user="root",
	passwd="xxxxxxxxx",
	database="test_jiradingtalk"
)

mycursor = mydb.cursor()
#mydb.close()


appkey = 'dingpq59rv5qcijk6fqo'
appsecret = 'xu-AqD0VTDgO98ueuT1XIOVj153TYQXxxOb1Xuz-_EiZnrFydMVSOuVxcUPsc2Io'
headers = {"Charset":"UTF-8", "Content-Type":"application/json"}
mycursor.execute("SELECT access_token FROM dingtalk_token where id = 1 and errmsg = 'ok' ")
access_token = mycursor.fetchone()


# 获取部门列表
def getDepartmentList():
	url = 'https://oapi.dingtalk.com/department/list?access_token=%s' % access_token
	department = requests.get(url, headers=headers)
	deptid = department.json()
	print (deptid)


# 指定部门id，获取该部门成员
def getDepartmentMemberList():
	url = "https://oapi.dingtalk.com/user/simplelist?access_token=%s&department_id=65443532" % access_token
	users = requests.get(url, headers=headers)
	print (users.json())

'''
	sql = "INSERT INTO userid_list (user_name, userid) VALUES (%s, %s)"
	b = mycursor.execute(sql, (users.json()['userlist'][1]['name'], users.json()['userlist'][1]['userid']))
	print (mycursor.rowcount, "userid:插入成功")
	mydb.commit()
'''


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
	if request.method == 'POST':
		changelog = request.form.get('changelog')
		issue_type = request.form.get('issue_event_type_name')
		user_id = request.form.get('user_id')
		user = request.form.get('user')
		issue = request.form.get('issue')
		user_key = request.form.get('user_key')
		webhookEvent = request.form.get('webhookEvent')
		timestamp = request.form.get('timestamp')


	'''
	sql = "SELECT userid FROM userid_list where user = %s"
	mycursor.execute(sql, user_id)
	userid = mycursor.fetchone()
	userid = userid[0]
	'''
	userid = '023236044237724141'

	text = ("JIRA: %s \n人员: %s \n归属: %s \n类型: %s \n项目: %s \n概要: %s \n点击查看: %s \n服务器时间:" % (webhookEvent, user_key, user_id, issue_type, user, issue, changelog, timestamp))
	payload = {
	'agent_id':'230638603',
	'userid_list': userid, 
	'to_all_user':'false',
	'msg':{
	'msgtype':'text',
	'text':{
	'content':text
	}
	}
	}

	# 向指定用户发送普通文本信息
	url = 'https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token=%s' % access_token
	message = requests.post(url, json=payload, headers=headers)
#	print (message.json())



if __name__ == '__main__':
#	getDepartmentList()
#	getDepartmentMemberList()
	app.run()
