import numpy

def get_oracle(y,h,empty):
	
	length = len(h)
	num_systems = len(h[0])
	results = []
	ref_dict = getRefDict([str(i) for i in y])
	for i in range(num_systems):
		results.append(h[0][i])
	for i in range(1,length):
		tmpresult = []
		for j in range(num_systems):
			for k in range(num_systems):
				tmpresult.append((results[j]+[h[i][k]], \
					calBleu([str(m) for m in results[j]+[h[i][k]]],re)))
		print tmpresult
		sort = sorted(tmpresult,key=lambda t:t[1],reverse=True)
		for j in range(num_systems):
			results[j] = tmpresult[j][0]
	print results
	return y

def my_log(a):
    if a == 0:
        return -100000
    return math.log(a)
def cutSen(x,state):
    if state['null_sym_target'] not in x:
        return x
    else:
        return x[:x.index(state['null_sym_target'])+1]

def getRefDict(words):
    lens = len(words)
    now_ref_dict = {}
    for n in range(1,5):
        for start in range(lens-n+1):
            gram = ' '.join([str(p) for p in words[start:start+n]])
            if gram not in now_ref_dict:
                now_ref_dict[gram] = 1
            else:
                now_ref_dict[gram] += 1
    return now_ref_dict, lens

def calBleu(x,ref_dict,lens):

    length_trans = len(x)
    words = x
    closet_length = lens
    sent_dict = {}
    for n in range(1,5):
        for start in range(length_trans-n+1):
            gram = ' '.join([str(p) for p in words[start:start+n]])
            if gram not in sent_dict:
                sent_dict[gram] = 1
            else:
                sent_dict[gram] += 1
    correct_gram = [0,0,0,0]
    for gram in sent_dict:
        if gram in ref_dict:
            n = len(gram.split(' '))
            correct_gram[n-1] += min(ref_dict[gram], sent_dict[gram])
    bleu = [0.,0.,0.,0.]
    smooth = 0
    for j in range(4):
        if correct_gram[j] == 0:
            smooth = 1
    for j in range(4):
        if length_trans > j:
            bleu[j] = 1.*(correct_gram[j]+smooth)/(length_trans - j + smooth)
        else:
            bleu[j] = 1
    brev_penalty = 1
    if length_trans < closet_length:
        brev_penalty = math.exp(1 - closet_length*1./length_trans)
    now_bleu = brev_penalty*math.exp((my_log(bleu[0]) + my_log(bleu[1]) + my_log(bleu[2]) + my_log(bleu[3]))/4)
    return now_bleu

if __name__ == "__main__":
	get_oracle([1,2,3,4,5],[[10,2,10,10,3,5,10],[1,2,10,10,3,4,5],[1,10,10,4,3,10,5]],10)