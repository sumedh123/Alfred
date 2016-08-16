import os
import sys
import requests
import json
from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config.from_pyfile('app.cfg')
db = SQLAlchemy(app)

PAGE_ACCESS_TOKEN = "EAAEMH5yZAxtABAIi5RjBMuW5ttS3kgZCOIM1LM92nZBp6ZAMZCg1NPleNMmKsRfS2Jbb4FrYeXca1knaalZBLJf7UCGj3XfBCZBn5YW1w0ZBkY4zhOZASW5Uf75IMJ0P7gIkPBlfZAnv4sYLi75V4EvZC6maLgvriPfaSB1sgHYXAo1gwZDZD"
VERIFY_TOKEN = "alfred"

class Event(db.Model):
    __tablename__='events'
    id=db.Column(db.Integer,primary_key=True)
    sender_id=db.Column(db.String(100))
    receipt_id=db.Column(db.String(100))
    name=db.Column(db.String(100),default='event')
    date=db.Column(db.DateTime)

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

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    send_message(sender_id, "got it, thanks!")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
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


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
app.run(debug=True)