"""

Quick little script to make basic ADSR envelops

"""
sample_rate = 44100 # CHANGE THIS IF YOU WANT TO USE A DIFFERENT SAMPLE RATE

name = input('Envelop name: ') + '.vol'

#td = int(input('Time division (in ms): '))

attack = int(input('Attack (in ms): ')) / 1000.0
if attack < 0:
    print('Error! Attack must be positive!')
    quit()
    
decay = int(input('Decay (in ms): ')) / 1000.0
if decay < 0:
    print('Error! Decay must be positive!')
    quit()
    
sustain = int(input('Sustain value (0-100): ')) / 100.0
if sustain > 1 or sustain < 0:
    print('Error! Sustain must be between 0 and 100!')
    quit()
    
release = int(input('Release (in ms): ')) / 1000.0
if release < 0:
    print('Error! Release must be positive!')
    quit()
    
# create envelop
f = open('envelope/' + name, 'w')

## time division
#if td == 0:
#    td = 1000 / 44100.0
#    f.write('timedivision=0\n')
#else:
#    f.write('timedivision=' + str(td) + '\n')

# attack
rise = 1
run = sample_rate * attack
#run = attack / td
m = rise / run
for x in range(0, int(run)):
    y = m * x
    tmp = '%.4f' % y
    f.write(tmp + '\n')
    
# decay
rise = sustain - 1
run = sample_rate * decay
#run = decay / td
m = rise / run
b = 1
for x in range(0, int(run)):
    y = m * x + b
    tmp = '%.4f' % y
    f.write(tmp + '\n')
    
# sustain
f.write(':\n')  # repeat symbol
f.write(str(sustain) + '\n')
f.write(':\n')  # repeat symbol

# release
rise = -sustain
run = sample_rate * release
#run = release / td
m = rise / run
b = sustain
for x in range(0, int(run)):
    y = m * x + b
    tmp = '%.4f' % y
    f.write(tmp + '\n')
f.write('0')

f.close()