#!/usr/bin/env python

import argparse
import cPickle
import traceback
import logging
import time
import sys

import numpy

import experiments.nmt
from experiments.nmt import\
    RNNEncoderDecoder,\
    Syscombination_withsource,\
    prototype_state,\
    parse_input

from experiments.nmt.numpy_compat import argpartition

logger = logging.getLogger(__name__)

class Timer(object):

    def __init__(self):
        self.total = 0

    def start(self):
        self.start_time = time.time()

    def finish(self):
        self.total += time.time() - self.start_time

class BeamSearch(object):

    def __init__(self, enc_dec):
        self.enc_dec = enc_dec
        state = self.enc_dec.state
        self.state = state
        self.eos_id = state['null_sym_target']
        self.unk_id = state['unk_sym_target']

    def compile(self):
        self.comp_repr = self.enc_dec.create_representation_computer()
        self.comp_init_states = self.enc_dec.create_initializers()
        self.comp_next_probs = self.enc_dec.create_next_probs_computer()
        self.comp_next_states = self.enc_dec.create_next_states_computer()

    def search(self, seq, systems, n_samples, ignore_unk=False, minlen=1):
        print 'beam search:',seq, systems

        c = self.comp_repr(seq)[0]
        states = map(lambda x : x[None, :], self.comp_init_states(c))
        dim = states[0].shape[1]

        num_levels = len(states)

        fin_trans = []
        fin_costs = []

        trans = [[]]

        costs = [0.0]
        lastpos = []
        for i in range(n_samples):
            lastpos.append([-1])
        systems = numpy.asarray(systems, dtype="int64").transpose()
        num_systems = len(systems[0])
        print 'systems',systems

        for k in range(len(systems)):
            if len(trans) == 0:
                break
            print '-----',k,'-----'
            print 'trans:',trans
            if n_samples == 0:
                break

            beam_size = len(trans)
            #calculate available next word
            h0 = numpy.zeros((beam_size, self.state['n_sym_target']), dtype="float32")
            words = []
            for n in range(beam_size):
                words.append({})
                for i in range(len(lastpos[n])):
                    pos = lastpos[n][i]+1
                    while pos < systems.shape[0]:
                        canempty = False
                        for snum in range(num_systems):
                            word = systems[pos][snum]
                            if word == self.state['empty_sym_target']:
                                canempty = True
                            elif words[n].has_key(word):
                                if not pos in words[n][word]:
                                    words[n][word].append(pos)
                            else:
                                words[n][word]=[pos]
                                h0[n][word] = 1.
                        if not canempty:
                            break
                        pos += 1
            print 'words:',words
            
            #h0 = numpy.zeros((n_samples, self.state['n_sym_target']), dtype="float32")
            #for i in xrange(self.state['num_systems']):
            #    for j in xrange(n_samples):
            #        h0[j][systems[i][k]] = 1.
            # Compute probabilities of the next words for
            # all the elements of the beam.
            

            last_words = (numpy.asarray(map(lambda t : t[-1], trans))
                    if k > 0
                    else numpy.zeros(beam_size, dtype="int64"))
            print 'last_words', last_words
            probs = self.comp_next_probs(c, h0, k, last_words,last_words, *states)[0]
            #print trans
            #print last_words
            #print last_refs
            #if k > 0:
            #    print costs
            #print probs
            #print probs.sum(axis=0)
            #print probs/probs.sum(axis=0).reshape((probs.))
            log_probs = numpy.log(probs)
            #print last_words
            #print log_probs

            # Adjust log probs according to search restrictions
            if ignore_unk:
                log_probs[:,self.unk_id] = -numpy.inf
            # TODO: report me in the paper!!!
            if k < minlen:
                log_probs[:,self.eos_id] = -numpy.inf

            # Find the best options by calling argpartition of flatten array
            next_costs = numpy.array(costs)[:, None] - log_probs
            flat_next_costs = next_costs.flatten()
            best_costs_indices = argpartition(
                    flat_next_costs.flatten(),
                    n_samples)[:n_samples]

            # Decypher flatten indices
            voc_size = log_probs.shape[1]
            trans_indices = best_costs_indices / voc_size
            word_indices = best_costs_indices % voc_size
            costs = flat_next_costs[best_costs_indices]

            # Form a beam for the next iteration
            availcount = 0
            availindex = [-1]*n_samples
            for i, (orig_idx, next_word, next_cost) in enumerate(
                    zip(trans_indices, word_indices, costs)):
                if next_word in words[orig_idx]:
                    availindex[i]= availcount
                    availcount += 1
            new_trans = [[]] * availcount
            new_costs = numpy.zeros(availcount)
            old_states = [numpy.zeros((availcount, dim), dtype="float32") for level
                    in range(num_levels)]
            new_last_refs = numpy.zeros(availcount, dtype="int64")
            new_lastpos = [[]] * availcount
            inputs = numpy.zeros(availcount, dtype="int64")
            for i, (orig_idx, next_word, next_cost) in enumerate(
                    zip(trans_indices, word_indices, costs)):
                if not next_word in words[orig_idx]:
                    continue
                new_trans[availindex[i]] = trans[orig_idx] + [next_word]
                new_costs[availindex[i]] = next_cost
                if next_word == self.state['empty_sym_target']:
                    new_last_refs[availindex[i]] = last_refs[orig_idx]
                else:
                    new_last_refs[availindex[i]] = next_word
                for level in range(num_levels): 
                    old_states[level][availindex[i]] = states[level][orig_idx]
                new_lastpos[availindex[i]] = words[orig_idx][next_word]
                inputs[availindex[i]] = next_word
            new_states = self.comp_next_states(c, h0, k, inputs,inputs, *old_states)
            

            # Filter the sequences that end with end-of-sequence character
            trans = []
            costs = []
            indices = []
            last_refs = []
            lastpos = []
            #print 'newtrans', new_trans
            for i in range(min(n_samples, len(new_trans))):
                if new_trans[i][-1] != self.enc_dec.state['null_sym_target']:
                    trans.append(new_trans[i])
                    costs.append(new_costs[i])
                    last_refs.append(new_last_refs[i])
                    indices.append(i)
                    lastpos.append(new_lastpos[i])
                else:
                    n_samples -= 1
                    #if k == len(systems[0])-1: 
                    fin_trans.append(new_trans[i])
                    fin_costs.append(new_costs[i])
            states = map(lambda x : x[indices], new_states)
            last_refs = numpy.asarray(last_refs, dtype='int64')

        # Dirty tricks to obtain any translation
        '''
        if not len(fin_trans):
            if ignore_unk:
                logger.warning("Did not manage without UNK")
                return self.search(seq, n_samples, False, minlen)
            elif n_samples < 500:
                logger.warning("Still no translations: try beam size {}".format(n_samples * 2))
                return self.search(seq, n_samples * 2, False, minlen)
            else:
                logger.error("Translation failed")
        '''

        fin_trans = numpy.array(fin_trans)[numpy.argsort(fin_costs)]
        fin_costs = numpy.array(sorted(fin_costs))
        #print fin_trans.shape
        return fin_trans, fin_costs

