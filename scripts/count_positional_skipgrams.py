#!/usr/bin/env python3
# coding: utf-8

import argparse
from collections import deque, namedtuple, Counter


class Skipgram(namedtuple('Skipgram', ['w', 'c', 'p'])):
    __slots__ = ()

    def __str__(self):
        return '%s\t%s:%d' % self

    @property
    def tagstr(self):
        return '%s:%d' % (self.c, self.p)
        


def parse_arguments():
    parser = argparse.ArgumentParser(description='Count positional skipgrams in a .vert file')
    parser.add_argument('vertfile', help='Input .vert file')
    parser.add_argument('-w', '--window', help='window size (each side of a token)',
                        default=5, type=int)
    return parser.parse_args()


def main():
    args = parse_arguments()
    right = deque(maxlen=args.window)
    left = deque(maxlen=args.window)
    ngrams = Counter()
    words = Counter()
    collocates = Counter()
    
    with open(args.vertfile, 'r') as vert:
        for line in vert:
            if not line.startswith('<'):
                fs = line.strip().split('\t')
                if len(fs) < 3:
                    continue
                sg = Skipgram(w=fs[1], c=fs[2], p=0)
                ngrams[sg] += 1
                words[fs[1]] += 1
                collocates[sg.tagstr] += 1
                for ri, rc in enumerate(right, start=1):
                    sg = Skipgram(w=rc, c=fs[2], p=ri)
                    ngrams[sg] += 1
                    collocates[sg.tagstr] += 1
                for li, lc in enumerate(left, start=1):
                    sg = Skipgram(w=fs[1], c=lc, p=-li)
                    ngrams[sg] += 1
                    collocates[sg.tagstr] += 1
                right.appendleft(fs[1])
                left.appendleft(fs[2])

    for ng, f in ngrams.most_common():
        print('\t'.join([ng.w, ng.tagstr, str(words[ng.w]), str(collocates[ng.tagstr]), str(f)]))

if __name__ == '__main__':
    main()
