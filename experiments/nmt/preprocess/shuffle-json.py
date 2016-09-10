import json
import sys
import random

num_files = len(sys.argv)-1

before = []
for i in range(1, num_files+1):
	before.append(json.loads(open(sys.argv[i], 'r').read()))
length = len(before[0])
for i in range(num_files):
	assert len(before[i]) == len(before[0])
print 'sentences:', length
'''
source = json.loads(open(sys.argv[1], 'r').read())
target = json.loads(open(sys.argv[2], 'r').read())
hypo = json.loads(open(sys.argv[3], 'r').read())

length = len(source)
print length
assert(len(target)) == length
assert(len(hypo)) == length

idx = range(length)
random.shuffle(idx)
newsource = []
newtarget = []
newhypo = []
'''
idx = range(length)
random.shuffle(idx)
after = []
for i in range(num_files):
	after.append([])
for i in xrange(len(idx)):
	if i % 10000 == 0:
		print i
	index = idx[i]
	for j in range(num_files):
		after[j].append(before[j][index])
	'''
	newsource.append(source[index])
	newtarget.append(target[index])
	newhypo.append(hypo[index])
	'''

for i in range(1, num_files+1):
	output = open(sys.argv[i]+'.shuf', 'w')
	output.write(json.dumps(after[i-1]))
	output.close()
'''
sourceout = open(sys.argv[1]+'.shuf', 'w')
sourceout.write(json.dumps(newsource))
sourceout.close()
targetout = open(sys.argv[2]+'.shuf', 'w')
targetout.write(json.dumps(newtarget))
targetout.close()	
hypoout = open(sys.argv[3]+'.shuf', 'w')
hypoout.write(json.dumps(newhypo))
hypoout.close()
'''