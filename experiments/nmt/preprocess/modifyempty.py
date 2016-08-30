import codecs
import string
import sys
import copy

inpfile = sys.argv[1]
lines = open(inpfile, 'r').read().split('\n')[:-1]

for i in range(len(lines)):
	if lines[i] == '':
		lines[i] = 'FAIL'

output = open(sys.argv[2],'w')
output.write('\n'.join(lines)+'\n')
output.close()