def indices_to_words(i2w, seq):
    sen = []
    for k in xrange(len(seq)):
        if i2w[seq[k]] == '<eol>':
            break
        sen.append(i2w[seq[k]])
    return sen

def sample(lm_model, seq, systems, n_samples,
        sampler=None, beam_search=None,
        ignore_unk=False, normalize=False,
        alpha=1, verbose=False):
    if beam_search:
        sentences = []
        trans, costs = beam_search.search(seq, systems, n_samples,
                ignore_unk=ignore_unk, minlen=len(seq) / 2)
        if normalize:
            counts = [len(s) for s in trans]
            costs = [co / cn for co, cn in zip(costs, counts)]
        for i in range(len(trans)):
            sen = indices_to_words(lm_model.word_indxs, trans[i])
            sentences.append(" ".join(sen))
        for i in range(len(costs)):
            if verbose:
                print "{}: {}".format(costs[i], sentences[i])
        return sentences, costs, trans
    elif sampler:
        sentences = []
        all_probs = []
        costs = []

        values, cond_probs = sampler(n_samples, 3 * (len(seq) - 1), alpha, seq)
        for sidx in xrange(n_samples):
            sen = []
            for k in xrange(values.shape[0]):
                if lm_model.word_indxs[values[k, sidx]] == '<eol>':
                    break
                sen.append(lm_model.word_indxs[values[k, sidx]])
            sentences.append(" ".join(sen))
            probs = cond_probs[:, sidx]
            probs = numpy.array(cond_probs[:len(sen) + 1, sidx])
            all_probs.append(numpy.exp(-probs))
            costs.append(-numpy.sum(probs))
        if normalize:
            counts = [len(s.strip().split(" ")) for s in sentences]
            costs = [co / cn for co, cn in zip(costs, counts)]
        sprobs = numpy.argsort(costs)
        if verbose:
            for pidx in sprobs:
                print "{}: {} {} {}".format(pidx, -costs[pidx], all_probs[pidx], sentences[pidx])
            print
        return sentences, costs, None
    else:
        raise Exception("I don't know what to do")


