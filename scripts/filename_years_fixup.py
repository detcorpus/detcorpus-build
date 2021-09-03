#!/usr/bin/env python
# coding: utf-8

import sys
import csv

def generate_filename(row):
    if not row['year']:
        return None
    decade = int(row['year']) // 10 * 10
    if row['year'] == row['edition_year']:
        filename = '%ds/%s.%d' % (decade, row['id'], int(row['year']))
    else:
        filename = '%ds/%s.%d_%d' % (decade, row['id'], int(row['year']), int(row['edition_year']))
    return filename

def filename_from_path(path):
    return path[:-5]

with open(sys.argv[1]) as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        old_fn = filename_from_path(row['filename'])
        new_fn = generate_filename(row)
        if new_fn and not old_fn == new_fn:
             print('\t'.join([old_fn, new_fn]))
