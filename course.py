
import requests,time,json
import threading
from io import StringIO
from bs4 import BeautifulSoup

course_url_prefix = "http://xkfw.xjtu.edu.cn/xsxk/elect.xk?method=handleZxxk&jxbid=20142"
course_url_suffix = "&xklx=3&xkzy=3&ysJxbid="
index_url = 'http://xkfw.xjtu.edu.cn/xsxk/index.xk'
login_url = 'https://cas.xjtu.edu.cn/login'
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36'}

def init():
	global username,password,course_name,thread_number,timeout,status
	status = {}
	config_file = open("course_config.json",'r')
	config = json.load(config_file)
	username = config['username']
	password = config['password']
	course_name = config['course']
	thread_number = config['thread_number']
	for i in range(len(course_name)) :
		course_name[i] = course_name[i].split('-')[0] + "00-0" + course_name[i].split('-')[1]
		status[course_name[i]] = False
	print(course_name)
	timeout = config['timeout']
	
def login():
	global sec
	init()
	sec = requests.session()
	# s = requests.session()
	#Get Login Ticket
	res = sec.get(login_url)

	soup = BeautifulSoup(res.text)
	lt = str(soup.find_all("input",attrs={"name":"lt"})).split('"')[5]
	ex = str(soup.find_all("input",attrs={"name":"execution"})).split('"')[5]
	form_data = {'username':username,
				'password':password,
				'code':'',
				'lt':lt,
				'execution':ex,
				'_eventId':'submit',
				'submit':'登陆'}
	res_get = sec.post(login_url,data = form_data,headers = header)
	#Get Cookies
	res_get_index = sec.get(index_url)
	f = open("out.html","w",encoding='utf-8')
	f.write(res_get.text)
	print("Login Successfully")

class timer(threading.Thread):
	def __init__(self,no,course_number):
		threading.Thread.__init__(self)
		self.no = no
		self.course_number = course_number
		self.thread_stop = False
	def run(self):
		global status
		while(status[self.course_number] == False) :
			if(status[self.course_number] == True) :
				stop()
			res_tar  = sec.get(course_url_prefix + self.course_number + course_url_suffix)
			if(res_tar.json()['success'] == True) :
				status[self.course_number] = True
				print(self.course_number + " " + "thread "+ str(self.no)  + ' ' + "课程已选中！")
			else :
				print(self.course_number + " " + "thread "+ str(self.no)  + ' ' + json.load(StringIO(res_tar.text))['message'])
			time.sleep(timeout)		
	def stop(self):
		self.thread_stop = True

login()
thread_count = 0
thread = {}
for w in course_name :
	for i in range(thread_number) :
		timer(thread_count,w).start()
		thread_count += 1
		time.sleep(1)
