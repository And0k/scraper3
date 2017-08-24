scrxPDF1707 version 0.0.1
=======================

A project intended to extract oil and gas production data for use in Hart Energy Publishing, LLLP.
scrxPDF1707 extracts data from speific format of Monthly Production Reports *.pdf to *.csv file(s)

Program uses the GPL Xpdf software copyrighted 1996-2014 Glyph & Cog, LLC.
(Email: derekn@foolabs.com, `WWW: <http://www.foolabs.com/xpdf/>`)

----

Program converts pdf file line by line to text strings and checks them using
regular expressions. Has ability to configurate regular expressions to some extent.
Program has command line arguments that start with '--' (eg. --path) and can
also be set in a config file (scrxPDF1707.ini)
If an argument is specified in more than one place, then commandline values
override config file values which override defaults.

For help run
scrxPDF1707.exe -h

[input_files] section of configurtion file can has settings:
path - Path to pdf file or dir with pdf files to parse. Use patterns in Unix shell style

Regular expressions names list:
County_Quad_Pool, Buyer_Lease_Type_Active, , Permit_Well_header, Permit_Well, , Product_by_month_header, Product_by_month

Program  using configuration file

2. Parses this page and all pages with header "Company Well Name..." obtaining data
according to table logic structure and my empiric format restrictions:
Company, Pool, Well, Location, County, File, Oil, Wtr, Days, Runs, Gas, Gas_Sold, Total
3. Adds columns:
Oil_SI - gets value of Oil if it is not digit (in this case Oil value will set to 0)
Is_Total - specifies which data sum writes to column Total
4. Removes extra spaces in names and duplicate data in adjacent rows
3. Writes *.csv to specified dir. If file with generated name exists, then _(#) will be appended.
Logs to console and file "&scrxpdf.log"
---------------------------------------------------------------------------

Usage:

Put *.pdf reports to .\pdf directory
start:
scrxPDF.bat          - to write into separate <name of pdf>.csv files, or
scrxPDF all_to_1.bat - to write into one <name of first pdf>+.csv file
*.csv files and log will be in .\csv directory

For help of available and default options run in .\bin directory:
scrxPDF -h

