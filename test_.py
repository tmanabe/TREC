#!/usr/bin/env python
# coding: utf-8

import tempfile
import TREC
import unittest


class TestTREC(unittest.TestCase):

    def _test(self, cls, path):
        d = tempfile.TemporaryDirectory()
        p = '%s/tmp.txt' % d.name
        source = cls().read(path)
        source.write(p)
        destination = cls().read(p)
        d.cleanup()
        return (source, destination)

    def test_query(self):
        self.assertEqual(*self._test(TREC.Query, './sample_query.txt'))

    def test_probabilistic_relevance(self):
        cls = TREC.ProbabilisticRelevance
        path = './sample_probabilistic_relevance.txt'
        self.assertEqual(*self._test(cls, path))

    def test_relevance(self):
        cls = TREC.Relevance
        path = './sample_relevance.txt'
        self.assertEqual(*self._test(cls, path))

    def test_run(self):
        self.assertEqual(*self._test(TREC.Run, './sample_run.txt'))

    def test_result(self):
        self.assertEqual(*self._test(TREC.Result, './sample_result.txt'))


if __name__ == '__main__':
    unittest.main()