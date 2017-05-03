#!/usr/bin/env python
# coding: utf-8

import NTCIR
from test_base import _sample
import TREC
from TRECpp.adv import ResultDict
from TRECpp.adv import RunDict
import unittest


class TestAdv(unittest.TestCase):
    def test_red_setitem(self):
        rd = ResultDict()
        rd['dummy'] = NTCIR.Result()
        rd['dummy'] = TREC.Result()
        try:
            rd['dummy'] = TREC.Run()
            raise
        except AssertionError:
            pass

    def test_red_paired_t(self):
        rd = ResultDict()
        rd['k0'] = TREC.Result().read(_sample('TREC_result.txt'))
        rd['k1'] = TREC.Result().read(_sample('TREC_result.txt'))
        rd['k1']['3']['alpha-nDCG@10'] = 0.0
        actual = rd.paired_t()
        self.assertAlmostEqual(actual['k0']['k1']['pvalue'], 0.373901)
        self.assertAlmostEqual(actual['k1']['k0']['pvalue'], 0.373901)
        self.assertAlmostEqual(
            actual['k0']['k1']['statistic'],
            -actual['k1']['k0']['statistic']
        )
        self.assertEqual(actual['k0']['k1']['level'], '')
        self.assertEqual(actual['k1']['k0']['level'], '')

    def test_rud_setitem(self):
        rd = RunDict()
        rd['dummy'] = NTCIR.Run()
        rd['dummy'] = TREC.Run()
        try:
            rd['dummy'] = TREC.Result()
            raise
        except AssertionError:
            pass

    def test_rud_ndeval(self):
        rd = RunDict()
        rd['dummy0'] = NTCIR.Run().read(_sample('NTCIR_run'))
        rd['dummy1'] = TREC.Run().read(_sample('TREC_run.txt'))
        rel = TREC.Relevance().read(_sample('TREC_relevance.txt'))
        expect = TREC.Result().read(_sample('TREC_result.txt'))
        actual = rd.ndeval(rel)['dummy1']
        self.assertEqual(expect, actual)

    def test_rud_NTCIREVAL(self):
        rd = RunDict()
        rd['dummy0'] = NTCIR.Run().read(_sample('NTCIR_run'))
        rd['dummy1'] = TREC.Run().read(_sample('TREC_run.txt'))
        rel = NTCIR.Relevance().read(_sample('NTCIR_relevance'))
        expect = NTCIR.Result().read(_sample('NTCIR_result'))
        actual = rd.NTCIREVAL(rel)['dummy0']
        self.assertEqual(expect, actual)


if __name__ == '__main__':
    unittest.main()