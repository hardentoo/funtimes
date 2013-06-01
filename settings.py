# settings.py

# this is temporary. find a better way to do it.
# allow the user to set in-game, if possible...
preferredButtons = 'abcdef'
#preferredButtons = '123456'
#preferredButtons = 'aoeujk'

fancyPrintSpeed = 0.015
fancyPrintLineDelay = 0.500

historycache = 10
defaultNonePrompt = '-->'
defaultNormalPrompt = 'What do you want to do?'
defaultInputPrompt = 'Please type something.'


# figure this out later
soundWorks = True

# store terminal settings for restoration on quit()
import sys
import termios
from termios import tcflush, TCIOFLUSH
stdinfd = sys.stdin.fileno()
oldtcattr = termios.tcgetattr(stdinfd)
newtcattr = termios.tcgetattr(stdinfd)

