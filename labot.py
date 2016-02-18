import time
import json
from datetime import datetime, timedelta
from eventRetriever import eventRetriever
from camera import myCamera
# from chatterbot import ChatBot
from slackclient import SlackClient
from Adafruit_Thermal import *
from bus import *
import threading

class myTalk(object):
    def __init__(self, mode, user, labot):
        self.mode = mode
        self.user = user
        self.labot = labot
        self.inDetail = False

    def startTalk(self):
        if self.mode == 'hi':
            self.outMsg = 'How are you feeling today?'
            self.choices = ['simple_smile','neutral_face']
        elif self.mode == 'bus':
            self.outMsg = 'Please select:\n1. Go from codeLab\n2. Come to codeLab'
            self.choices = ['one','two']
        elif self.mode == 'lecture':
            self.eventsObj = eventRetriever()
            self.event = self.eventsObj.getUpComingEvent()
            attachment = self.lecture_attachment()
            self.outMsg = 'Here is a lecture for you:'
            outMsg = [self.outMsg, attachment]
            self.choices = ['rewind','fast_forward','information_source','printer']
            return outMsg, self.choices
        return self.outMsg, self.choices

    def continueTalk(self, inMsg):
        if self.mode == 'hi':
            if self.outMsg == 'How are you feeling today?':
                if inMsg == 'simple_smile':
                    self.outMsg = "It is good to hear that."
                    self.choices = []
                elif inMsg =='neutral_face':
                    self.outMsg = "Make yourself happier."
                    self.choices = []
        elif self.mode =='bus':
            if self.outMsg == 'Please select:\n1. Go from codeLab\n2. Come to codeLab':
                if (inMsg == 'one') or ('1' in inMsg):
                    self.outMsg = 'Where is your destination?'
                    self.labot.isListening = True
                    self.labot.talkHandler = self
                    self.choices = []
                elif (inMsg == 'two') or ('2' in inMsg):
                    self.outMsg = 'Where are you now?'
                    self.labot.isListening = True
                    self.labot.talkHandler = self
                    self.choices = []
            elif self.outMsg == 'Where is your destination?':
                message, attachment = self.getBusInfo(inMsg, 'fromCodeLab')
            elif self.outMsg == 'Where are you now?':
                message, attachment = self.getBusInfo(inMsg, 'toCodeLab')
            elif self.outMsg == 'Do you want me to remind you?':
                if inMsg == 'white_check_mark':
                    arrivalTime = self.bus.arrivalTime
                    now = datetime.now()
                    if arrivalTime > now:
                        eta = arrivalTime - now
                        eta = int(eta.seconds)
                        if eta > 180:
                            self.outMsg = 'OK. I will remind you.'
                            self.choices = []
                            remindMsg = 'Your bus is coming! Prepare to go!'
                            busReminder = threading.Timer(eta-180, \
                                          self.labot.sendMessage, [remindMsg])
                            busReminder.start()
                    else:
                        self.outMsg = 'Sorry, the bus has gone.'
                        self.choices = []
                elif inMsg == 'negative_squared_cross_mark':
                    self.outMsg = 'OK. Hope you can catch it.'
                    self.choices = []
        elif self.mode == 'lecture':
            if inMsg == 'rewind':
                self.labot.updateMessage(self.timeStamp, 'previous')
                return None, []
            elif inMsg == 'fast_forward':
                self.labot.updateMessage(self.timeStamp, 'next')
                return None, []
            elif inMsg == 'information_source':
                self.inDetail = not(self.inDetail)
                attachment = self.lecture_attachment()
                self.labot.updateMessage(self.timeStamp, self.outMsg, attachment)
                return None, []
            elif inMsg == 'printer':
                self.outMsg = 'Do you want me to print it?'
                self.choices = ['white_check_mark','negative_squared_cross_mark']
        return self.outMsg, self.choices

    def getBusInfo(self, userAdr, userDir):
        busQuery = myBusQuery(userAdr, userDir)
        result = busQuery.getETA()
        if result is None:
            message = 'Sorry, unable to retrive time.'
            attachment = ''
        else:
            message = 'Here is the bus info:'
            bus, busStop, deltaTime = result
            self.bus = bus
            self.busStop = busStop
            stepA = 'Go to '+ busStop.stopName + ' bus stop.'
            stepB = 'Take ' + bus.busName
            stepC = 'Arriving in ' + deltaTime
            steps = stepA + '\n' + stepB + '\n' + stepC
            attachment = \
            [
                {
                    "text": steps,
                    "color": "#7CD197",
                }
            ]
        return message, json.dumps(attachment)

    def lecture_attachment(self):
        lecture = self.event
        attachment = \
        [
            {
                "title": lecture.title,
                "title_link": lecture.lectureLink,
                "text": '',
                "fields": [
                    {
                        "title": "Lecturer",
                        "value": lecture.lecturer,
                        "short": True
                    },
                    {
                        "title": "Date",
                        "value": lecture.startDate,
                        "short": True
                    },
                    {
                        "title": "Time",
                        "value": lecture.startTime,
                        "short": True
                    },
                    {
                        "title": "Location",
                        "value": lecture.location,
                        "short": True
                    }
                ],
                "color": "#7CD197",
            }
        ]
        if self.inDetail:
            attachment[0]['text'] = lecture.description
            attachment[0]["image_url"] = lecture.imgLink
        return json.dumps(attachment)

    def takeAction(self, inMsg):
        if self.mode == 'bus':
            if self.outMsg == 'Where is your destination?':
                message, attachment = self.getBusInfo(inMsg, 'fromCodeLab')
            elif self.outMsg =='Where are you now?':
                message, attachment = self.getBusInfo(inMsg, 'toCodeLab')
            self.labot.sendMessage(message, attachment)
            self.outMsg = message
            if self.outMsg == 'Here is the bus info:':
                self.outMsg = 'Do you want me to remind you?'
                recipt = self.labot.sendMessage(self.outMsg)
                self.timeStamp = recipt['ts']
                self.choices = ['white_check_mark','negative_squared_cross_mark']
                self.labot.addReaction(self.timeStamp, self.choices)

