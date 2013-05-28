# predicaments.py
# generates the dictionary that holds all the available predicaments
# also the new home of the Predicament class

import os
from profiledata import profile
 
predicaments = {}

datadir = os.getcwd() + '/data/predicaments'
if not os.path.isdir(datadir):
    raise BadPredicamentError(8)
    #print("error: no data directory")
    #raise SystemExit

class BadPredicamentError(Exception):
    def __init__(self, code=0, *args):
        print("error code:", code)
        if code == 1:
            print("what the hell? i can't find predicament", args[0],
                  "\ndid you modify it while the game was running?")
        elif code == 2:
            print("wrong predicament found:", args[0])
        elif code == 3:
            print("oops! predicament '%s' doesn't exist yet :C" % args[0])
        elif code == 4:
            print("reading %s. %s was not ended correctly." %(args[0], args[1]))
        elif code == 5:
            print("should be busy...", "was the file %s too short?" % args[0])
        elif code == 6:
            print("in", args[0])
        elif code == 7:
            print("didn't find an end of predicament for:", args[0])
        elif code == 8:
            print("no data directory")
        elif code == 9:
            print("%s has inputtype %s, which is insane." %(args[0],args[1]))
        elif code == 10:
            print("'%s' not in profile" % args[0])
        elif code == 11:
            print("unexpected line after", args[0])
        elif code == 12:
            print("unexpected end if in predicament", args[0])
        print("this is a fatal error. aborting")
        raise SystemExit

class Predicament:
    """this is a class for holding a predicament!
when creating a Predicament, pass in a string holding the name. 
the constructor will try to find this pred's data in the datadir
by checking the predicaments dictionary."""

    # class variable, accessible anywhere, shared by instances of Predicament
    numPredicaments = 0

    def __init__(self, name):
        Predicament.numPredicaments += 1
        self.name = name
        self.text = None
        self.setvars = None
        self.disable = None
        self.options = None
        # goto is a list if inputtype = 'normal', a string otherwise 
        self.goto = None
        self.inputtype = None
        self.result = None
        self.prompt = None

        try:
            filename, lineNo = predicaments[self.name]
        except KeyError:
            raise BadPredicamentError(3, self.name)
        busy = False #whether we are currently reading a predicament
        with open(datadir + '/' + filename, 'r') as fp:
            # basically all of this is just to get to the right line and test
            for line in fp:
                # count down to the correct line
                if lineNo > 1:
                    lineNo -= 1
                    continue
                line = line.strip()
                # we know this is the right line, but check anyway!
                if line.find('new predicament') != 0:
                    raise BadPredicamentError(1, self.name)
                # if it's the wrong predicament, freak the hell out
                elif self.name != line.split('=')[1].strip():
                    raise BadPredicamentError(2, self.name)
                busy = True
                break
            if not busy:
                # we should be busy reading a predicament by this point...
                raise BadPredicamentError(5, filename)

            # finally, we start actually assigning the data
            # line should be true (it should still be the new pred line)
            readingIfLevel = 0
            while line:
                line = getNonBlankLine(fp)
                if line.find("end of predicament") == 0:
                    busy = False
                    break
                elif line.find("end if") == 0:
                    if readingIfLevel > 0:
                        readingIfLevel -= 1
                        continue
                    raise BadPredicamentError(12, self.name)
                key, value = line.split('=')
                key = key.rstrip().lower()
                if key == 'new predicament':
                    # we're in a new predicament without closing the last one.
                    # the pred file must be invalid.
                    raise BadPredicamentError(4, filename)
                elif key == 'text':
                    if not self.text:
                        self.text = []
                    # remove only the first space if any. 
                    # leading whitespace is now allowed!
                    if value and value[0] == ' ':
                        value = value[1:]
                    # add each line of text onto the prev line of text
                    self.text.append(value)
                elif key == 'option':
                    if not self.options:
                        self.options = []
                    # we only allow abcdef - 6 options
                    if len(self.options) < 6:
                        self.options.append(value.strip())
                elif key == 'choice':
                    if not self.goto:
                        self.goto = []
                    # we only allow abcdef - 6 choices
                    if len(self.goto) < 6:
                        self.goto.append(value.strip())
                elif key == 'disable':
                    if not self.disable:
                        self.disable = []
                    self.disable.append(value.strip())
                elif key[:3] == 'set':
                    if not self.setvars:
                        self.setvars = []
                    # everything between 'set' and '=' is the parameter
                    # parameter cannot have spaces in it
                    key, parameter = key.split() 
                    # stored as a list of tuples (variable, value)
                    self.setvars.append((parameter.strip(), value.strip()))
                elif key == 'next':
                    self.goto = value.strip()
                elif key == 'inputtype':
                    if value.strip() not in ('none', 'normal', 'input'):
                        print("WHOA! %s is not a chill inputtype!" % value)
                        raise BadPredicamentError(6, self.name)
                    self.inputtype = value.strip()
                elif key == 'result':
                    self.result = value.strip()
                elif key == 'prompt':
                    self.prompt = value.strip()
                elif key[:2] == 'if':
                    parameter = key.split()[1].strip()
                    tempIfLevel = readingIfLevel + 1
                    if doIf(fp, parameter, value.strip()):
                        # if the condition is true, read normally
                        readingIfLevel += 1
                        continue
                    # if the condition isn't true, 
                    # discard lines until we reach end if
                    while readingIfLevel < tempIfLevel:
                        nextline = getNonBlankLine(fp)
                        if nextline[:6] == 'end if':
                            tempIfLevel -= 1
                        elif nextline[:2] == 'if':
                            tempIfLevel += 1
                else:
                    print("%s is not a valid pred directive" % key)
                    raise BadPredicamentError(6, self.name)
        if busy or readingIfLevel:
            raise BadPredicamentError(7, self.name)

    # this isn't used anywhere, but handy for debugging
    def __str__(self):
        return 'Predicament: %s: %s' % (self.name, self.text)

