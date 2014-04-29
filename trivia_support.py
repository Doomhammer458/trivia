# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado
import os
import datetime
import calendar
import random

users = {} #dict that stores user progress

winners = [] # ordered list of winners

finish_times = {} # stores each users personal time to finish 

def find_questions():
    files = os.listdir(os.path.dirname(os.path.abspath(__file__)))
    html_files = []
    for f in files:
        if ".html" in f:
            html_files.append(f)
    c = 0
    question_nums = []
    for f in html_files:
        try:
            question_nums.append(int(f[:-5]))
            c+=1
        except:
            pass
    if c == 0:
        raise Exception("No questions found")
    if sum(question_nums) != sum(range(1,c+1)):
        raise Exception("Missing questions. Question numbers should be sequential")
    return c
        
    
def Timestamp(_datetime): 
    return calendar.timegm(_datetime.timetuple())

def toTStamp(DATETIME):
        stamp = Timestamp(DATETIME)
        stamp = str(stamp)
        return stamp
def fromTStamp(stamp):
    date = datetime.datetime.utcfromtimestamp(float(stamp))
    return date
num_questions = find_questions() # number of HTML files 
# all date time objects are UTC objects
class BaseHandler(tornado.web.RequestHandler):

        @tornado.web.authenticated
        def get(self):
            self.render("index.html",Now = datetime.datetime.utcnow(), 
            datetime=datetime.datetime,contest_start = self.contest_start)
        
	def get_current_user(self): 
	   return self.get_secure_cookie("login")
	def post(self):
	    if datetime.datetime.utcnow() < self.contest_start:
	        self.write("cheater!")
            else:
                if self.get_secure_cookie("0") == None:
                    
               	    zero_time=datetime.datetime.utcnow()
               	    time = toTStamp(zero_time)
               	    self.set_secure_cookie("0",time,expires_days=2) #stores start time as a cookie which is used to calculate when clues appears
           	
           	self.redirect("/question")
# users are tracked by setting a secure cookie for each user
class IndexHandler(BaseHandler):
        def initialize(self, contest_start):
            self.contest_start = contest_start
class LoginHandler(BaseHandler):
	def get(self):
		self.render("login.html")
	def post(self):
	

	        
            user = self.get_argument("user")
            global users
            users[user] = 0
        
            self.set_secure_cookie("login",user,expires_days=5)
            self.redirect("/")

class LeaderBoard(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("leaderboard.html", users=users)
class WinnersHandler(BaseHandler):
    def get(self):
        self.render("winners.html", winners = winners, time=finish_times)

                
class Question(BaseHandler):

    """   
user progress is tracked by the user dict. For each question the handler checks
the user dict and then serves the corresponding question to the user.
When the user answers a question the post function checks their answer against 
the answer dict and if right, sets a time stamp cookie for the next question and 
changes the users entry in the users dict so the next question will be served.

    """      
    @tornado.web.authenticated
    def initialize(self, answers):
        self.answers = answers
    def get(self):
      
        user = self.current_user 
       
        try:
            time = self.get_secure_cookie(str(users[user]))
            if time == None:
                self.redirect("/")
                return
            
        except:
            print user,
            print " has experienced a key error"
            self.redirect("/login/")
            return
        
        start = fromTStamp(time)
        if users[user] == num_questions:

            self.redirect("/winners")
            return
        htmlPage = str(users[user]+1) +".html"
        self.render(htmlPage,time=start,Now = datetime.datetime.utcnow(),
        timedelta = datetime.timedelta)
        
    def post(self):
        answer = self.get_argument("answer")
        user = self.current_user
        if self.answers[str(users[user]+1)].lower() in answer.lower() :
            time=datetime.datetime.utcnow()
	    time = toTStamp(time)
	    self.set_secure_cookie(str(users[user]+1),time,expires_days=2)
            users[user] += 1
	 
            if users[user]==num_questions:
                global winners
                winners.append(user)
                global finish_times
                start_time = fromTStamp(self.get_secure_cookie("0"))
                end_time = datetime.datetime.utcnow()
                finish_time = end_time - start_time
                finish_times[user] = finish_time
                self.redirect("/winners")
                return
        self.redirect("/question")