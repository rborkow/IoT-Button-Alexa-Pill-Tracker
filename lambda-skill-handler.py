"""
AWS IoT Button + Alexa Skill Pill Tracker
2017 - Robert Borkowski

AWS lambda function for responding to pill tracker requests.

Requires an AWS IoT Button writing events to a DynamoDB instance named 'pillbutton_presses'.

Derived from this sample: http://amzn.to/1LzFrj6
"""

from __future__ import print_function
from time import time
from boto3.dynamodb.conditions import Key
#from datetime import datetime
#from tzlocal import get_localzone

import boto3
import os

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Vitamin Tracker. " \
                    "You can ask me when you last took vitamins by " \
                    "asking when did I last take vitamins?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "You can ask me when you last took vitamins by " \
                    "asking when did I last take vitamins?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Vitamin Tracker. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def check_last_pilltime(intent, session):

    buttonSerialNumber = 'G030JF058236K6GF'

    card_title = intent['name']
    session_attributes = {}
    should_end_session = True

    dynamo = boto3.resource('dynamodb').Table('pillbutton_presses')
    response = dynamo.query(
        KeyConditionExpression=Key('SerialNumber').eq(buttonSerialNumber),
        Limit=1,
        ScanIndexForward=False
    )
    print(response)
    items = response['Items']

    if len(items) == 0:
        speech_output = "Hmm, I don't see any record of you taking vitamins. " \
                        "Try again later."
        reprompt_text = "I'm not sure what you're asking for. "
    else:
        timestamp = items[0]['Timestamp']/1000
        now = int(time())
        print(timestamp)
        print(int(time()))

        diff=now-timestamp
        print(diff)
        hours_ago = int(round(diff/3600, 0))
        if hours_ago <= 2:
            speech_output = "It looks like you took your vitamins pretty recently."
            reprompt_text = "You can ask me when you last took vitamins by " \
                        "asking when did I last take vitamins?"
        else:
            hours_ago = str(hours_ago)
            speech_output = "It looks like you last took your vitamins about " + \
                        hours_ago + \
                        " hours ago."
            reprompt_text = "You can ask me when you last took vitamins by " \
                        "asking when did I last take vitamins?"

        # utc_tz = pytz.timezone('UTC')
        # utc_dt = utc_tz.localize(datetime.utcfromtimestamp(timestamp))
        #
        # sf_tz = pytz.timezone('America/Los_Angeles')
        # sf_dt = sf_tz.normalize(utc_dt.astimezone(sf_tz))

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "HoursAgoIntent":
        return check_last_pilltime(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """

    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
