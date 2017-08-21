# Run the build process by entering 'setup.py py2exe' or
# 'python setup.py py2exe' in a console prompt.
#
# If everything works well, you should find a subdirectory named 'dist'
# containing some files, among them hello.exe and test_wx.exe.


from distutils.core import setup
import py2exe
import sys #; sys.exit()
#sys.path.insert(0, 'd:\\Work\\_Python\\_fromMat')
#sys.path.append('d:\\Work\\_Python\\_fromMat')
"""
wd_path = 'C:\\Python27\\Lib\\site-packages\\selenium\\webdriver'
required_data_files = [('selenium/webdriver/firefox',
                        ['{}\\firefox\\webdriver.xpi'.format(wd_path),
                        '{}\\firefox\\webdriver_prefs.json'.format(wd_path)])]
"""

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "0.0.1",
    description = "scrape/combine files from one cite",
    name = "scraper from Andrey Korzh <korzh@nextmail.ru>",

    # targets to build
    console = ["scraper(api).py", "filejoin(api).py"], #, "filejoin.py"
    options = {"py2exe": {
                 'includes': ['lxml.etree', 'lxml._elementpath'],
                 "compressed": 1, 
                 "optimize": 2,
                 "excludes": ['scipy', 'pandas', 'numpy'] 
              }}

    )