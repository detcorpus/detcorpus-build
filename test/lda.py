#!/usr/bin/env python3
# coding: utf-8

import os
import unittest
import pandas as pd
from collections import defaultdict


class LdaModelTestCase(unittest.TestCase):
    def setUp(self):
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        self.df = pd.read_csv(os.path.join(tests_dir, "../metadata.csv"))
        self.meta_docids = set(self.df['id'])
        self.models = [100, 200, 300]
        self.doctopics = defaultdict(set)
        for k in self.models:
            with open(os.path.join(tests_dir, "../lda/doc-topics{}.txt".format(str(k)))) as dt:
                for line in dt:
                    fields = line.split('\t')
                    if len(fields) > 1:
                        self.doctopics[k].add(fields[1])

    longMessage = False
    def test_no_missing_ids(self):
        """check that each document id is present in doc-topics tables"""
        for k in self.models:
            for docid in self.meta_docids:
                with self.subTest(docid=docid):
                    self.assertIn(docid, self.doctopics[k], msg='{0} not found in doc-topics{1}.txt'.format(docid, k))

    def test_no_spurious_ids(self):
        """check that all docids in doc-topics tables are known to the metadata table"""
        for k in self.models:
            for docid in self.doctopics[k]:
                with self.subTest(docid=docid):
                    self.assertIn(docid, self.meta_docids, msg='doc-topics{0}.txt: {1} not found in metadata.csv'.format(k, docid))

if __name__ == '__main__':
    unittest.main()
