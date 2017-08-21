#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Purpose:  unit tests
  Author:   Andrey Korzh <ao.korzh@gmail.com>
  Created:  08.08.2017
"""
import unittest
from sys import argv
from os import path as os_path
from csv import DictWriter as csv_DictWriter
from scraper3.scrxPDF.scrxPDF1707 import *

class unitsTest(unittest.TestCase):
    def setUp(self):
        self.path_test_csv= os_path.join(os_path.dirname(__file__), 'test_out.csv')
        path_pdf= os_path.join(
            os_path.dirname(__file__), 'input_files\*PROD [GASOIL][GASOIL][GASOIL].pdf')
        # this dir must include pdftotext.exe:
        argv[0] = os_path.join(os_path.dirname(os_path.dirname(__file__)), 'scrxPDF')
        argv[1:] = ['--path', path_pdf, '--b_ask_to_start', 'False']
        try:
            main() # for all inits
            from scraper3.scrxPDF.scrxPDF1707 import cfg
            self.cfg = cfg
        except ValueError as e: #Exception
            print('testing error:')
            print('\n==> '.join([s for s in e.args if isinstance(s, str)]))
    def tearDown(self):
        pass

    def test_proc_data(self):
        cfg= self.cfg
        fp_out= self.path_test_csv
        with open(fp_out, 'w') as fp_out:
            csv_dict_writer = csv_DictWriter(
                fp_out, fieldnames=cfg['output_files']['header'])
            csv_dict_writer.writeheader()
            for n, nameFull in enumerate(cfg['input_files']['namesFull'], start=1):
                file_data = proc_data(nameFull, csv_dict_writer)
                print(file_data)
                if __debug__:
                    fp_out.flush()
                break # 1 cycle only


if __name__ == '__main__':  #
    unittest.main() #warnings='ignore'