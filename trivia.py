# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado
import os
import datetime
import calendar
import random


def find_questions():
    files = os.listdir(os.path.dirname(os.path.abspath(__file__)))
    html_files = []
    for f in files:
        if ".html" in f:
            html_files.append(f)
    c = 0
    for f in html_files:
        try:
            int(f[:-5])
            c+=1
        except:
            pass
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
contest_start = datetime.datetime(2014, 4, 26,2,00)

answers = {  #dict to store answers
"1" : "bahrain",
"2": "hephaestus",
"3" : "6.626",       
"4": "war of 1812",
"5" :"neutropenia",  
"6": "answer6", 
"7": "answer7",
"8": "answer8",
"9": "answer9",  
"10": "answer10" }


users = {} #dict that stores user progress

winners = [] # ordered list of winners

finish_times = {} # stores each users personal time to finish 

STATIC_PATH= os.path.join(os.path.dirname(__file__),r"static/")

class BaseHandler(tornado.web.RequestHandler):
        @tornado.web.authenticated
        def get(self):
            self.render("index.html",Now = datetime.datetime.utcnow(), 
            datetime=datetime.datetime,contest_start = contest_start)
        
	def get_current_user(self):
		return self.get_secure_cookie("login")
	def post(self):
	    if datetime.datetime.utcnow() < contest_start:
	        self.write("cheater!")
            else:
                if self.get_secure_cookie("0") == None:
                    
               	    zero_time=datetime.datetime.utcnow()
               	    time = toTStamp(zero_time)
               	    self.set_secure_cookie("0",time,expires_days=2) #stores start time as a cookie which is used to calculate when clues appears
           	
           	self.redirect("/question")
# users are tracked by setting a secure cookie for each user
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
the user dict and the serves the corresponding question to the user.
When the user answers a question the post function checks their answer against 
the answer dict and if right sets a time stamp cookie for the next question and 
changes the users entry in the users dict so the next question will be served.

    """      
    @tornado.web.authenticated
    def get(self):
        user = self.current_user 
        try:
            time = self.get_secure_cookie(str(users[user]))
            
            
        except:
            print user,
            print " has experienced a key error"
            self.redirect("/login/")
            return
        if time == None:
            self.redirect("/")
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
        if answers[str(users[user]+1)] in answer.lower() :
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
    
application = tornado.web.Application([
	(r"/", BaseHandler),
	(r"/question", Question),
	(r"/leaderboard",LeaderBoard),
	(r"/winners", WinnersHandler),
	(r"/login/", LoginHandler),
],static_path=STATIC_PATH,login_url=r"/login/", 
 cookie_secret="35wfa35tgty5wf5yhxbt4"+str(random.randint(0,1000000)))

if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()
    




