# Run the build process by entering 'setup.py py2exe' or
# 'python setup.py py2exe' in a console prompt.
#
# If everything works well, you should find a subdirectory named 'dist'
# containing some files, among them hello.exe and test_wx.exe.


from distutils.core import setup
import py2exe
import sys #; sys.exit()
sys.path.insert(0, '../..')
"""
required_data_files = [('pdftotext.exe',)]
"""
setup(
    console = ["scrxPDF1707.py"],
    data_files=[('.', ['pdftotext.exe', 'pdftotext64.exe'])]
    )

"""
setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "0.0.1",
    description = "parse well production report pdf",
    name = "scraper from Andrey Korzh <ao.korzh@gmail.ru>",

    # targets to build
    console = ["scrxPDF1707.py"] #,
    #options = {"py2exe": {"compressed": 1,
    #                       "optimize": 2}}
    #,"skip_archive": True
    #   		}
    )
"""