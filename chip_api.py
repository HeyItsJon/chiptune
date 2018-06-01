"""

TO DO:
- error check config file
- error check song file
- error check wave/envelope/pitch files

"""

import chiptune4
import sys

configfile = 'config.txt'
# or do this...
#configfile = sys.argv[1] + '.txt'

# open configuration file and split it into sections
f = open(configfile)
g = f.read().split('#')

# parse config file
# TODO: error check config file - check all arguments are present, etc

# SONG settings
settings = {}  # empty dictionary
for s in g[1].split('\n'):
    if s == '':
        continue
    sp = s.split('=')
    if len(sp) == 1:
        settings['name'] = sp[0]
    else:
        settings[sp[0]] = sp[1]  
c = chiptune4.Chiptune(**settings)

# INSTRUMENT settings
settings = {}   # reset the dictionary
for s in g[2:]:
    settings = {}   # reset the dictionary
    for i in s.split('\n'):
        if i == '':
            continue
        isp = i.split('=')
        if len(isp) == 1:
            settings['name'] = isp[0]
        else:
            settings[isp[0]] = isp[1]
    c.make_instrument(**settings)

# cleanup
del settings
del g
f.close()

#c.output()

c.make_song()

# error check song file?
# error check wave table, envelop and pitch table files
#   - envelope and pitchtable:
#       - check ':' on lines by themselves
#       - make sure there are exactly two ':' symbols
#       - check for timedivision on first line (value can be blank)
#       - make sure every value is a number or ':'
# song file format TBD
# start song creation

# https://pythontips.com/2013/08/04/args-and-kwargs-in-python-explained/



