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
        try:
            with zipfile.ZipFile(os.path.join(tests_dir, '../texts.zip')) as zfile:
                self.zipfiles = list(map(lambda f: f.filename.replace('data/text/', ''),
                                    zfile.infolist()))
            self.nozip = False
        except FileNotFoundError:
            self.nozip = True

    def skipIfTrue(flag, reason):
        def deco(f):
            def wrapper(self, *args, **kwargs):
                if getattr(self, flag):
                    self.skipTest(reason)
                else:
                    f(self, *args, **kwargs)
            return wrapper
        return deco
            
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

    def test_year_matches_decade_dir(self):
        """check that year corresponds to filename's decade dir"""
        for i, row in self.df.iterrows():
            f = row['filename']
            year = row['year']
            with self.subTest(f=f):
                self.assertEqual(int(f[:3]), int(year) // 10, msg='year/decade dir mismatch: %s — %d' % (f, year))

    def test_unique_ids(self):
        """check that there's no duplicate values in the id column"""
        dups = self.df['id'][self.df['id'].duplicated()]
        self.assertEqual(0, len(dups), msg='duplicate ids: %s' % ' '.join(dups))

    def test_duplicate_titles(self):
        """check that there's only one instance for each author/title combination"""
        dups = self.df[['author','title']][self.df[['author', 'title']].duplicated()]
        self.assertEqual(0, len(dups), msg='duplicate titles:\n %s' % dups)

    longMessage = False
    @skipIfTrue('nozip', 'texts.zip is not yet built')
    def test_no_missing_files(self):
        """check that every metadata entry has a corresponding file in the archive"""
        for f in self.df.filename:
            with self.subTest(f=f):
                self.assertIn(str(f), self.zipfiles, msg='%s not found in the texts.zip' % f)

    @skipIfTrue('nozip', 'texts.zip is not yet built')
    def test_no_missing_metadata(self):
        """check that every file in the archive has a corresponding metadata entry"""
        mfiles = set(self.df.filename)
        for f in self.zipfiles:
            with self.subTest(f=f):
                self.assertIn(str(f), mfiles, msg='%s has no metadata entry' % f)

if __name__ == '__main__':
    unittest.main()
