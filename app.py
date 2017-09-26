#Python libraries that we need to import for our bot
import requests
from flask import Flask, request, redirect, render_template, request, session, abort
from pymessenger.bot import Bot
from pymessenger import Element, Button
from random import randint
import os
import sys
import json
import csv

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
access_token = ACCESS_TOKEN
verify_token = VERIFY_TOKEN
bot = Bot (access_token)

#We will receive messages that Facebook sends to our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            #Facebook Messenger ID for user so we know where to send response back to
            recipient_id = message['sender']['id']

            if message.get('message'):
                #if user just sends us a regular text message
                if message['message'].get('text'):
                    response_sent_text = get_message()
                    send_message_user = send_message(recipient_id, response_sent_text)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message_user = send_message(recipient_id, esponse_sent_nontext)
            else:
                pass
    return "success"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == verify_token:
        return request.args.get("hub.challenge")
    else:
        return 'Invalid verification token'

#opens a csv file from https://github.com/wessilfie/Black-Girl-Magic-Bot/blob/master/magic_csv/blackgirlmagicCSV.csv 
# and chooses one randomly
def get_message():
    with open('./magic_csv/blackgirlmagicCSV.csv', 'r') as csvfile:
        magiccsv = list(csv.reader(csvfile)) 
    lengthofcsv = len(magiccsv)
    position = randint(0, lengthofcsv)
    response = magiccsv[position][0]
    #return selected item to the user
    return response 

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    """since some of our response types are not text, we try to send it as an image
    If we send the text to Facebook and the image fails, we simply send the user a text message with
    just the link from our file"""
    try:
        response_nontext = bot.send_image_url(recipient_id, response)
        if "error" in response_nontext:
            b = bot.send_text_message(recipient_id, response)
    except:
        response_text = bot.send_text_message(recipient_id, response)
    #return a message stating that the message was sent
    return "success"

@app.route("/privacypolicy", methods=['GET', 'POST'])
def privacy():
    return render_template('privacy.html')

if __name__ == "__main__":
    app.run()