# -*- coding: utf-8 -*-
from trivia_support import *
    

_start = datetime.datetime(2014, 4, 26,2,00)

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



STATIC_PATH= os.path.join(os.path.dirname(__file__),r"static/")


    
application = tornado.web.Application([
	(r"/", IndexHandler, dict(contest_start=_start)),
	(r"/question", Question, dict (answers = answers)),
	(r"/leaderboard",LeaderBoard),
	(r"/winners", WinnersHandler),
	(r"/login/", LoginHandler),
],static_path=STATIC_PATH,login_url=r"/login/", 
 cookie_secret="35wfa35tgtres5wf5yhxbt4"+str(random.randint(0,1000000)))

if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()
    




