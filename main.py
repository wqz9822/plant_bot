import sys
from labot import myLabot

token = 'xoxb-22074170434-gwN94TD4BeKiwq5l2Y51BHjL'

def main_loop():
    try:
        labot.start()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    labot = myLabot(token)
    main_loop()
