#!/usr/bin/env python

import argparse
import cPickle
import logging
import pprint

import numpy

from groundhog.trainer.SGD_adadelta import SGD as SGD_adadelta
from groundhog.trainer.SGD import SGD as SGD
from groundhog.trainer.SGD_momentum import SGD as SGD_momentum
from groundhog.trainer.SGD_adadeltamrt_scws import SGD as SGD_adadeltamrt
from groundhog.mainLoop import MainLoop
from experiments.nmt import\
        RNNEncoderDecoder, Syscombination_withsource, prototype_state, get_batch_iterator, get_batch_iterator_syscombination
import experiments.nmt
from sample_scws import BeamSearch

logger = logging.getLogger(__name__)

class RandomSamplePrinter(object):

    def __init__(self, state, model, train_iter, beam_search):
        args = dict(locals())
        args.pop('self')
        self.__dict__.update(**args)

    def __call__(self):
        def cut_eol(words):
            for i, word in enumerate(words):
                if words[i] == '<eol>':
                    return words[:i + 1]
            raise Exception("No end-of-line found")

        sample_idx = 0
        while sample_idx < self.state['n_examples']:
            batch = self.train_iter.next(peek=True)
            xs, ys, hs, ohs = batch['x'], batch['y'], batch['h'], batch['oh']
            for seq_idx in range(xs.shape[1]):
                if sample_idx == self.state['n_examples']:
                    break

                x, y, h, oh= xs[:, seq_idx], ys[:, seq_idx], hs[:, seq_idx, :], ohs[:, seq_idx, :]
                #print oh

                x_words = cut_eol(map(lambda w_idx : self.model.word_indxs_src[w_idx], x))
                y_words = cut_eol(map(lambda w_idx : self.model.word_indxs[w_idx], y))
                #h_words = map(lambda w_idx : self.model.word_indxs[w_idx], h)
                if len(x_words) == 0:
                    continue

                print "Input: {}".format(" ".join(x_words))
                for i in xrange(self.state['num_systems']):
                    oh_tmp = oh[:,i]
                    oh_words = cut_eol(map(lambda w_idx : self.model.word_indxs[w_idx], oh_tmp))
                    print "System "+str(i)+':'," ".join(oh_words)
                print "Target: {}".format(" ".join(y_words))
                #print h_words
                trans,costs=self.beam_search.search(x[:len(x_words)],oh[:,:],10)
                if trans.shape[0] > 0:
                    best = numpy.argmin(costs)
                    out_words = cut_eol(map(lambda w_idx : self.model.word_indxs[w_idx], trans[best]))
                    print "Output:", out_words
                else:
                    print 'Failed'
                #self.model.get_samples(self.state['seqlen'] + 1, self.state['n_samples'], x[:len(x_words)],h[:,:])
                sample_idx += 1

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", help="State to use")
    parser.add_argument("--proto",  default="prototype_state",
        help="Prototype state to use for state")
    parser.add_argument("--skip-init", action="store_true",
        help="Skip parameter initilization")
    parser.add_argument("changes",  nargs="*", help="Changes to state", default="")
    return parser.parse_args()

def main():
    args = parse_args()

    state = getattr(experiments.nmt, args.proto)()
    if args.state:
        if args.state.endswith(".py"):
            state.update(eval(open(args.state).read()))
        else:
            with open(args.state) as src:
                state.update(cPickle.load(src))
    for change in args.changes:
        state.update(eval("dict({})".format(change)))

    logging.basicConfig(level=getattr(logging, state['level']), format="%(asctime)s: %(name)s: %(levelname)s: %(message)s")
    logger.debug("State:\n{}".format(pprint.pformat(state)))

    rng = numpy.random.RandomState(state['seed'])
    enc_dec = Syscombination_withsource(state, rng, args.skip_init)
    enc_dec.build() 
    lm_model = enc_dec.create_lm_model()
    if state['mrt']:
        train_sampler = enc_dec.create_sampler(many_samples=True)
        beam_search = BeamSearch(enc_dec)
        beam_search.compile()

    logger.debug("Load data")
    train_data = get_batch_iterator_syscombination(state)
    logger.debug("Compile trainer")
    if state['mrt']:
        algo = eval(state['algo'])(lm_model, state, train_data, train_sampler, beam_search)
    else:
        algo = eval(state['algo'])(lm_model, state, train_data)
    logger.debug("Run training")
    main = MainLoop(train_data, None, None, lm_model, algo, state, None,
            reset=state['reset'],
            hooks=[RandomSamplePrinter(state, lm_model, train_data, beam_search)]
                if state['hookFreq'] >= 0
                else None)
    if state['reload']:
        main.load()
    if state['loopIters'] > 0:
        main.main()

if __name__ == "__main__":
    main()
