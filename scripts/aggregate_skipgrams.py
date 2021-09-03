#!/usr/bin/env python3
# coding: utf-8

import sys
from collections import Counter

ngrams = Counter()
words = Counter()
l_words = Counter()

for line in sys.stdin:
    if line.startswith('FILENAME'):
        fn = line.strip()
        words.update(l_words)
        l_words.clear()
        continue
    try:
        word, tag, f_word, f_tag, f_ngram = line.strip().split('\t')
        ngrams[(word, tag)] += int(f_ngram)
        if word not in l_words:
            l_words[word] += int(f_word)
        if tag not in l_words:
            l_words[tag] += int(f_tag)
    except ValueError:
        sys.stderr.write("Incorrect input line — %s: %s" % (fn, line))

for ng, f in ngrams.most_common():
    word, tag = ng
    print('\t'.join([word, tag, str(words[word]), str(words[tag]), str(f)]))
