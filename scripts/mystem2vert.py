#!/usr/bin/env python3
# coding: utf-8

import sys
import re
import string
import xml.etree.cElementTree as e
from collections import defaultdict


def flatten_grammemes_list(grams):
    out = set()
    for gset in grams.split('|'):
        for gram in gset.split(','):
            out.add(gram)
    return '|'.join(sorted(out))


def parse_grammemes(attr):
    const, variable = attr.split(u'=')
    tags = const.split(u',')
    pos = tags[0]
    constgram = u'|'.join(tags[1:])
    vargram = flatten_grammemes_list(variable.strip('()'))
    d = {'tag': pos,
         'const': constgram,
         'var': vargram}
    return d


class Tokenizer(object):
    def __init__(self):
        self.ispunct = re.compile("[{}]+$".format(re.escape(string.punctuation +
                                                            '—«»„“”‘’…–')))
        """workaround that helps hide page breaking tags from mystem"""
        self.ispagebreak = re.compile('PB[0-9]+')

    def make_pagebreak_tag(self, tok):
        """format page break tags in a format suitable for indexing"""
        num = re.search('[0-9]+', tok)
        return '<page n="{}"/>'.format(num.group(0))

    def tokenize_tail(self, tail):
        """split non-word data left out by mystem into tokens"""
        toklist = re.split("\\s+", tail)
        for tok in filter(None, toklist):
            if self.ispagebreak.match(tok):
                t = defaultdict(str, word=self.make_pagebreak_tag(tok))
            elif self.ispunct.match(tok):
                t = defaultdict(str, word=tok, tag='c', lemma=tok)
            elif re.match("\\d+", tok):
                t = defaultdict(str, word=tok, tag='NUM', lemma=tok)
            else:
                t = defaultdict(str, word=tok, tag='UNK', lemma=tok)
            yield t


def print_token(fields):
    """format token dict as a row for a vert file"""
    s = u'{f[word]}\t{f[lemma]}\t{f[tag]}\t{f[const]}\t{f[var]}\n'.format(f=fields)
    sys.stdout.write(s)


def print_header(filename):
    m = re.search(u'([a-zA-Z_]+\.[0-9a-zA-Z._-]+[a-zA-Z]?[0-9]?)\.([12][90][0-9][0-9])[._]([12][90][0-9][0-9])?.*', filename)
    if m:
        id, year, printed = m.groups()
        if not printed:
            printed = 'UNDEF'
        h = u'<doc id="{0}" text_year="{1}" source_year="{2}">\n<f id=1>\n<s>\n'.format(id, year, printed)
    else:
        h = u'<doc>\n<f id=1>\n<s>\n'
    sys.stdout.write(h)


def print_footer():
    sys.stdout.write(u"</s>\n</f>\n</doc>\n")


def main():
    fragsize = 500
    itoken = 0
    fragid = 1
    print_header(sys.argv[1])
    fields = defaultdict(str)
    tokz = Tokenizer()
    for event, elem in e.iterparse(sys.stdin):
        if elem.tag == 'se':
            sys.stdout.write("</s>\n<s>\n")
        elif elem.tag == 'ana':
            fields['lemma'] = elem.get('lex')
            gr = parse_grammemes(elem.get('gr'))
            fields.update(gr)
        elif elem.tag == 'w':
            fields['word'] = u''.join(elem.itertext())
            print_token(fields)
            itoken += 1
            if (itoken % fragsize) == 0:
                fragid += 1
                sys.stdout.write("</f>\n<f id={}>\n".format(fragid))
            fields = defaultdict(str)
            try:
                tail = elem.tail.strip()
            except AttributeError:
                tail = None
            if tail:
                for tok in tokz.tokenize_tail(tail):
                    print_token(tok)
                    itoken += 1
            if (itoken % fragsize) == 0:
                fragid += 1
                sys.stdout.write("</f>\n<f id={}>\n".format(fragid))
    print_footer()


if __name__ == '__main__':
    main()
