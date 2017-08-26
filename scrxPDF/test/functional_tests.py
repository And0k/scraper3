#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Purpose:  funtional test
  Author:   Andrey Korzh <ao.korzh@gmail.com>
  Created:  08.08.2017
"""
import unittest
from sys import argv
from os import path as os_path
from scraper3.scrxPDF.scrxPDF1707 import main as scrxPDF

class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_can_start_a_list_and_retrieve_it_later(self):
        # User starts program with path to pdf file
        path_pdf= os_path.join(
            os_path.dirname(__file__), 'input_files\*PROD [GASOIL][GASOIL][GASOIL].pdf')
        # this dir must include pdftotext.exe:

        argv[0] = os_path.join(os_path.dirname(os_path.dirname(__file__)), 'scrxPDF')
        argv[1:] = ['-v']
        scrxPDF()

        argv[1:] = ['-h']
        scrxPDF()

        argv[0] = os_path.join(os_path.dirname(os_path.dirname(__file__)), 'scrxPDF')
        argv[1:] = ['--path', path_pdf, ]
        scrxPDF()
        # It finds 30 files and parse them. Result saved to
        #D:\Work\_Python3\And0K\scraper3\12200_PROD GAS+.csv.csv

if __name__ == '__main__':  #
    unittest.main() #warnings='ignore'