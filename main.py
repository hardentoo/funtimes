#!/usr/bin/python3
# main.py
# THIS DOES EVERYTHING!

from collections import deque
import pickle
from sys import argv

from predicaments import Predicament
from funtoolkit import clear, playSound, initialize, anykey
from settings import historycache, soundOn
from profiledata import profile

def main(start='title'):
    initialize()
    # if playSound doesn't work, tell them the game will be mute
    #if not profile['soundWorks']:
    if not playSound and soundOn:
        Predicament('nosound').play()
    currentPredicament = Predicament(start)
    # prevPredicaments is a queue. after each new predicament, append it.
    # it holds past Predicaments. it does not hold strings
    prevPredicaments = deque(maxlen=historycache)
    while True:
        nextPredicament = currentPredicament.play()
        if nextPredicament == currentPredicament.name:
            # if this is the same predicament, play it again
            continue
        elif nextPredicament == '\x7F':
            # go back to last predicament
            try:
                currentPredicament = prevPredicaments.pop()
            except IndexError:
                clear()
                anykey("no history available.")
            continue
        # store this predicament on the list of previous predicaments 
        prevPredicaments.append(currentPredicament)
        currentPredicament = Predicament(nextPredicament)

if __name__ == '__main__':
    if len(argv) > 1:
        for predicament in argv[1:]:
            main(predicament)
    else:
        main()
