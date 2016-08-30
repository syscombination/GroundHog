import codecs
import string
import sys
import copy

inpfile = sys.argv[1]
inp = open(inpfile, 'r').read()
inp = inp.replace('$ ', '')
inp = inp.replace(' $', '')

output = open(sys.argv[2],'w')
output.write(inp)
output.close()