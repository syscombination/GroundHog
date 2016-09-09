import json
import sys
import random

source = json.loads(open(sys.argv[1], 'r').read())
target = json.loads(open(sys.argv[2], 'r').read())
hypo = json.loads(open(sys.argv[3], 'r').read())
oracle = json.loads(open(sys.argv[4], 'r').read())

length = len(source)
print length
assert(len(target)) == length
assert(len(hypo)) == length
assert(len(oracle)) == length

idx = range(length)
random.shuffle(idx)
newsource = []
newtarget = []
newhypo = []
neworacle = []

for i in xrange(len(idx)):
	if i % 10000 == 0:
		print i
	index = idx[i]
	newsource.append(source[index])
	newtarget.append(target[index])
	newhypo.append(hypo[index])
	neworacle.append(oracle[index])

sourceout = open(sys.argv[1]+'.shuf', 'w')
sourceout.write(json.dumps(newsource))
sourceout.close()
targetout = open(sys.argv[2]+'.shuf', 'w')
targetout.write(json.dumps(newtarget))
targetout.close()	
hypoout = open(sys.argv[3]+'.shuf', 'w')
hypoout.write(json.dumps(newhypo))
hypoout.close()
oracleout = open(sys.argv[4]+'.shuf', 'w')
oracleout.write(json.dumps(neworacle))
oracleout.close()