
import time
import os
import sys
import requests
import json
from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
import datetime
from datetime import date
import apiai
def main(query,sessionid):
    ai = apiai.ApiAI('13537e5537c543b78b713852b76ff0f3 ')

    request = ai.text_request()

    request.lang = 'en'  # optional, default value equal 'en'

    request.session_id = sessionid

    request.query = query

    response = request.getresponse()
    response=json.loads(response.read())
    print(response)

    send_message(sessionid, response['result']['fulfillment']['speech'])






app=Flask(__name__)
app.config.from_pyfile('app.cfg')
db = SQLAlchemy(app)

PAGE_ACCESS_TOKEN = "EAAYUNKfFZCuABAOLNNzAQxrmgbAqrD1m9DRkB0WrCZB8zOEPyI4ilHyWSvvifXArhEPNkxKT7LiNc4u4s7VL1tltMr9JL6IisLM0VXQrs6OYLeSK28lk5pXdEhod4qiioC6TeJN74NqbmKqQwIBlpbNUmCXvTcPnJSFFjMAwZDZD"
VERIFY_TOKEN = "alfred-svnit"

def short_url(url):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB0N1UrT-OxThltr9Lr1bb1IeCuYma-rro'
    params = json.dumps({'longUrl': url})
    response = requests.post(post_url,params,headers={'Content-Type': 'application/json'})
    response1=json.loads(response.text)
    return response1['id']

class Event(db.Model):
    __tablename__='events'
    id=db.Column(db.Integer,primary_key=True)
    sender_id=db.Column(db.String(100))
    name=db.Column(db.String(100),default='event')
    date=db.Column(db.DateTime)
    reminded=db.Column(db.Boolean,default=False)

class Subscriber(db.Model):
    __tablename_='subscribers'
    id=db.Column(db.Integer,primary_key=True)
    sub_id=db.Column(db.String(100))

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must
    # return the 'hub.challenge' value in the query arguments

    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200

@app.route('/', methods=['POST'])
def webook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message
                    
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass
                if messaging_event.get("optin"):  # optin confirmation
                    pass
                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass
                all_reminders = Event.query.all()
                for i in all_reminders:
                    if i.reminded==False:
                        event_date = i.date
                        nowdate = datetime.datetime.today()
                        e=divmod((event_date-nowdate).days* 86400+ (event_date-nowdate).seconds , 60)
                        if (e[0]<450) and (e[0]>330) :
                            timeleft= (e[0]-330)/60.0
                            hr=timeleft-(timeleft%1)
                            mi=round((timeleft%1)*60,0)
                            senderid = i.sender_id
                            reminder_message = "Sir, you have a " + i.name + " after "+str(hr)+" hours and "+str(mi)+" minutes!"
                            send_message(senderid, reminder_message)
                            i.reminded=True
                            db.session.add(i)
                            db.session.commit()
                        elif e[0]<330:
                            i.reminded=True
                            send_message(i.sender_id,"sir, your "+ i.name +" is over already!")
                            db.session.add(i)
                            db.session.commit()


    return "ok", 200




def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

@app.route('/<message>', methods=['GET','POST'])
def mass(message):
    subs=Subscriber.query.all()
    for user in subs:
        send_message(user.sub_id,message)
    return "ok", 200



def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
