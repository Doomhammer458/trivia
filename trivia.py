# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado
import os
import datetime
import calendar
import random

# all date time objects are UTC objects
contest_start = datetime.datetime(2014, 4, 26,2,00) # year, month , day , hour, minute

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



num_prizes = 20
runner_up_prize = 1000
prizes = [20000,10000,5000] #first second and third place

#if setting up a contest, there is no need to modify anything below this comment



user_data= {} #master dict of user data
user_data["users"] = {} #dict that stores user progress
user_data["winners"] = [] # ordered list of winners
user_data["finish"] = {} # stores each users personal time to finish 
user_data["question_times"] = {}
user_data["last_answer"] = {}

for i in range(num_prizes - 3):  #runners up
    prizes.append(runner_up_prize)

STATIC_PATH= os.path.join(os.path.dirname(__file__),r"static/")
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
def sum_time_deltas(delta_dict):
    total = datetime.timedelta(seconds = 0)
    for  key in delta_dict.keys():
        total += delta_dict[key]
    return total
    
def Timestamp(_datetime): 
    return calendar.timegm(_datetime.timetuple())

def toTStamp(DATETIME):
        stamp = Timestamp(DATETIME)
        stamp = str(stamp)
        return stamp
def fromTStamp(stamp):
    date = datetime.datetime.utcfromtimestamp(float(stamp))
    return date
def time_per_question(handler,num_questions):
    times = {}
    for i in range(num_questions-1):
        start = fromTStamp(handler.get_secure_cookie(str(i)))
        end = fromTStamp(handler.get_secure_cookie(str(i+1)))
        times[str(i+1)] =  end-start
    
    return times   
def sort_users(user_dict, num_questions):
    sort_list = []
    c = num_questions +1
    for i in range(c):
        for user in user_dict.keys():
            if user_dict[user]== c-i-1:
                sort_list.append(user) 
        
    return sort_list
    
    
    
num_questions = find_questions() # number of HTML files 



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
            global user_data
            user_data["users"][user] = 0
            user_data["last_answer"][user] = datetime.datetime.utcnow()
            self.set_secure_cookie("login",user,expires_days=5)
            self.redirect("/")

class LeaderBoard(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("leaderboard.html", users=user_data["users"],
        sorted_users = sort_users(user_data["users"],num_questions))
class WinnersHandler(BaseHandler):
    def get(self):
        self.render("winners.html", winners = user_data["winners"], time=user_data["finish"])

                
class Question(BaseHandler):
    """   
user progress is tracked by the user dict. For each question the handler checks
the user dict and then serves the corresponding question to the user.
When the user answers a question the post function checks their answer against 
the answer dict and if right, sets a time stamp cookie for the next question and 
changes the users entry in the users dict so the next question will be served.

    """      
    @tornado.web.authenticated
    def get(self):
        user = self.current_user 
        try:
            time = self.get_secure_cookie(str(user_data["users"][user]))
            
            
        except:
            print user,
            print " has experienced a key error"
            self.redirect("/login/")
            return
        if time == None:
            self.redirect("/")
            return
        start = fromTStamp(time)
        if user_data["users"][user] == num_questions:

            self.redirect("/winners")
            return
        htmlPage = str(user_data["users"][user]+1) +".html"
        self.render(htmlPage,time=start,Now = datetime.datetime.utcnow(),
        timedelta = datetime.timedelta)
        
    def post(self):
        global user_data
        user = self.current_user
        answer = self.get_argument("answer")
        
        if len(answer) > 30:
            self.write('<head><meta HTTP-EQUIV="REFRESH" content="10"; url="/question"> </head> \
            <body>Please enter 1 answer at a time. </body>')
            return
        if  datetime.datetime.utcnow()- user_data["last_answer"][user] < datetime.timedelta(seconds=2):
            self.write('<head><meta HTTP-EQUIV="REFRESH" content="5"; url="/question"> </head> \
            <body>Answers are  limited to 1 answer every 2 seconds. </body>')
            return
        
        
        if answers[str(user_data["users"][user]+1)].lower() in answer.lower() :
            time=datetime.datetime.utcnow()
	    time = toTStamp(time)
	    self.set_secure_cookie(str(user_data["users"][user]+1),time,expires_days=2)
            user_data["users"][user] += 1
	 
            if user_data["users"][user]==num_questions:
                
                user_data["winners"].append(user)
                q_time = time_per_question(self,num_questions)
                end_time = datetime.datetime.utcnow()
                finish_time = end_time - contest_start
                user_data["finish"][user] = finish_time
                q_time[str(num_questions)]= end_time - fromTStamp(self.get_secure_cookie(str(num_questions-1)))
                time_sum = sum_time_deltas(q_time)
                q_time["total"] = time_sum
                user_data["question_times"][user]= q_time
                self.redirect("/winners")
                return
                
        user_data["last_answer"][user] = datetime.datetime.utcnow()
        self.redirect("/question")
class UserHandler(BaseHandler):
    def get(self):
        user = self.get_argument("user")
        self.render("users.html",user = user,  num_q=num_questions,
        times = user_data["question_times"][user])
        
class PrizeHandler(BaseHandler):
    
    def get(self):
        self.render("prizes.html", winners = user_data["winners"], prizes = prizes)
application = tornado.web.Application([
	(r"/", BaseHandler),
	(r"/question", Question),
	(r"/leaderboard",LeaderBoard),
	(r"/winners", WinnersHandler),
	(r"/users", UserHandler),
	(r"/prizes", PrizeHandler),
	(r"/login/", LoginHandler),
],static_path=STATIC_PATH,login_url=r"/login/", #debug=True,
 cookie_secret="35wfa35tgtres5wf5tyhxbt4"+str(random.randint(0,1000000)))

if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()
    