def doIf(fp, parameter, value):
    # figures out whether to read conditional stuff in pred definitions
    if parameter not in profile:
        raise BadPredicamentError(10, parameter)
    followup = getNonBlankLine(fp).lower()
    conditionIsTrue = ( profile[parameter] == value.strip() )
    if followup[:8] == 'then not':
        # don't use this, it breaks if more than one statement is processed
        # for the simplest statements, it's okay. 
        return not conditionIsTrue
    elif followup[:4] == 'then':
        return conditionIsTrue
    line = getNonBlankLine(fp)
    if line[:3] != 'if ':
        raise BadPredicamentError(11, "'%s'" % followup)
    key, value = line.split('=')
    parameter = key.split()[1].strip()
    if followup[:7] == 'and not':
        return ( not doIf(fp, parameter, value) and conditionIsTrue )
    elif followup[:3] == 'and':
        return ( doIf(fp, parameter, value) and conditionIsTrue )
    elif followup[:6] == 'or not':
        return ( not doIf(fp, parameter, value) or conditionIsTrue )
    elif followup[:2] == 'or':
        return ( doIf(fp, parameter, value) or conditionIsTrue )
    raise BadPredicamentError(11, 'if %s = %s' % (parameter, value))

def getNonBlankLine(fp):
    line = fp.readline().strip()
    while line == '' or line[0] == '#':
        line = fp.readline().strip()
    return line

# populate predicaments dictionary with locations of all known predicaments
for filename in os.listdir(datadir):
    basename, ext = os.path.splitext(filename)
    if ext != '.pred':
        print("WARNING: skipping %s/%s%s..." % (datadir, basename, ext))
        continue
    busy = False # whether we're currently reading a predicament
    lineNo = 0
    with open(datadir + '/' + filename, 'r') as fp:
        for line in fp:
            lineNo += 1
            line = line.strip()
            if line.find("new predicament") == 0:
                name = line.split('=')[1]
                # create entry in predicaments dictionary
                # 'title of predicament' : ('which pred file it is in',lineNo)
                name = name.strip()
                predicaments[name] = (filename, lineNo)

if __name__ == '__main__':
    #print("content of", datadir, ": ", os.listdir(datadir))
    #print()
    #print("number of predicaments:", Predicament.numPredicaments)
    print("number of predicaments:", len(predicaments))
    for key in predicaments:
        print(key + ":", predicaments[key])
    raise BadPredicamentError
