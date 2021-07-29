#!/usr/bin/env python3
# coding: utf-8

import sys
from collections import Counter

ngrams = Counter()

for line in sys.stdin:
    fs = line.strip().split('\t')
    ngrams[(fs[0], fs[1])] += int(fs[2])

for ng, f in ngrams.most_common():
    print('%s\t%s\t%d' % (ng[0], ng[1], f))
