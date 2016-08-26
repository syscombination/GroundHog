import codecs
import string
import sys
import traceback

alignfile = sys.argv[1]
num_systems = string.atoi(sys.argv[2])
outputfile = sys.argv[3]

num_align = num_systems*(num_systems-1)
#num_align = (num_systems-1)
aligns = open(alignfile, 'r').read().split('\n')
if aligns[-1] == '':
	aligns = aligns[:-1]
print 'lines:',len(aligns)
num_sentence = len(aligns)/num_align
print 'sentence num:',num_sentence
assert num_sentence*num_align == len(aligns)

result = []

for i in xrange(num_systems):
	result.append([])

for i in xrange(num_sentence):
	try: 
		if i % 10000 == 0:
			print 'sentence:',i
		index = num_align*i
		#print 'index:', index
		tmpresult = []
		for j in xrange(num_systems):
			tmpresult.append([])
		#print aligns[index]
		nodes = aligns[index].split(' ')
		for k in xrange(len(nodes)):
			node = nodes[k]
			tmpresult[0].append(node.split('|')[1])
			tmpresult[1].append(node.split('|')[0])
		#print len(tmpresult[0])
		#print len(tmpresult[1])
		for j in range(2, num_systems):
			index = num_align*i+j-1
			#print 'index:', index
			#print '-----'+str(j)+'-----'
			pos = 0
			nodes = aligns[index].split(' ')
			for k in xrange(len(nodes)):
				node = nodes[k]
				if len(node.split('|')) == 3:
					if node.split('|')[0] != '':
						bone = '|'
						newh = node.split('|')[0]
					elif  node.split('|')[-1] != '':
						bone = node.split('|')[-1]
						newh = '|'
					elif node.split('|')[0] == '$':
						newh = '$'
						bone = node.split('|')[1]+'|'+node.split('|')[2]
					elif  node.split('|')[-1] == '$':
						bone = node.split('|')[-2]+'|'+node.split('|')[-1]
						newh = '$'
				else:
					bone = node.split('|')[1]
					newh = node.split('|')[0]
				#print node,str(k)+'/'+str(len(nodes)), pos, len(tmpresult[0]), len(tmpresult[1])
				if bone == '$':
					if pos == len(tmpresult[0]): 
						for h in xrange(j):
							tmpresult[h].insert(pos,'$')
						tmpresult[j].append(newh)
						pos += 1
					else:
						if tmpresult[0][pos] != '$':
							for h in xrange(j):
								tmpresult[h].insert(pos,'$')
						tmpresult[j].append(newh)
						pos += 1
				else:
					while tmpresult[0][pos] != bone:
						pos += 1
						tmpresult[j].append('$')
					tmpresult[j].append(newh)
					pos+=1
			while len(tmpresult[j]) < len(tmpresult[0]):
				tmpresult[j].append('$')
				#pos += 1
		#print tmpresult
		for i in xrange(num_systems):
			result[i].append(' '.join(tmpresult[i]))
	except:
		print traceback.print_exc()
		print 'fail:', i
		print index
		print aligns[index]
		print tmpresult
		print len(tmpresult[0])
		print len(tmpresult[j])
		print bone, newh
		print pos
		exit()

for i in xrange(num_systems):
	output = open(outputfile+str(i),'w')
	output.write('\n'.join(result[i])+'\n')
	output.close()