# This class is cited from python-rtmbot project
class rtmBot(object):
    def __init__(self, token):
        self.last_ping = 0
        self.token = token
        self.botUserName = 'U0F52JLMV' #labotteam
        #self.botUserName = 'U0GB1147M' #112labot
        self.slack_client = None

    def connect(self):
        #Convenience method that creates Server instance
        self.slack_client = SlackClient(self.token)
        self.slack_client.rtm_connect()

    def autoping(self):
        #hardcode the interval to 3 seconds
        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now

    def input(self, data):
        # print(data)
        if "subtype" in data:
            if data['subtype'] == 'message_changed': return
        if "type" in data:
            if data["type"] == 'message':
                self.process_message(data)
            elif data["type"]=='reaction_added' or data["type"]=='reaction_removed':
                self.process_reactions(data)

    # ------------------------Data dispatch  ---------------------------

    # This function is called every time there is a new incomming msg
    def process_message(self, data):
        # print(data)
        # Message must contains the user
        if 'user' not in data: return
        # Only react to message from user
        if data['user'] == self.botUserName: return
        # respond if being @ in a channel or chat through direct message
        if data['channel'].startswith("D") or '@'+self.botUserName in data['text']:
            self.user = data['user']
            self.timeStamp = data['ts']
            self.channel =  data['channel']
            if '@'+self.botUserName in data['text']:
                self.inMsg = data['text'].replace('@'+self.botUserName,'')
            else:
                self.inMsg = data['text']
            if self.isListening:
                self.isListening = False
                self.talkHandler.takeAction(self.inMsg)
            else:
                self.takeAction()
            # print(labot.getChannelHistory())

    # This function is called every time there is a new incomming msg
    def process_reactions(self, data):
        user = data['user']
        timeStamp = data['item']['ts']
        choice = data['reaction']
        if self.talkHandler is None: return
        talkHandler = self.talkHandler
        if (timeStamp == talkHandler.timeStamp) and (user == talkHandler.user) \
                                           and (choice in talkHandler.choices):
            outMsg, choices = talkHandler.continueTalk(choice)
            if outMsg is not None:
                recipt = self.sendMessage(outMsg)
                talkHandler.timeStamp = recipt['ts']
                if len(choices)>0:
                    self.addReaction(talkHandler.timeStamp, choices)
            self.talkHandler = talkHandler