def parse_args():
    parser = argparse.ArgumentParser(
            "Sample (of find with beam-serch) translations from a translation model")
    parser.add_argument("--state",
            required=True, help="State to use")
    parser.add_argument("--beam-search",
            action="store_true", help="Beam size, turns on beam-search")
    parser.add_argument("--beam-size",
            type=int, help="Beam size")
    parser.add_argument("--ignore-unk",
            default=False, action="store_true",
            help="Ignore unknown words")
    parser.add_argument("--source",
            help="File of source sentences")
    parser.add_argument("--system",
            help="File of single system outputs", nargs="+")
    parser.add_argument("--trans",
            help="File to save translations in")
    parser.add_argument("--normalize",
            action="store_true", default=False,
            help="Normalize log-prob with the word count")
    parser.add_argument("--verbose",
            action="store_true", default=False,
            help="Be verbose")
    parser.add_argument("model_path",
            help="Path to the model")
    parser.add_argument("changes",
            nargs="?", default="",
            help="Changes to state")
    return parser.parse_args()

def main():
    args = parse_args()
    print args.system

    state = prototype_state()
    with open(args.state) as src:
        state.update(cPickle.load(src))
    state.update(eval("dict({})".format(args.changes)))
    if 'num_systems' not in state:
        state['num_systems'] = 4
    if 'empty_sym_target' not in state:
        state['empty_sym_target'] = 136

    logging.basicConfig(level=getattr(logging, state['level']), format="%(asctime)s: %(name)s: %(levelname)s: %(message)s")

    rng = numpy.random.RandomState(state['seed'])
    enc_dec = Syscombination_withsource(state, rng, skip_init=True)
    enc_dec.build()
    lm_model = enc_dec.create_lm_model()
    lm_model.load(args.model_path)
    indx_word = cPickle.load(open(state['word_indx'],'rb'))
    indx_word_t = cPickle.load(open(state['word_indx_target'],'rb'))

    sampler = None
    beam_search = None
    if args.beam_search:
        beam_search = BeamSearch(enc_dec)
        beam_search.compile()
    else:
        sampler = enc_dec.create_sampler(many_samples=True)

    idict_src = cPickle.load(open(state['indx_word'],'r'))
    idict_tgt = cPickle.load(open(state['indx_word_target'],'r'))

    if args.source and args.trans and args.system:
        # Actually only beam search is currently supported here
        assert beam_search
        assert args.beam_size
        #assert len(args.system) == state['num_systems']

        fsrc = open(args.source, 'r')
        ftrans = open(args.trans, 'w')
        fsystems = []
        for i in xrange(state['num_systems']):
            fsystems.append(open(args.system[i],'r'))

        start_time = time.time()


        n_samples = args.beam_size
        total_cost = 0.0
        logging.debug("Beam size: {}".format(n_samples))
        for i, line in enumerate(fsrc):
            seqin = line.strip()
            seq, parsed_in = parse_input(state, indx_word, seqin, idx2word=idict_src)
            systems = []
            for s in xrange(state['num_systems']):
                systems.append(parse_input(state, indx_word_t, fsystems[s].readline(), idx2word=idict_tgt)[0])
            if args.verbose:
                print "Parsed Input:", parsed_in
            trans, costs, _ = sample(lm_model, seq, systems, n_samples, sampler=sampler,
                    beam_search=beam_search, ignore_unk=args.ignore_unk, normalize=args.normalize)
            best = numpy.argmin(costs)
            print >>ftrans, trans[best]
            if args.verbose:
                print "Translation:", trans[best]
            total_cost += costs[best]
            #exit()
            if (i + 1)  % 100 == 0:
                ftrans.flush()
                logger.debug("Current speed is {} per sentence".
                        format((time.time() - start_time) / (i + 1)))
        print "Total cost of the translations: {}".format(total_cost)

        fsrc.close()
        ftrans.close()
    else:
        while True:
            try:
                seqin = raw_input('Input Sequence: ')
                n_samples = int(raw_input('How many samples? '))
                alpha = None
                if not args.beam_search:
                    alpha = float(raw_input('Inverse Temperature? '))
                seq,parsed_in = parse_input(state, indx_word, seqin, idx2word=idict_src)
                print "Parsed Input:", parsed_in
            except Exception:
                print "Exception while parsing your input:"
                traceback.print_exc()
                continue

            sample(lm_model, seq, n_samples, sampler=sampler,
                    beam_search=beam_search,
                    ignore_unk=args.ignore_unk, normalize=args.normalize,
                    alpha=alpha, verbose=True)

if __name__ == "__main__":
    main()
