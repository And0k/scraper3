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
If an argument is specified in more than one place, then command line values
override config file values which override defaults.

Main parameters:
path: Path to pdf file or dir with pdf files to parse. Use patterns in Unix shell style.
Can be specified in [input_files] section of configuration file.

tasks_list: Regular expressions names list. This is list of rows to parse.
Each task must have regular expression "re_<Name>" (see below).
Empty items is for skip lines without warning (besides of empty lines which skipped silently
Default is "County_Quad_Pool, Buyer_Lease_Type_Active, , Permit_Well_header, 
Permit_Well, Permit_Well_end, Product_by_month_header, Product_by_month"

"re_<Name>": Regular expressions for each task where <Name> is name of task listed in tasks_list

out_path: Path to csv output. It can be specified in [output_files] section of configuration file.
Here can be used <File_in> special string to substitute with "1st file name"+.
If no extension provided then ".csv" will be used. If file with generated name exists, then it
 _(N) will be appended, where N is changed= 1,2,3... to generate new name.

log: dir/path of log relative to output path. It can be specified in [program] section of configuration file.

<prog> text will be replaced with program name.

For more help and to list default parameters run
scrxPDF1707.exe -h