class myLabot(rtmBot):

    def __init__(self, token):
        super().__init__(token)
        self.channel = ''
        self.inMsg = ''
        self.mode = ''
        self.outMsg = ''
        self.attachment = ''
        self.isListening = False
        self.talkHandler = None
        # self.chatbot = ChatBot("Labot",
        # io_adapter="chatterbot.adapters.io.NoOutputAdapter")
        # # Train based on the english corpus
        # self.chatbot.train("chatterbot.corpus.english")

    def start(self):
        self.connect()
        while True:
            for reply in self.slack_client.rtm_read():
                self.input(reply)
            self.autoping()
            time.sleep(.1)

    # ------------------------  Slack API Wrapper  ---------------------------

    def sendMessage(self, outMsg, attachment = ''):
        if type(outMsg) is list:
            if len(outMsg) == 2:
                attachment = outMsg[1]
                outMsg = outMsg[0]
        recipt =  self.slack_client.api_call("chat.postMessage", \
                  channel=self.channel,text=outMsg, as_user=True, \
                  attachments=attachment, parse='full')
        recipt = json.loads(recipt.decode('utf-8'))
        return recipt

    def updateMessage(self, timeStamp, outMsg, attachment = ''):
        recipt =  self.slack_client.api_call("chat.update", ts=timeStamp, \
                  channel=self.channel,text=outMsg, \
                  attachments=attachment, parse='full')
        recipt = json.loads(recipt.decode('utf-8'))
        return recipt

    def getChannelHistory(self):
        if self.channel.startswith("D"):
            history = self.slack_client.api_call("im.history",\
                                                  channel=self.channel,count=1)
        else:
            history = self.slack_client.api_call("channels.history",\
                                                  channel=self.channel,count=1)
        return history

    # Add reaction emoji to a message
    def addReaction(self, timeStamp, choices):
        for choice in choices:
            reaction = self.slack_client.api_call('reactions.add',\
                    channel=self.channel, timestamp = timeStamp, name=choice)

    # ---------------------    Labot behaviour    ----------------------------

    def printInfo(self, text):
        # print('Printing')
        printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)
        printer.upsideDownOn()
        printer.justify('C')
        printer.println(text)
        printer.upsideDownOff()
        printer.feed(2)

    def getMode(self):
        inMsg = self.inMsg.lower()
        mode = ''
        keywords = dict()
        keywords['hi'] = ['hi','hello','what\'s up']
        keywords['picture'] = ['picture','photo']
        keywords['lecture'] = ['lecture','event']
        keywords['bus'] = ['bus','transit']
        keywords['print'] = ['print','note']
        keywords['help'] = ['help','what can you do']
        for keyword in keywords:
            for word in keywords[keyword]:
                if word in inMsg:
                    mode = keyword
        return mode

    def startConversation(self, mode):
        talkHandler = myTalk(mode, self.user, self)
        outMsg, choices = talkHandler.startTalk()
        recipt = self.sendMessage(outMsg)
        timeStamp = recipt['ts']
        if len(choices)>0:
            self.addReaction(timeStamp, choices)
        talkHandler.timeStamp = timeStamp
        self.talkHandler = talkHandler

    def takeAction(self):
        mode = self.getMode()
        if (mode == 'hi'):
            self.startConversation(mode)
        elif mode == 'picture':
            try:
                recipt = self.sendMessage('Sure, just a minute.')
                camera = myCamera()
                shareLink = camera.takePicture(self, recipt['ts'])
                if shareLink != '':
                    outMsg = shareLink
                else:
                    outMsg = 'Unable to generate shareLink.'
                self.sendMessage(outMsg)
            except:
                self.sendMessage('Camera offline.')
        elif mode == 'lecture':
            self.startConversation(mode)
        elif mode == 'print':
            try:
                self.printInfo(self.inMsg.replace('print',''))
            except:
                self.sendMessage('Printer offline.')
        elif mode == 'bus':
            self.startConversation(mode)
        elif mode == 'help':
            message = 'Here are the things that I can do:'
            instrction = 'Any sentence contains the following keywords will triger the actions.\n'
            instrction += '1. *Hello*:  Greeting conversations with me.\n'
            instrction += '2. *Lecture*:  Get upcoming lectures information.\n'
            instrction += '3. *Bus*:  Get bus time between codeLab and your location.\n'
            instrction += '4. *Picture*:  Take a real-time picture of codeLab.\n'
            instrction += '5. *Print*:   Print out your notes on a recipt printer.\n'
            instrction += '6. *Help*:   Display help instrctions.'
            attachment = \
            [
                {
                    "title": 'Manual',
                    "text": instrction,
                    "color": "#7CD197",
                    "mrkdwn_in": ["text"]
                }
            ]
            self.sendMessage(message, json.dumps(attachment))
