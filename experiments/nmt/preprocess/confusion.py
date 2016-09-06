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

def getsplit(node):
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
	return bone, newh


result = []

for i in xrange(num_systems):
	result.append([])


def getplainalign(align):
	tnodes = align.split(' ')
	refs = []
	newhs = []
	for i in range(len(tnodes)):
		bone, newh = getsplit(tnodes[i])
		refs.append(bone)
		newhs.append(newh)
	return refs, newhs


def findpos(sentence, opos):
	tmp = -1
	result = -1
	while tmp < opos:
		result += 1
		if sentence[result] != '$':
			tmp += 1
	return result

def findalign(refs,newhs,source, tpos):
	sp = [0]*1000
	for i in range(tpos-1):
		if refs[i] != '$':
			idx = source[sp.index(0):].index(refs[i])+sp.index(0)
			sp[idx] = 1
	finalidx = source[sp.index(0):].index(refs[tpos])+sp.index(0)
	return (refs[tpos], finalidx)

for i in xrange(num_sentence):
	try: 
		if i % 10000 == 0:
			print 'sentence:',i
		index = num_align*i
		#print 'index:', index
		tmpresult = []
		tmpsentences = []
		for j in range(num_systems):
			tmpindex = num_align*i+j*(num_systems-1)
			tmpsentences.append([])
			nodes = aligns[tmpindex].split(' ')
			for k in range(len(nodes)):
				bone, newh =getsplit(nodes[k])
				if bone != '$':
					tmpsentences[j].append(bone)
		#print tmpsentences
		#exit()
		nodes = aligns[index].split(' ')
		bonepos = 0
		newpos = [0]*1000 
		for k in xrange(len(nodes)):
			node = nodes[k]
			bone, newh =getsplit(nodes[k])
			
			if bone == '$':
				bo = '$'
			else:
				bo = (bone, bonepos)
				bonepos+=1
			if newh == '$':
				ne = '$'
			else:
				np = tmpsentences[1][newpos.index(0):].index(newh)+newpos.index(0)
				ne = (newh, np)
				newpos[np] = 1
			tmpresult.append([bo,ne])
		#print tmpresult
		for j in range(2, num_systems):
			index = num_align*i+j-1
			newpos = [0]*1000
			#print 'index:', index
			#print '-----'+str(j)+'-----'
			pos = 0
			nodes = aligns[index].split(' ')
			refss = []
			newhss = []
			for ref in range(1, j):
				secondindex = num_align*i+(num_systems-1)*j+ref
				#print aligns[7]
				refs, newhs = getplainalign(aligns[secondindex])
				#print secondindex
				#print refs, newhs
				refss.append(refs)
				newhss.append(newhs)
			for k in range(len(nodes)):
				node = nodes[k]
				bone, newh = getsplit(node)
				#print pos,bone,newh
				if pos == len(tmpresult):
					tail = []
					for h in xrange(j):
						tail.append('$')
					tmpresult.append(tail)
				while len(tmpresult[pos]) == j+1:
					pos += 1
					if pos == len(tmpresult):
						tail = []
						for h in xrange(j):
							tail.append('$')
						tmpresult.append(tail)
				if newh == '$':
					ne = '$'
				else:
					np = tmpsentences[j][newpos.index(0):].index(newh)+newpos.index(0)
					ne = (newh, np)
					newpos[np] = 1
				#print node,str(k)+'/'+str(len(nodes)), pos, len(tmpresult[0]), len(tmpresult[1])
				if bone == '$':
					#judge if align to secondary hypothesis
					aligned = -1
					if newh != '$':
						#print bone, newh, np, newpos
						for ref in range(1, j):
							spos = findpos(refss[ref-1],np)
							if newhss[ref-1][spos] != '$':
								
								aligned = ref
								dest = findalign(newhss[ref-1], refss[ref-1], tmpsentences[ref], spos)
								#print j,spos,newh,dest
								break
					if aligned >= 0:
						for tmpp in range(len(tmpresult)):
							if tmpresult[tmpp][aligned] == dest:
								if len(tmpresult[tmpp]) == j+1:
									tmpresult[tmpp][j] = ne
								else:
								#print 'ok'
									tmpresult[tmpp].append(ne)
					else:
						if pos == len(tmpresult): 
							tail = []
							for h in xrange(j):
								tail.append('$')
							tail.append(ne)
							tmpresult.append(tail)
							pos += 1
						else:
							if tmpresult[pos][0] != '$':
								ins = []
								for h in xrange(j):
									ins.append('$')
								ins.append(ne)
								tmpresult.insert(pos, ins)
							else:
								tmpresult[pos].append(ne)
							pos += 1
				else:
					lastpos = pos
					bad = False
					while True: 
						if pos == len(tmpresult):
							bad= True
							pos = lastpos
							break
						if tmpresult[pos][0] != '$':
							if tmpresult[pos][0][0] == bone:
								#print lastpos,pos
								break		
						pos += 1
					#print tmpresult[pos],ne
					if bad:
						continue
					else:
						for tm in range(lastpos,pos):
							if len(tmpresult[tm]) < j+1:
								tmpresult[tm].append('$')
					#print tmpresult[pos],ne
					tmpresult[pos].append(ne)
					pos+=1
			for p in range(len(tmpresult)):
				if len(tmpresult[p]) < j+1:
					#print p
					tmpresult[p].append('$')
			#while len(tmpresult[j]) < len(tmpresult[0]):
			#	tmpresult[j].append('$')
				#pos += 1
		#print tmpresult
		#print tmpresult
		for j in range(num_systems):
			result[j].append([])
		for i in xrange(len(tmpresult)):
			for j in range(num_systems):
				if tmpresult[i][j] == '$':
					result[j][-1].append('$')
				else:
					result[j][-1].append(tmpresult[i][j][0])
		for j in range(num_systems):
			result[j][-1] = ' '.join(result[j][-1])
	except:
		print traceback.print_exc()
		print 'fail:', i, j
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
