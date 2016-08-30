import codecs
import string
import sys
import copy

alignfile='meteor.alignment'

aligns = open(alignfile, 'r').read().split('\n')[:-1]

grfile = sys.argv[1]
grs = open(grfile, 'r').read().split('\n')[:-1]

print len(aligns)
print len(grs)

for i in range(14600,len(grs)):
	index = 12*i+1
	align =aligns[index]
	nodes = align.split(' ')
	s = [node.split('|')[1] for node in nodes]
	so = copy.deepcopy(s)
	while '$' in s:
		s.remove('$')
	sent = ' '.join(s)
	gr = grs[i].replace('$', '<dollar-symbol>')
	sent = sent.replace("  ", " ")
	#print sent
	#print gr
	if sent != gr:
		print i, index
		print gr
		#print align
		#print so
		#print s
		print sent
	 	assert 0 == 1
#print index