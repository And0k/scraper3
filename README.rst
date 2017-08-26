scrxPDF1707 version 0.1.2
=========================

Program extracts oil and gas production data from specific format of 
Monthly Production Reports ``*.pdf`` files and saves data to ``*.csv`` file.

----

Program converts each found pdf file line by line to text strings by using the GPL
`Xpdf software <http://www.foolabs.com/xpdf/>`_ copyrighted 1996-2014 Glyph & Cog, 
LLC (email: derekn@foolabs.com).

This text is parsed checks by using regular expressions. Program has ability to 
configure regular expressions to some extent.

Configuration
-------------
Program has command line arguments that start with '--' (eg. --path) and can
also be set in a config file (scrxPDF1707.ini)
If an argument is specified in more than one place, then command line values
override config file values which override defaults.

Main parameters:

--path:  Path to pdf file or dir with pdf files to parse. Use patterns in Unix shell style.
         Can be specified in [input_files] section of configuration file.

--tasks_list:  Regular expressions names list. This is list of rows to parse.
         Each task must have regular expression "re_<Name>" (see below). Empty items is for skip lines without warning (besides of empty lines which skipped silently
         Default is "County_Quad_Pool, Buyer_Lease_Type_Active, , Permit_Well_header, Permit_Well, Permit_Well_end, Product_by_month_header, Product_by_month"

--"re_<Name>":  regular expressions for each task where <Name> is name of task listed in tasks_list

--out_path:  Path to output ``csv`` file. It can be specified in [output_files] section of configuration file.
         Here can be used <File_in> special string to substitute with ``1st file name+``.
         If no extension provided then ".csv" will be used. If file with generated name exists, then "_(N)" will be appended, where N = 1,2,3... is changed to generate new name.

--log:  dir/path of log relative to output path. It can be specified in [program] section of configuration file.

Text ``<prog>`` will be replaced with program name.

For more help and to list default parameters:

- run scrxPDF1707.exe -h

----

Мail to <ao.korzh@gmail.com>
