import sys
from labot import myLabot
from bus import *

# labotteam
token = 'xoxb-15172632743-gLamDlvhW2B9FbkSIzmzmr9x'
#112labot
#token = 'xoxb-16375038259-HvgL1l7nw4TEGnDmsvUqhAlA'

def main_loop():
    try:
        labot.start()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    labot = myLabot(token)
    main_loop()
