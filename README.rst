scrxPDF1707 version 0.0.1
=======================

A project intended to extract oil and gas production data for use in Hart Energy Publishing, LLLP.
scrxPDF1707 extracts data from Monthly Production Reports *.pdf to *.csv file(s)

Program uses the GPL Xpdf software copyrighted 1996-2014 Glyph & Cog, LLC.
(Email: derekn@foolabs.com, `WWW: <http://www.foolabs.com/xpdf/>`)

----

1. Gets Year and Month from table name "Monthly Production Reports <date>"
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

