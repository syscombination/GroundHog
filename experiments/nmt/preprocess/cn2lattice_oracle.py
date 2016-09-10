import codecs
import string
import sys
import traceback
import json

hypofile = sys.argv[1]
oraclefile = sys.argv[2]
empty = string.atoi(sys.argv[3])
null = empty+1

hypos = json.loads(open(hypofile,'r').read())
oracles = json.loads(open(oraclefile,'r').read())


num_systems = len(hypos[0][0])
assert len(hypos) == len(oracles)

print 'sentences:', len(oracles)
print 'num_systems:', len(hypos[0][0])
lattice = []
oracles_delempty = []
for i in range(len(oracles)):
	if (i+1) % 10000 == 0:
		print i+1
	hypo = hypos[i]+[[null]*num_systems]
	oracle = oracles[i]+[null]
	#print hypo
	#print oracle
	assert len(hypo) == len(oracle)
	lastpos = [-1]
	tmpl = []
	tmpo = []
	for j in range(len(oracle)):
		#print j, lastpos
		if oracle[j] == empty:
			continue
		tmpo.append(oracle[j])
		lastpos = sorted(lastpos)
		nextpos = []
		nowwords = []
		for k in range(len(lastpos)):
			pos = lastpos[k]+1
			while pos < len(hypo):
				#print pos
				canempty = False
				for snum in range(num_systems):
					#print snum
					word = hypo[pos][snum]
					if word == empty:
						canempty = True
					elif not word in nowwords:
						nowwords.append(word)
					if word == oracle[j]:
						if not pos in nextpos:
							nextpos.append(pos)
				if not canempty:
					break
				pos += 1
		lastpos = nextpos
		tmpl.append(nowwords)
		#print tmpl 
	del tmpo[-1]
	oracles_delempty.append(tmpo)
	lattice.append(tmpl)

assert len(lattice) == len(oracles)
assert len(oracles_delempty) == len(oracles)
output = open(sys.argv[4], 'w')
output.write(json.dumps(oracles_delempty))
output.close()
output = open(sys.argv[5], 'w')
output.write(json.dumps(lattice))
output.close()


				

