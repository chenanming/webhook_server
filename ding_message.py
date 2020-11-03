#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from flask import Flask, request
import json
import time
import datetime
import pymysql
import requests


app = Flask(__name__)

# 建立python与mysql之间的连接
mydb = pymysql.connect(
	host="127.0.0.1",
	user="root",
	passwd="xxxxxxxxxxxx",
	database="xxxxxxxxxxxx"
)
mycursor = mydb.cursor()
headers = {"Charset":"UTF-8", "Content-Type":"application/json"}
mycursor.execute("SELECT access_token FROM dingtalk_token where id = 1 and errmsg = 'ok' ")
access_token = mycursor.fetchone()
#print(access_token)


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
	participant_list = []
	userid_list = []

	request_data = request.get_data().decode('utf-8')  # 对原始数据进行编码，不然中文可能出不来
	data = json.loads(request_data)
	try:
		key = data['issue']['key'] #任务id
		webhookEvent = data['webhookEvent']  #提交类型
		project_key = data['issue']['fields']['project']['key']  #项目key
		summary = data['issue']['fields']['summary']  #任务概要
		issuetype = data['issue']['fields']['issuetype']['name'] #类型
		tostring = data['issue']['fields']['status']['name']  #任务更新后状态
		fromstring = data['changelog']['items'][-1]['fromString']  #任务更新前状态
		updated = data['issue']['fields']['updated']  #任务更新时间
		user = data['user']['displayName']  #操作人
		creator = data['issue']['fields']['creator']['displayName']  #创建人
		reporter = data['issue']['fields']['reporter']['displayName']  #报告人
		assignee = data['issue']['fields']['assignee']['displayName']  #经办人名字
		participant = data['issue']['fields']['customfield_10102']  #参与人

		# 过滤出参与人的名字 “displayName”字段, 写入participant_list列表
		if participant is None:
			pass
		else:
			for item in participant:
				for key in item.keys():
					if key == 'displayName':
						participant_list.append(item[key])

		issue_key = "http://jira.ad6755.com:8889/browse/%s" % key  # 拼接任务链接
		dt = datetime.datetime.strptime(updated,'%Y-%m-%dT%H:%M:%S.%f%z')
		updated_time = datetime.datetime.strftime(dt, '%Y-%m-%d %H:%M:%S')  # 格式化服务器时间 “xx-xx-xx 00:00:00:00”

		# 通过部门id，查询出各项目的负责人
		if project_key == 'YSG':
			mycursor.execute("SELECT b.user_name FROM department_list a, userid_list b WHERE a.department_id = b.department_id AND b.department_id in ('65457446', '43584425', '65490301', '65454442')")
			project_user = mycursor.fetchall()
		else:
			mycursor.execute("SELECT b.user_name FROM department_list a, userid_list b WHERE a.department_id = b.department_id AND b.department_id in ('71556244', '43584425', '65490301', '65454442')")
			project_user = mycursor.fetchall()

		if participant is None:			
			sql = "SELECT userid FROM userid_list where user_name = %s or user_name = %s or user_name = %s or user_name = %s or user_name in %s"
			username_list = (user, creator, reporter, assignee, project_user)
		else:
			sql = "SELECT userid FROM userid_list where user_name = %s or user_name = %s or user_name = %s or user_name = %s or user_name in %s or user_name in %s"
			username_list = (user, creator, reporter, assignee, project_user, participant_list)

		mycursor.execute(sql, username_list)
		userid = mycursor.fetchall()
		for i in userid:
			userid_list.append(i[0])
		userid_list = ",".join(userid_list)
	except TypeError:
		raise

	text = ("#### 概要：[%s](%s)  \n  类型：%s  \n  经办人：%s  \n  状态变更：%s将任务由[%s]改为[%s]  \n  更新时间：%s" % (summary, issue_key, issuetype, assignee, user, fromstring, tostring, updated_time))
	payload = {
	'agent_id':'230638603',
	'userid_list': userid_list, 
	'to_all_user':'false',
	'msg':{
	'msgtype':'markdown',
	'markdown':{
	'title':"jira工作消息通知：",
	'text': text
	}
	}
	}

	# 向指定用户发送markdown文本信息
	url = 'https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token=%s' % access_token
	message = requests.post(url, json=payload, headers=headers)
	return 'message'


if __name__ == '__main__':
	app.run(host='0.0.0.0', port='8999')
