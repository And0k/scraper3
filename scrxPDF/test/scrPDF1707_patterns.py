#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Purpose:  patterns tests
  Author:   Andrey Korzh <ao.korzh@gmail.com>
  Created:  08.08.2017
"""
import re

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
        "0012229"],                         #bad Well
        "((?P<Permit>[^ ]{1,10})| )((?: +(?P<Well>.*))|$)")

    re_match_and_print([  # Product_by_month_header
        "  Year  Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep  Oct  Nov  Dec  Totals"],
        "(?P<nodata> *Year +Jan +Feb +Mar +Apr +May +Jun +Jul +Aug +Sep +Oct +Nov +Dec +Totals)")

    re_match_and_print([  # Product_by_month
        "  2011  0  0  0  0  0  0  0  0  0  0  655  4865  5520",
        "  2012  9722  9318  9304.8  6100.7  8069.6  7167  7579  7379  6712  6640  836  6122.4  84950.5",
        "  2014  0  0  103.95  0  0  0  134.55  0  0  0  0  250.49  488.99",
        "  Totals  20138  18529  19350.8  15773.7  17159.6  16670  16364  17016  14957  15899  10168.2  18953  200978.3",
        "  Totals  0  0  103.95  0  0  0  134.55  0  0  0  0  250.49  488.99"
    ],
        " *(?P<Year>\d{2,4}|Totals) +(?P<Jan>[\d.]{1,10}) +(?P<Feb>[\d.]{1,10})"
        " +(?P<Mar>[\d.]{1,10}) +(?P<Apr>[\d.]{1,10}) +(?P<May>[\d.]{1,10})"
        " +(?P<Jun>[\d.]{1,10}) +(?P<Jul>[\d.]{1,10}) +(?P<Aug>[\d.]{1,10})"
        " +(?P<Sep>[\d.]{1,10}) +(?P<Oct>[\d.]{1,10}) +(?P<Nov>[\d.]{1,10})"
        " +(?P<Dec>[\d.]{1,10}) +(?P<Totals>[\d.]{1,10})")


if __name__ == '__main__':  #
    test_patterns()

# "(Buyer: +(?P<Buyer>.*?(?=([, ]+(Buyer's|) *Lease#):)))|(.*)"
            # "([, ]+(Buyer's|) *Lease#: +(?P<Lease>.*?(?= +Production)))|(.*) +"
            # "(Buyer: +(?P<Buyer>[^ ].+?(?=( +Buyer's|( *) Lease#):)))|(.*)[, ]+(Buyer's Lease#: +(?P<Lease>.*?))|(.*?) +"