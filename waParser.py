import argparse

parser = argparse.ArgumentParser(prog='waParser', description='Takes a Worms Armageddon input file (truncated from a replay file) and outputs the player inputs in Bizhawk format')
parser.add_argument('inputFilePath')
args = parser.parse_args()
inputFilePath = str(args.inputFilePath)

with open(inputFilePath, 'rb') as inputFile:
    inputData = inputFile.read()

# Event Code: [ argument size, description ]
events = {
    0x00: [ 0,  'Control spacer' ],
    0x02: [ 0,  'Frame End' ],
    0x06: [ 1,  'Round Finish' ],
    0x08: [ 8,  'Checksum ' ],
    0x09: [ 4,  'Checksum' ],
    0x0C: [ 5,  'Unknown' ],
    0x0D: [ 2,  'Disconnection Information' ],
    0x0F: [ 4,  'Discussion' ],
    0x11: [ 5,  'Mouse Movement' ],
    0x12: [ 2,  'Girder Orientation' ],
    0x13: [ 2,  'Strike Orientation' ],
    0x16: [ 1,  'Game End' ],
    0x17: [ 0,  'Cut Crate Parachute' ],
    0x1A: [ 1,  'Thought Bubble' ],
    0x1B: [ 1,  'Unknown' ],
    0x1E: [ 1,  'Left Key' ],
    0x1F: [ 1,  'Right Key' ],
    0x20: [ 1,  'Up Key' ],
    0x21: [ 1,  'Down Key' ],
    0x24: [ 1,  'Forward Jump (or release rope)' ],
    0x25: [ 1,  'Upward Jump' ],
    0x26: [ 1,  'Weapon Launch' ],
    0x27: [ 1,  'Weapon Release' ],
    0x2B: [ 1,  'Team Forced Out' ],
    0x2C: [ 1,  'Trigger Weapon' ],
    0x2D: [ 1,  'Sheep fly left' ],
    0x2E: [ 1,  'Sheep fly right' ],
    0x2F: [ 2,  'Set fuse' ],
    0x30: [ 2,  'Set herd size' ],
    0x31: [ 2,  'Set bounciness' ],
    0x32: [ 7,  'Mouse click' ],
    0x33: [ 3,  'Weapon selection' ],
    0x3A: [ 0,  'Sudden Death' ],
    0x43: [ 1,  'Worm selection' ],
    0x62: [ 1,  'Pressing Shift' ],
    0x6B: [ 5,  'Unknown' ],
    0x6C: [ 0,  'Spurious Extra Frame' ],
    0x6D: [ 2,  'Player disconnection' ],
    0x70: [ 3,  'Various player information' ],
    0x71: [ 3,  'Various player information' ],
    0x72: [ 3,  'Various player information' ],
    0x73: [ 3,  'Various player information' ],
    0x74: [ 4,  'A Skipped Packet possibility' ] }

head = 0
fileSize = len(inputData)

# Base input that bizhawk can read
baseInput = '| 1280, 1024,    0,    0,............................................................................................................|'

# Creating new input from the base input
newInput = list(baseInput)

# Keeps track of the current frame
curFrame = 0

# Frame offset (to correct with unaligned frame value in RAM watch)
frameOffset = 37

while (head < fileSize):

    # Parsing code
    code = inputData[head]
    if not code in events:
        print(f"Error, undetected code: {code}")
        exit(-1)

    # Advance head to the first argument position
    head = head + 1

    # Printing frame marker, Z for even, X for odd. This is to guide myself
    #if (head % 2 == 0): newInput[60] = 'Z'
    #else: newInput[61] = 'X'

    # Parsing direction key press
    if (code == 0x1E): newInput[113] = '<'
    if (code == 0x1F): newInput[116] = '>'
    if (code == 0x20): newInput[114] = '^'
    if (code == 0x21): newInput[115] = 'v'

    # Parsing forward jump
    if (code == 0x24): newInput[82] = 'e'

    # Unknown code seems to be enter?
    #if (code == 0x0C): 
    #    newInput[82] = 'e'
    #    print(f' 0x{inputData[head+0]:02X}')
    #    print(f' 0x{inputData[head+1]:02X}')
    #    print(f' 0x{inputData[head+2]:02X}')
    #    print(f' 0x{inputData[head+3]:02X}')

    # Parsing upward jump
    if (code == 0x25): newInput[81] = 'b'

    # Parsing weapon shooting
    if (code == 0x26): newInput[83] = 's'

    # Parsing weapon release
    if (code == 0x27): newInput[84] = 'd'

    # Parsing weapon trigger
    if (code == 0x2C): newInput[83] = 's'

    # Sheep Flight
    if (code == 0x2D): newInput[113] = '<'
    if (code == 0x2E): newInput[116] = '>'

    # Pressing Shift
    if (code == 0x62): newInput[84] = 's'

    # Set Fuse
    if (code == 0x2F): 
        worm     = inputData[head + 0]
        duration = inputData[head + 1]
        if (duration == 1): newInput[31] = '1'
        if (duration == 2): newInput[32] = '2'
        if (duration == 3): newInput[33] = '3'
        if (duration == 4): newInput[34] = '4'
        if (duration == 5): newInput[35] = '5'

    # If end frame code, then print and reset the new input
    if (code == 0x02): 
        print(f' Frame {curFrame + frameOffset:04d}: {"".join(newInput)}')
        newInput = list(baseInput)
        curFrame = curFrame + 1
    
    
    # Print code
    if code != 0x02 and code != 0x0C: print(f'Code: 0x{code:02X}: {events[code][1]}')

    # Advance head to skip arguments, into the next code
    head = head + events[code][0]
