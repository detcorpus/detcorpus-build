#!/usr/bin/env python
# coding: utf-8

import sqlite3
import argparse
import csv
import re
import html
import sys
import os
from collections import defaultdict

def get_year(s_year):
    s_year = str(s_year)
    pattern = re.compile('\d{4}')
    m = pattern.search(s_year)
    max_year = 0
    while m:
        year = int(m.group(0))
        if year > max_year:
            max_year = year
        m = pattern.search(s_year, m.end(0))
    if max_year > 0:
        return max_year
    else:
        print('Unknown year: ' + s_year)
        return None

class MetaDB(object):
    def __init__(self, dbfile, genres):
        self._conn = sqlite3.connect(dbfile)
        self._conn.row_factory = sqlite3.Row
        self._cur = self._conn.cursor()
        self._genres = defaultdict(str)

        for row in self.query("SELECT * FROM genres"):
            self._genres[row['filename']] = row['genre']

    def query(self, query, params=None):
        if params:
            return self._cur.execute(query, params)
        else:
            return self._cur.execute(query)

    def __del__(self):
        self._conn.close()

    def get_all_files(self):
        filelist = []
        for row in self.query('SELECT filename FROM texts WHERE filename IS NOT NULL'):
            filelist.append(row[0])
        return filelist

    def concat_description(self, sourcetitle, colophon):
        result = None 
        if sourcetitle:
            result = sourcetitle
        if colophon:
            if result:
                result += ', ' 
            else:
                result = ''
            result += colophon
        return result

    def meta_for_file(self, filename):
        metad = {'id': self.generate_id(filename)}
        for row in self.query(
                "SELECT texts.title, texts.year,"
                " texts.uuid, texts.colophon, texts.sourcetitle,"
                " first_texts.year as first_book_publication,"
                " first_texts.colophon as first_colophon,"
                " first_texts.sourcetitle as first_sourcetitle"
                " FROM texts "
                " LEFT JOIN texts as first_texts ON texts.uuid = first_texts.uuid AND first_texts.filename is null"
                " WHERE texts.filename=?", (filename,)):
            metad.update(row)
        try:
            authors = self.get_authors(metad['uuid'])
            metad.update(authors)
            if not row['first_book_publication']:
                metad['first_book_publication'] = metad['year']
            year = get_year(metad['first_book_publication'])
            metad['edition_year'] = get_year(metad['year'])
            metad['edition'] = self.concat_description(row['sourcetitle'] , row['colophon'])
            if year:
                metad['year'] = year
            if row['first_sourcetitle'] or row['first_colophon']:
                metad['firstprint_description'] = self.concat_description(row['first_sourcetitle'], row['first_colophon'])
            else:
                metad['firstprint_description'] = metad['edition']
            metad.pop('first_sourcetitle')
            metad.pop('first_colophon')
            metad.pop('first_book_publication')
        except (KeyError):
            metad.update(self.fallback_years(filename))
        metad['genre'] = self._genres[filename]
        metad['filename'] = filename
        return metad

    def get_filenames(self):
        fs = self.query('SELECT filename FROM texts WHERE filename is not NULL and filename != \'\' ORDER BY filename')
        return list(map(lambda r: r[0], fs.fetchall()))

    def get_authors(self, uuid):
        authors = defaultdict(list)
        authorid = self.query('SELECT author_id, pseudo_id FROM text_author WHERE uuid=?', (uuid,)).fetchall()
        for row in authorid:
            if row['pseudo_id']:
                authors['author'].append(self.make_authorname('pseudonyms', 'pseudo_id', row['pseudo_id']))
                authors['realname'].append(self.make_authorname('authors', 'author_id', row['author_id']))
            else:
                authors['author'].append(self.make_authorname('authors', 'author_id', row['author_id']))
            authordata = self.query('SELECT sex, birth_year, death_year FROM authors WHERE author_id=?', (row['author_id'],)).fetchone()
            if authordata != None:
                authors['author_sex'].append(authordata['sex'])
                authors['author_birth_year'].append(authordata['birth_year'])
                authors['author_death_year'].append(authordata['death_year'])
        return authors

    def make_authorname(self, table, column, a_id):
        c = self.query('SELECT full, last, first, middle FROM "{}" WHERE {}=?'.format(table.replace('"', '""'), column), (a_id,))
        author = c.fetchone()
        if author == None:
            return ''
        elif 'full' in author:
            return '{full}'.format(**author)
        else:
            return '{last}, {first} {middle}'.format(**author)

    def generate_id(self, filename):
        m = re.search('[0-9]+s/([^.]+\.[^.]+.*?)\.([12][09][0-9][0-9])', filename)
        try:
            return m.group(1)
        except AttributeError:
            sys.stderr.write("Problem generating id: %s\n" % filename)
            m = re.search('[0-9]+s/([^.]+\.[^.]+).*', filename)
            if m:
                return m.group(1)
            else:
                return "NOID"


    def format_docheader(self, metad):
        values = []
        for k, v in metad.items():
            if isinstance(v, list):
                values.append('{}="{}"'.format(k, html.escape('|'.join([str(i) for i in v]))))
            else:
                values.append('{}="{}"'.format(k, html.escape(str(v))))
        return '<doc {}>'.format(' '.join(values))

    def fallback_years(self, filename):
        out = {}
        m = re.search(u'[^.]+\.[^.]+\.([12][90][0-9][0-9])[._-]([12][90][0-9][0-9])?.*', filename)
        if m:
            year, printed = m.groups()
            out['text_year'] = year
            if printed:
                out['year'] = printed
            else:
                out['year'] = year
        return out
                


def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract metadata from sqlite db')
    parser.add_argument('-d', '--dbfile', help='database file')
    parser.add_argument('-g', '--genres', help='genres.csv file')
    parser.add_argument('-f', '--filename', help='return metadata for a given filename')
    parser.add_argument('-o', '--outfile', help='output all metadata as CSV table')
    parser.add_argument('--dataset', action='store_true',
            help='output metadata table in format tailored for dataset publication')
    return parser.parse_args()

def main():
    args = parse_arguments()
    meta_db = MetaDB(args.dbfile, args.genres)
    if args.filename:
        metad = meta_db.meta_for_file(args.filename)
        print(meta_db.format_docheader(metad))
        del meta_db
    elif args.outfile:
        fs = meta_db.get_filenames()
        if args.dataset:
            fieldnames = ['filename', 'author', 'realname', 'author_birth_year', 'author_death_year', 'author_sex',
                    'title', 'year', 'firstprint_description', 'edition_year', 'edition', 'genre', 'id']
        else:
            fieldnames = ['filename', 'id', 'year', 'edition_year', 'genre', 'author_sex',
                           'author_death_year', 'uuid', 'title', 'author', 'author_birth_year', 'realname', 'colophon', 'sourcetitle',
                                               'firstprint_description', 'edition']
        with open(args.outfile, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames, extrasaction='ignore', lineterminator=os.linesep)
            writer.writeheader()
            for f in fs:
                try:
                    metad = meta_db.meta_for_file(f)
                except AttributeError:
                    print("NotFound File: {}".format(f))
                for k, v in metad.items():
                    if isinstance(v, list):
                        metad[k] = ';'.join(str(i) for i in v)
                metad['filename'] = re.sub("\.[^.]+$", ".vert", f)
                writer.writerow(metad) 

if __name__ == '__main__':
    main()
