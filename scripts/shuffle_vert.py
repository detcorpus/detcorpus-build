#!/usr/bin/python3
# coding: utf-8

import argparse
import random


def parse_arguments():
    parser = argparse.ArgumentParser(description='Reshuffle data in vert files for publishing')
    parser.add_argument('infile', type=argparse.FileType('r'),
                        default='-', help=".vert file to be processed")
    parser.add_argument('outfile', type=argparse.FileType('w'), default='-',
                        help="Output file")
    return parser.parse_args()


class Doc(object):
    def __init__(self, data):
        self.header = None
        self.footer = None
        self.body = []
        self.fragments = []
        for line in data:
            if line.startswith('<doc'):
                self.header = line
            elif line.startswith('</doc'):
                self.footer = line
            else:
                self.body.append(line)

    def iter_fragments(self):
        body = []
        for line in self.body:
            if line.startswith('<f'):
                head = line
            elif line.startswith('</f'):
                tail = line
                yield Fragment(head, body, tail)
                body = []
            else:
                body.append(line)
        if body:
            print("REMAINDER", body)


class Fragment(object):
    def __init__(self, head, body, tail):
        self.head = head
        self.body = body
        self.tail = tail
        self.sentences = self.iter_sentences()

    def iter_sentences(self):
        out = []
        s = []
        for line in self.body:
            if line.startswith('<s'):
                if s:
                    out.append(s)
                    s = []
            elif line.startswith('</s'):
                out.append(s)
                s = []
            else:
                s.append(line)
        if s:
            out.append(s)
        return out

    def shuffle_sent(self):
        random.shuffle(self.sentences)

    def __str__(self):
        sents = []
        for s in self.sentences:
            sents.append('<s>\n{}</s>\n'.format(''.join(s)))
        return ''.join([self.head, ''.join(sents), self.tail])


def main():
    args = parse_arguments()
    doc = Doc(args.infile)
    args.outfile.write(doc.header)
    for f in doc.iter_fragments():
        f.shuffle_sent()
        args.outfile.write(str(f))
    args.outfile.write(doc.footer)


if __name__ == '__main__':
    main()
