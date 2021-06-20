#!/usr/bin/env python3
# coding: utf-8

import os
import unittest
import zipfile
import pandas as pd


class MetadataIntegrityTestCase(unittest.TestCase):
    def setUp(self):
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        self.df = pd.read_csv(os.path.join(tests_dir, "../metadata.csv"))
        self.genres = ['adventure',
                       'animalistic',
                       'biography',
                       'detective',
                       'encyclopedia',
                       'fantasy',
                       'girls',
                       'historical',
                       'horror',
                       'love',
                       'nonfiction',
                       'realism',
                       'school',
                       'skazka']
        with zipfile.ZipFile(os.path.join(tests_dir, '../texts.zip')) as zfile:
            self.zipfiles = list(map(lambda f: f.filename.replace('data/text/', ''),
                                zfile.infolist()))

    def test_empty_authors(self):
        """check that there's no empty author fields"""
        self.assertFalse(any(pd.isna(self.df.author)))

    def test_empty_years(self):
        """check that every item has a publication year"""
        self.assertFalse(any(pd.isna(self.df.year)))

    def test_empty_genre(self):
        """check that every item has a genre label"""
        self.assertFalse(any(pd.isna(self.df.genre)))

    def test_known_genres(self):
        """check that only documented genre labels are used"""
        s = self.df.genre.apply(lambda x: x.split(":"))
        genres = list(s.apply(pd.Series).stack().reset_index(drop=True).unique())
        for genre in genres:
            with self.subTest(genre=genre):
                self.assertIn(genre, self.genres)

    def test_filenames_are_vert(self):
        """check that all fienames have .vert suffix"""
        for f in self.df.filename:
            with self.subTest(f=f):
                self.assertTrue(f.endswith(".vert"))

    def test_unique_ids(self):
        """check that there's no duplicate values in the id column"""
        dups = self.df['id'][self.df['id'].duplicated()]
        self.assertEqual(0, len(dups), msg='duplicate ids: %s' % ' '.join(dups))

    def test_duplicate_titles(self):
        """check that there's only one instance for each author/title combination"""
        dups = self.df[['author','title']][self.df[['author', 'title']].duplicated()]
        self.assertEqual(0, len(dups), msg='duplicate titles:\n %s' % dups)

    longMessage = False
    def test_no_missing_files(self):
        """check that every metadata entry has a corresponding file in the archive"""
        for f in self.df.filename:
            with self.subTest(f=f):
                self.assertIn(str(f), self.zipfiles, msg='%s not found in the texts.zip' % f)

    def test_no_missing_metadata(self):
        """check that every file in the archive has a corresponding metadata entry"""
        mfiles = set(self.df.filename)
        for f in self.zipfiles:
            with self.subTest(f=f):
                self.assertIn(str(f), mfiles, msg='%s has no metadata entry' % f)

if __name__ == '__main__':
    unittest.main()
