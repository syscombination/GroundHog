import numpy
import math


def get_oracle(y,h,empty):
    delempty = {}
    length = len(h)
    num_systems = len(h[0])
    results = {}
    #print [str(i) for i in y]
    ref_dict,l = getRefDict([str(i) for i in y])
    #print l
    #print ref_dict
    #calBleu(['1','2','3','4','5'],ref_dict,5)
    #exit()
    for i in range(num_systems):
        if h[0][i] != empty:
            delempty[str(h[0][i])] = str(h[0][i])
            results[str(h[0][i])]=calBleu([str(h[0][i])],ref_dict,l)
        else:
            delempty[str(h[0][i])] = ''
            results[str(h[0][i])]=calBleu([],ref_dict,l)
    for i in range(1,length):
        #print 'results:', results
        tmpresult = {}
        for r in results:
            for k in range(num_systems):
                if h[i][k] != empty:
                    if delempty[r] == '':
                        delempty[r+' '+str(h[i][k])] = str(h[i][k])
                    else:
                        delempty[r+' '+str(h[i][k])] = delempty[r]+' '+str(h[i][k])
                    tmpresult[r+' '+str(h[i][k])]=calBleu(delempty[r+' '+str(h[i][k])].split(' '),ref_dict,l)
                else:
                    delempty[r+' '+str(h[i][k])] = delempty[r]
                    tmpresult[r+' '+str(h[i][k])]=results[r]
        #print 'tmpresult:',tmpresult
        sort = sorted(tmpresult.items(),key=lambda t:t[1],reverse=True)
        #print sort
        results = {}
        for j in range(min(num_systems*100,len(sort))):
            results[sort[j][0]] = sort[j][1]
    #print results
    sort = sorted(results.items(),key=lambda t:t[1],reverse=True)
    print sort[0][0], sort[0][1]
    if sort[0][0].split(' ') == [str(empty)]*length:
        return sort[1][0].split(' ')
    else:
        return sort[0][0].split(' ')

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
    if length_trans == 0:
        return 0.5
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
            bleu[j] = 0.01

    brev_penalty = 1
    if length_trans < closet_length:
        brev_penalty = math.exp(1 - closet_length*1./length_trans) 
    #brev_penalty = 1

    now_bleu = brev_penalty*math.exp((my_log(bleu[0]) + my_log(bleu[1]) + my_log(bleu[2]) + my_log(bleu[3]))/4)
    #print x,bleu, brev_penalty,now_bleu,closet_length,length_trans
    return now_bleu

if __name__ == "__main__":
    y = numpy.asarray([1,2,3,4,5],dtype=int)
    h = numpy.asarray([[1,1],[10,2],[6,10],[3,3],[4,10],[5,5]],dtype=int)
    get_oracle(y,h,10)