import requests
import argparse
import os
import re
import json
import datetime
from random import *
import pycurl
import re
from io import BytesIO
from bs4 import BeautifulSoup
try:
    # python 3
    from urllib.parse import urlencode
except ImportError:
    # python 2
    from urllib import urlencode
# construct the argument parser and parse the arguments
import smtplib
from email.mime.text import MIMEText
 

ap = argparse.ArgumentParser()
ap.add_argument("-e", "--email", required=True,
    help="email")

ap.add_argument("-p", "--password", required=True,
    help="password")

ap.add_argument("-d", "--date", required=True,
    help="date")

args = vars(ap.parse_args())

API_HOST = 'http://member.bodycodi.com/'
HEADERS = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8', 'User-Agent': 'A', 'Referer': 'http://member.bodycodi.com/reservation/classReservationFinal','Origin': 'http://member.bodycodi.com'}
HEADERS_PYCURL = ['Content-Type: application/x-www-form-urlencoded']

def req(path, query, method, data={},
	headers={}):
    url = API_HOST + path
    print('HTTP Method: %s' % method)
    print('Request URL: %s' % url)
    print('Headers: %s' % headers)
    print('QueryString: %s' % query)
    print('Data: %s' %data)

    if method == 'GET':
        return requests.get(url, headers=headers, params = query)
    else:
        return requests.post(url, headers=headers, data=data)

def login(email, password):
	url = 'signMember/signIn'
	data = {'email': email, 'password': password}
	resp = req(url,'', 'POST',data, headers = HEADERS)
	HEADERS_PYCURL.append('Cookie:'+resp.headers['Set-Cookie'])
	HEADERS['Cookie'] = resp.headers['Set-Cookie']
	return resp

def getClassList(seqPartnerClass, seqPartnerProduct, seqPartnerProductPass, seqPartnerPayment, targetDate):
	url = 'reservation/ajax/getAvailableClassScheduleForSelectedDay'
	query = {
			'seqPartnerClass': seqPartnerClass, 
			'seqPartnerProduct': seqPartnerProduct, 
			'seqPartnerProductPass': seqPartnerProductPass, 
			'seqPartnerPayment': seqPartnerPayment,
			 'targetDate': targetDate
	}

	resp = req(url, query, 'GET', headers = HEADERS)
	return resp

def checkReservation():
	url = 'reservation/classReservationComplete'
	resp = req(url, '', 'GET', headers = HEADERS)
	pattern = re.compile('var reservationResult = (.*?);')
	soup = BeautifulSoup(resp.text,features="html.parser")
	for script in soup.find_all("script", {"src":False}):
		if script:
			m = pattern.search(script.string)
			if m:
				print(m.group(1))
				if m.group(1) == '-983' :
					break
	return resp

def selectMySchedule(seqPartner):
	url = 'myPage/ajax/selectMyProduct'
	data = {'seqPartner': seqPartner}
	resp = req(url, '', 'POST', data, headers = HEADERS)
	print("response status:\n%d" % resp.status_code)
	print("response headers:\n%s" % resp.headers)
	return resp

def getMyInfo(seqPartner):
	select_place_url = 'myPage/myReservation'
	mydata_url = 'myPage/ajax/selectMyProduct'
	query = {'seqPartner': seqPartner}
	data = {'seqPartner': seqPartner}
	resp = req(select_place_url, query, 'GET', headers = HEADERS)
	resp = req(mydata_url, '', 'POST', data, headers = HEADERS)
	return resp.json()

def classReservation(data):
	b = BytesIO()
	postfields = urlencode(data)
	c = pycurl.Curl()
	c.setopt(c.URL, 'http://member.bodycodi.com/reservation/classReservationFinal')
	c.setopt(c.POST, True)
	c.setopt(c.SSL_VERIFYPEER, False)
	c.setopt(pycurl.HTTPHEADER, HEADERS_PYCURL)
	c.setopt(pycurl.POSTFIELDS, postfields)
	c.setopt(c.HEADERFUNCTION, b.write)
	c.perform()
	print('Status: %d' % c.getinfo(c.RESPONSE_CODE))
	print('TOTAL_TIME: %f' % c.getinfo(c.TOTAL_TIME))
	c.close()
	body = b.getvalue().decode("utf-8")
	return body


if __name__ == '__main__':
	param = {}
	login(args['email'], args['password'])
	date = re.search(r'\d{4}-\d{2}-\d{2}', args['date']).group()
	hour = re.search(r'\d{2}:\d{2}', args['date']).group()

	data = getMyInfo('66')
	data = data[0]
	param['seq_member'] = data['SEQ_MEMBER']
	param['seq_partner'] = data['SEQ_PARTNER']
	param['seq_partner_product'] = data['SEQ_PARTNER_PRODUCT']
	param['seq_partner_product_pass'] = data['SEQ_PARTNER_PRODUCT_PASS']
	param['seq_partner_class'] = data['SEQ_PARTNER_CLASS']
	param['pass_name'] = data['PASS_NAME']
	param['service_type'] = data['SERVICE_TYPE']
	param['seq_partner_payment'] = data['SEQ_PARTNER_PAYMENT']
	param['use_start_dt'] = data['USE_START_DT']
	param['use_end_dt'] = data['USE_END_DT']
	param['use_number'] = data['USE_NUMBER']
	param['basic_number'] = data['BASIC_NUMBER']
	param['remain_days'] = data['REMAIN_DAYS']
	
	data = getClassList(
		param['seq_partner_class'],
		param['seq_partner_product'],
		param['seq_partner_product_pass'],
		param['seq_partner_payment'], date)

	for row in data.json():
		if row['START_DATE'] == args['date']:
			param['lesson_name'] = row['LESSON_NAME']
			param['class_time'] = row['CLASS_NAME']
			param['coach_name'] = row['COACH_NAME']
			param['seq_partner_coach'] = row['SEQ_PARTNER_COACH']
			param['reservation_use_start_dt'] = row['START_DATE']
			param['reservation_use_end_dt'] = row['END_DATE']
			param['seq_partner_class'] = row['SEQ_CLASS']
			param['seq_partner_class_schedule'] = row['SEQ_CLASS_SCHEDULE']
			param['update_flag'] = ''
			param['schedule_id'] = round(random() * datetime.datetime.now().microsecond)
	print('now:', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	classReservation(param)
	checkReservation()






