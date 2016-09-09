import codecs
import string
import sys
import traceback

alignfile = sys.argv[1]
num_systems = string.atoi(sys.argv[2])
outputfile = sys.argv[3]
oraclefile = sys.argv[4]

num_align = num_systems*(num_systems+1)
#num_align = (num_systems-1)
aligns = open(alignfile, 'r').read().split('\n')
if aligns[-1] == '':
	aligns = aligns[:-1]
print 'lines:',len(aligns)
num_sentence = len(aligns)/num_align
print 'sentence num:',num_sentence
assert num_sentence*num_align == len(aligns)

result = []
oracle = []

def getalignedwords(node):
	if len(node.split('|')) >= 3:
		if node.split('|')[0] == '$':
			newh = '$'
			bone = '|'.join(node.split('|')[1:])
		elif  node.split('|')[-1] == '$':
			newh = '|'.join(node.split('|')[:-1])
			bone = '$'
		elif node.split('|')[0] != '':
			bone = '|'
			newh = node.split('|')[0]
		elif  node.split('|')[-1] != '':
			bone = node.split('|')[-1]
			newh = '|'		
	else:
		bone = node.split('|')[1]
		newh = node.split('|')[0]
	return bone,newh

for i in xrange(num_systems):
	result.append([])

for i in xrange(num_sentence):
	try: 
		if i % 10000 == 0:
			print 'sentence:',i
		index = num_align*i+num_systems+1
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
			index = num_align*i+num_systems+j
			#print 'index:', index
			#print '-----'+str(j)+'-----'
			pos = 0
			nodes = aligns[index].split(' ')
			for k in xrange(len(nodes)):
				node = nodes[k]
				bone, newh = getalignedwords(node)
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
			#align to the sentence ending
			while len(tmpresult[j]) < len(tmpresult[0]):
				tmpresult[j].append('$')
			#incremental swap
			iterator = range(len(tmpresult[0]))
			k = 0
			while k < len(iterator):
				pos = iterator[k]
				unrelated = True
				if tmpresult[j][pos] == '$':
					k += 1
					continue
				for ref in range(j):
					if tmpresult[ref][pos] == tmpresult[j][pos]:
						unrelated = False
						break
				if unrelated:
					#print j,pos,tmpresult[j][pos],
					finish = False
					for swap in range(len(tmpresult[0])):
						for ref in range(j):
							if not finish and tmpresult[ref][swap] == tmpresult[j][pos] and tmpresult[ref][swap] != tmpresult[j][swap]:
								#print j,k,pos,swap,tmpresult[ref][swap],tmpresult[j][pos],tmpresult[j][swap]
								tmp = tmpresult[j][swap]
								tmpresult[j][swap] = tmpresult[j][pos]
								tmpresult[j][pos] = tmp
								iterator[swap] = pos
								finish = True
				k += 1
			#delete all empty positions 
			pos = 0
			while pos < len(tmpresult):
				allempty = True
				for k in range(num_systems):
					if tmpresult[k][pos] != '$':
						allempty = False
						break
				if allempty:
					for k in range(num_systems):
						del tmpresult[k][pos]
					pos -=1
				pos+=1 
		#print tmpresult
		for tmpn in xrange(num_systems):
			result[tmpn].append(' '.join(tmpresult[tmpn]))
		#calculate oracle path
		tmporacle = ['$']*len(tmpresult[0])
		index = num_align*i+num_systems
		pos = 0
		nodes = aligns[index].split(' ')
		miss = []
		for k in xrange(len(nodes)):
			node = nodes[k]
			bone, ref = getalignedwords(node)
			if bone == '$':
				miss.append(ref)
			else:
				while tmpresult[0][pos] != bone:
					pos += 1
				tmporacle[pos] = ref
		#print tmporacle
		#print miss
		while len(miss) > 0:
			ref = miss[0]
			for pos in range(len(tmpresult[0])):
				for snum in range(num_systems):
					if tmpresult[snum][pos] == ref and tmpresult[snum][pos] != tmporacle[pos]:
						#print ref
						tmporacle[pos] = ref
			del miss[0]
		oracle.append(' '.join(tmporacle))
		#print oracle
	except:
		print traceback.print_exc()
		print 'fail:', i
		print index
		print aligns[index]
		print tmpresult
		print len(tmpresult[0])
		print len(tmpresult[j])
		print bone, newh
		print node.split('|')
		print pos
		exit()

for i in xrange(num_systems):
	output = open(outputfile+str(i),'w')
	output.write('\n'.join(result[i])+'\n')
	output.close()
output = open(oraclefile,'w')
output.write('\n'.join(oracle)+'\n')
output.close()
