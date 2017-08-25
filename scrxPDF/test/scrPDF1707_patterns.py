#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Purpose:  patterns tests
  Author:   Andrey Korzh <ao.korzh@gmail.com>
  Created:  08.08.2017
"""
import re
from scraper3.scrxPDF.scrxPDF1707 import *

def none_in_dict(r):
    keys_of_None = [k for k, v in r.items() if v is None]
    if any(keys_of_None):
        print('Bad ID for field(s)' + str(keys_of_None))

def re_match_and_print(data_rows, regex):
    for line in data_rows:
        r = re.match(regex, line).groupdict()
        print(r)
        none_in_dict(r)

def test_patterns():
    re_match_and_print([  # County_Quad_Pool
        "Morgan County; GOBEY Quad; Unassigned Field Pool",
        "County;  Quad;   Field Pool"],
        " *(?P<County>.*?)(?: *County;) +(?P<Quad>.*?)(?: *Quad;)"
        " +(?P<Pool>.*?)(?: +Field +Pool.*)$")

    re_match_and_print([  # Buyer_Lease_Type_Active
        "Buyer:  B&W  Buyer's  Lease#: Production     Type      Gas      Production Unit",
        "Buyer:  Regal Petroleum Company Buyer's  Lease#: 78755  Production  Type  Oil  Production Unit",
        "Buyer:  B&W      Lease#: Production     Type      Gas      Production Unit"
    ],
        "(?:Buyer: +)(?P<Buyer>.*?)(?:,? *(Buyer's|) *Lease#: +)(?P<Lease>.*?)(?: *Production +Type +)(?P<Type>[^ ]*?)(?: *Production +Unit.*| .*|$)")

    re_match_and_print([  # Permit_Well_header
        "Permit        Well Name",
        "Permit #      Well Name"],
        "(?P<nodata>Permit +#? +Well +Name)")

    re_match_and_print([  # Permit_Well
        "0012218       Corrigan TLP, LLC #DPI-211",
        "0012201        WPP, LLC #DPI 213",
        "              John V. Baird #1-H", #bad Permit
        "0012229",                          #bad Well
        "                     Edit   Wells"            #bad because end of table
    ],
        #"((?P<Permit>[^ ]{1,10})| )((?: +(?P<Well>.*))|$)"
        "(?! *Edit)((?P<Permit>[^ ]{1,10})| {8})((?: +(?P<Well>.*))|$)")

    re_match_and_print([  # Product_by_month_header
        "  Year  Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep  Oct  Nov  Dec  Totals"],
        "(?P<nodata> *Year +Jan +Feb +Mar +Apr +May +Jun +Jul +Aug +Sep +Oct +Nov +Dec +Totals)")

    re_match_and_print([  # Product_by_month
        "  2011  0  0  0  0  0  0  0  0  0  0  655  4865  5520",
        "  2012  9722  9318  9304.8  6100.7  8069.6  7167  7579  7379  6712  6640  836  6122.4  84950.5",
        "  2014  0  0  103.95  0  0  0  134.55  0  0  0  0  250.49  488.99",
        "  Totals  20138  18529  19350.8  15773.7  17159.6  16670  16364  17016  14957  15899  10168.2  18953  200978.3",
        "  Totals  0  0  103.95  0  0  0  134.55  0  0  0  0  250.49  488.99"
        "2007         485    130#3 #######     1397.8#6 ###############        "
        #         Aug      Sep      Oct      Nov       Dec      Totals
        "983.939  923.772  838.573  874.012  784.833   797.913  11952.12",
        "2008    760.309     643.608  758.666  704.103       650.632  616.354  "
        "569.145  568.953  542.855  621.403  531.416   523.859  7491.303"
    ],
        " *(?P<Year>\d{2,4}|Totals) +(?P<Jan>[\d.]{1,10}) +(?P<Feb>[\d.]{1,10})"
        " +(?P<Mar>[\d.]{1,10}) +(?P<Apr>[\d.]{1,10}) +(?P<May>[\d.]{1,10})"
        " +(?P<Jun>[\d.]{1,10}) +(?P<Jul>[\d.]{1,10}) +(?P<Aug>[\d.]{1,10})"
        " +(?P<Sep>[\d.]{1,10}) +(?P<Oct>[\d.]{1,10}) +(?P<Nov>[\d.]{1,10})"
        " +(?P<Dec>[\d.]{1,10}) +(?P<Totals>[\d.]{1,10})")

    re_match_and_print([  # Product_by_month
        " 2007         485    130#3 #######     1397.8#6 ###############        "
        #12345678123456789123456789A123456789123456789123456789123456789A
        "983.939  923.772  838.573  874.012  784.833   797.913  11952.12",
        " 2008    760.309     643.608  758.666  704.103       650.632  616.354  "
        "569.145  568.953  542.855  621.403  531.416   523.859  7491.303"
        " 2007    1567        129#6 #######     1366.3#5 #######################"
        "########################################               15668.25"
        " 2012    13190       13158         13023  8201    10835   9523.6###  ##"
        "###    10385   9521.17       9341  8177.74   8161.9   123879.6"
        " 2007         485    1303###  #####    1397.86###    ########  #####   "
        " 983.939  923.772  838.573  874.012  784.833   797.913  11952.12"
        " 2008 ###  ########  ########  ########  #####       968.633   915.019 "
        "  911.203   859.564   597.718   942.347      796.64  845.712  11197.35"
        "1994    613.69   751.49   840.39   606.03   805.11   400.33   591.13  "
        " 575.42   603.93   487.92   344.02   0        6619.46"
        " Totals       98          121  157.5           43  38.53        44.6    "
        "   0  33.35          0       56      44.7  224.39        861.07"
    ],
        " *(?P<Year>[\d.#]{2,4}[\d.]|Totals)(?: {1,13}|)"
        "(?P<Jan>[\d.]{,9})(?:#{,9})(?: {1,13}|)"
        "(?P<Feb>[\d.]{,9})(?:#{,9})(?: {1,13}|)"
        "(?P<Mar>[\d.]{,9})(?:#{,9})(?: {1,13}|)"
        "(?P<Apr>[\d.]{,9})(?:#{,9})(?: {1,13}|)"
        "(?P<May>[\d.]{,9})(?:#{,9})(?: {1,13}|)"
        "(?P<Jun>[\d.]{,9})(?:#{,9})(?: {1,13}|)"
        "(?P<Jul>[\d.]{,9})(?:#{,9})(?: {1,13}|)"
        "(?P<Aug>[\d.]{,9})(?:#{,9})(?: {1,13}|)"
        "(?P<Sep>[\d.]{,9})(?:#{,9})(?: {1,13}|)"
        "(?P<Oct>[\d.]{,9})(?:#{,9})(?: {1,13}|)"
        "(?P<Nov>[\d.]{,9})(?:#{,9})(?: {1,13}|)"
        "(?P<Dec>[\d.]{,9})(?:#{,9})(?: {1,15}|)"
        "(?P<Totals>[\d.]{1,10})(?:#{,10})$"

    )
if __name__ == '__main__':  #
    test_patterns()
"""

