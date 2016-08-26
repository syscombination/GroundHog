import cPickle
import sys
import string

vocab = cPickle.load(open(sys.argv[1]))
for i in vocab:
	if vocab[i] == string.atoi(sys.argv[3])-1:
		del vocab[i]
		break
vocab['$'] = string.atoi(sys.argv[3])-1
cPickle.dump(vocab, sys.argv[2], protocol=cPickle.HIGHEST_PROTOCOL)