Plant-bot
=============
A Slack bot program written in python3 that connects via the [Slack RTM API](https://api.slack.com/rtm).

Features
----------
1. Interactive dialogue system utilizing Slack reaction feature.
2. Provide sensors data from Arduino.
3. Take real-time photos of the plants from Raspberry Pi.
    
Build Environment
-----------
* Ubuntu 14.04.3 LTS
* Python 3.4.3

Dependencies
----------
* [websocket-client](https://pypi.python.org/pypi/websocket-client/)
* [python-slackclient](https://github.com/slackhq/python-slackclient)

Installation
-----------
1. Create a virtualenv

       virtualenv -p python3 slackbot

2. Activate the virtualenv

       cd slackbot
       source bin/activate

3. Install dependencies

       pip install -r requirements.txt

4. Update your bot's [token](https://api.slack.com/bot-users) in main.py

5. Run main program
    
       python main.py