" *(?P<Year>[\d.#]{2,4}[\d.#]|Totals)(?: {1,13}|)"
                "(?P<Jan>[\d.#]{1,9})(?: {1,13}|)"
                "(?P<Feb>[\d.#]{1,9})(?: {1,13}|)"
                "(?P<Mar>[\d.#]{1,9})(?: {1,13}|)"
                "(?P<Apr>[\d.#]{1,9})(?: {1,13}|)"
                "(?P<May>[\d.#]{1,9})(?: {1,13}|)"
                "(?P<Jun>[\d.#]{1,9})(?: {1,13}|)"
                "(?P<Jul>[\d.#]{1,9})(?: {1,13}|)"
                "(?P<Aug>[\d.#]{1,9})(?: {1,13}|)"
                "(?P<Sep>[\d.#]{1,9})(?: {1,13}|)"
                "(?P<Oct>[\d.#]{1,9})(?: {1,13}|)"
                "(?P<Nov>[\d.#]{1,9})(?: {1,13}|)"
                "(?P<Dec>[\d.#]{1,9})(?: {1,15}|)"
                "(?P<Totals>[\d.#]{1,11})$")

# "(Buyer: +(?P<Buyer>.*?(?=([, ]+(Buyer's|) *Lease#):)))|(.*)"
            # "([, ]+(Buyer's|) *Lease#: +(?P<Lease>.*?(?= +Production)))|(.*) +"
            # "(Buyer: +(?P<Buyer>[^ ].+?(?=( +Buyer's|( *) Lease#):)))|(.*)[, ]+(Buyer's Lease#: +(?P<Lease>.*?))|(.*?) +" 
            """