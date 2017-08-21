#! /usr/bin/env python
# -*- coding: utf-8 -*-


from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, \
StaleElementReferenceException, NoSuchWindowException, TimeoutException, \
WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from socket import error as Socket_error
from http.client import BadStatusLine #error
import logging
import time
from os import path as os_path, listdir as os_listdir, rename as os_rename, remove as os_remove \
, environ as os_environ
from sys import argv as sys_argv
#from shutil import move
from re import sub as re_sub
import json
from lxml import etree

startName= "" #OTHA O. DEES ET UX #11-6 JWR 31-2-348 Aland-09-20-08-32-04-1927 24-13-20 #35031
byWellName= True

fileListAPI= "AL_API list.csv"
strURL= "http://www2.gsa.state.al.us/ogb/wellrecords.aspx?PERMIT=&API="
maxTimeOfFileDownloading_s=200 #s
maxTimeOfFileDownloadingStart_s=10 #s
path_geckodriver= os_path.join(os_path.dirname(os_path.realpath(sys_argv[0])),
    'geckodriver64.exe' if 'PROGRAMFILES(X86)' in os_environ and os_path.isfile(
        r'c:\Program Files\Mozilla Firefox\firefox.exe')
    else 'geckodriver.exe')
if not os_path.isfile(path_geckodriver):
    raise IOError(path_geckodriver + ' not found')

def init(byWellName, outDir):
    global dirSave, dirTemp, fileOptionsF
    global l
    nameAdd= ""
    dirSave= os_path.join(os_path.abspath(outDir), strURL.partition(
        '.aspx')[0].partition('://')[-1].replace('/','-'))+nameAdd
    dirTemp= os_path.join(dirSave,'temp')

        #b_dirSaveCreated= True
    #else:
        #b_dirSaveCreated= False

    # Logging
    logging.basicConfig(filename=os_path.join(outDir, '&scraper_api'+nameAdd+'.log'),
                        format='%(asctime)s %(message)s', level=logging.INFO)
    # set up logging to console - warnings only
    console= logging.StreamHandler()
    console.setLevel(logging.WARN)
    # set a format which is simpler for console use
    formatter= logging.Formatter('%(message)s') #%(name)-12s: %(levelname)-8s ...
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    l = logging.getLogger(__name__)

    #if b_dirSaveCreated:
    if not os_path.isdir(dirSave):
        os_path.os.mkdir(dirSave)
        l.warninig('dir "%s" created to fill with data', dirSave)
    if not os_path.isdir(dirTemp):
        os_path.os.mkdir(dirTemp)
    fileOptionsF= os_path.join(outDir,  fileListAPI) #'&options' + nameAdd + '.json'



def browserInit(browser = None):

    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList",2)
    fp.set_preference("browser.download.manager.showWhenStarting",False)
    fp.set_preference("browser.download.dir", dirTemp)

    #fp.set_preference("browser.helperApps.neverAsk.openFile", "")
    fp.set_preference("browser.helperApps.neverAsk.openFile","application/excel")
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/xls,application/vnd.ms-excel,application/xml,application/x-msexcel,application/excel,application/x-excel,text/csv,text/plain,text/xml,image/png,image/jpeg,text/html,text/plain,application/msword,application/xml")
    fp.set_preference("browser.helperApps.alwaysAsk.force", False)
    fp.set_preference("browser.download.manager.focusWhenStarting", False)

    # Disable CSS (may couse side effects)
    fp.set_preference('permissions.default.stylesheet', 2)
    # Disable images
    fp.set_preference('permissions.default.image', 2) #not works?
    # Disable Flash
    fp.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

    #if want use the firefox extension quickjava
    #(https://addons.mozilla.org/en-us/firefox/addon/quickjava/):
    '''
    fp.add_extension(folder_xpi_file_saved_in + "\\quickjava-2.0.6-fx.xpi")
    fp.set_preference("thatoneguydotnet.QuickJava.curVersion", "2.0.6.1") ## Prevents loading the 'thank you for installing screen'
    fp.set_preference("thatoneguydotnet.QuickJava.startupStatus.Images", 2)  ## Turns images off
    fp.set_preference("thatoneguydotnet.QuickJava.startupStatus.AnimatedImage", 2)  ## Turns animated images off

    fp.set_preference("thatoneguydotnet.QuickJava.startupStatus.CSS", 2)  ## CSS
    fp.set_preference("thatoneguydotnet.QuickJava.startupStatus.Cookies", 2)  ## Cookies
    fp.set_preference("thatoneguydotnet.QuickJava.startupStatus.Flash", 2)  ## Flash
    fp.set_preference("thatoneguydotnet.QuickJava.startupStatus.Java", 2)  ## Java
    fp.set_preference("thatoneguydotnet.QuickJava.startupStatus.JavaScript", 2)  ## JavaScript
    fp.set_preference("thatoneguydotnet.QuickJava.startupStatus.Silverlight", 2)



# other settings variant:
    fp.set_preference("network.http.pipelining", True)
    fp.set_preference("network.http.proxy.pipelining", True)
    fp.set_preference("network.http.pipelining.maxrequests", 8)
    fp.set_preference("content.notify.interval", 500000)
    fp.set_preference("content.notify.ontimer", True)
    fp.set_preference("content.switch.threshold", 250000)
    fp.set_preference("browser.cache.memory.capacity", 65536) # Increase the cache capacity.
    fp.set_preference("browser.startup.homepage", "about:blank")
    fp.set_preference("reader.parse-on-load.enabled", False) # Disable reader, we won't need that.
    fp.set_preference("browser.pocket.enabled", False) # Duck pocket too!
    fp.set_preference("loop.enabled", False)
    fp.set_preference("browser.chrome.toolbar_style", 1) # Text on Toolbar instead of icons
    fp.set_preference("browser.display.show_image_placeholders", False) # Don't show thumbnails on not loaded images.
    fp.set_preference("browser.display.use_document_colors", False) # Don't show document colors.
    fp.set_preference("browser.display.use_document_fonts", 0) # Don't load document fonts.
    fp.set_preference("browser.display.use_system_colors", True) # Use system colors.
    fp.set_preference("browser.formfill.enable", False) # Autofill on forms disabled.
    fp.set_preference("browser.helperApps.deleteTempFileOnExit", True) # Delete temprorary files.
    fp.set_preference("pdfjs.disabled", True)
	fp.set_preference("browser.shell.checkDefaultBrowser", False)
    fp.set_preference("browser.startup.homepage", "about:blank")
    fp.set_preference("browser.startup.page", 0) # blank
    fp.set_preference("browser.tabs.forceHide", True) # Disable tabs, We won't need that.
    fp.set_preference("browser.urlbar.autoFill", False) # Disable autofill on URL bar.
    fp.set_preference("browser.urlbar.autocomplete.enabled", False) # Disable autocomplete on URL bar.
    fp.set_preference("browser.urlbar.showPopup", False) # Disable list of URLs when typing on URL bar.
    fp.set_preference("browser.urlbar.showSearch", False) # Disable search bar.
    fp.set_preference("extensions.checkCompatibility", False) # Addon update disabled
    fp.set_preference("extensions.checkUpdateSecurity", False)
    fp.set_preference("extensions.update.autoUpdateEnabled", False)
    fp.set_preference("extensions.update.enabled", False)
    fp.set_preference("general.startup.browser", False)
    fp.set_preference("plugin.default_plugin_disabled", False)
    fp.set_preference("permissions.default.image", 2) # Image load disabled again

    '''



    fp.set_preference("browser.link.open_newwindow", 2) # tabs instead windows #not works?

    fp.set_preference("browser.startup.homepage_override.mstone", "ignore") #not works?
    fp.set_preference("startup.homepage_welcome_url.additional",  "about:blank") #not works?
    #fp.update_preferences()
    try:
        if browser:
            browser.close()
    except:
        pass
    driver = webdriver.Firefox(firefox_profile=fp, executable_path=path_geckodriver) # Get local session of firefox
    driver.implicitly_wait(10)
    return driver

#----------------------------------------------------------------------
def addNumberIfNonUnique(filename_newF, filename_new= None, filenameE= None):
    """
    Set unique file name. Change file name by adding '_(N)' before extension if
    needed.

    addNumberIfNonUnique(filename_newF) - autofinds filename_new and filenameE
    """
    if filename_new is None:
        filename_new= os_path.basename(filename_newF)
        filenameE= os_path.splitext(filename_new)[1]
    m= 1
    filename_new_orig_no_ext= os_path.splitext(filename_new)[0]
    while os_path.isfile(filename_newF): #rename while target exists
        filename_new= filename_new_orig_no_ext + '_(' + str(m) + ')' + filenameE
        filename_newF= os_path.join(dirSave, filename_new)
        m+=1
    return filename_newF, filename_new

def page_prepare(strURL, bVerbose = False):
    """"""
    global NoSuchElementException, StaleElementReferenceException, TimeoutException
    global browser
    elem1= None
    for n_timeout_exceptions_allow in range(3):
        if bVerbose: print('go to ' + strURL, end='.')
        try:
            browser.get(strURL) # Load page
            time.sleep(0.1)     # Let the page load, will be added to the API
            if not "Well Records" in browser.title:
                time.sleep(0.5)
                raise TimeoutException("Error - Page is not opened!")
            elem1 = browser.find_element_by_xpath("id('ReportViewer1_ctl05')") #for id('ReportViewer1_ctl05_ctl04_ctl00_Menu')/x:div[1]/x:a get selenium.common.exceptions.InvalidSelectorException
            break
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
            l.warninig(e.msg)
        except Socket_error as e:
            l.warninig(e.msg)
            browser= browserInit(browser)
    return elem1
    #time.sleep(9)

def download_option(str_opt):
    '''
    Inputs 'str_opt' in page, finds corresponding data and clicks to save
    '''
    global NoSuchElementException, StaleElementReferenceException, TimeoutException
    global browser
    elem1= page_prepare(strURL + str_opt)
    if str_opt not in browser.current_url: #strURL
        raise TimeoutException("Error - Page is not opened!")
    # except Sys.InvalidOperationException

    # Check temp download folder - should be empty
    files_set= set() # files which can not (re)move
    for filename in os_listdir(dirTemp):
        filenameF= os_path.join(dirTemp,filename)
        try:
            if os_path.getsize(filenameF)>20: #move nonempty files and prefix "_"
                filename_newF,filename_new = addNumberIfNonUnique(os_path.join(
                    dirSave, '_'+filename))
                os_rename(filenameF, filename_newF)
                l.warning("- check: old file (" + filename_new + ") found!")
                #break
            else:
                os_remove(filenameF) #delete strange empty files
                print('z', end='')
        except:
            files_set.add(filename)

    # Download data
    try:
        browser.execute_script("$find('ReportViewer1').exportReport('Excel')")
        if not elem1.is_displayed():
            raise TimeoutException("Error - Page was not opened!")
    except (StaleElementReferenceException, NoSuchElementException) as e:
        raise TimeoutException(" - No such control on page!")


    #try:# Find data character
        ##browser.implicitly_wait(2)
        ##if byWellName:
        #elemTest = WebDriverWait(browser, 2).until(
        #EC.presence_of_element_located((By.XPATH, "//form//tr[th='Pool Name']")))
        ##else:
            ##elemTest = WebDriverWait(browser, 2).until(
            ##EC.presence_of_element_located((By.XPATH, "//th")))
    #except TimeoutException:
        #raise TimeoutException(" - Page have not data table for option")
    #finally:
        #browser.implicitly_wait(10)

    #browser.find_element_by_name("btn_export") # Find button Export

    # Looping until file is retrieved
    time.sleep(1)
    msgFile= ''
    for t in range(maxTimeOfFileDownloading_s):
        #monitor chenged folder contents
        files_set_upd= set()
        for filename in os_listdir(dirTemp):
            files_set_upd.add(filename)
        if len(files_set):
            files_set_upd.difference_update(files_set)
        L= len(files_set_upd)
        try:
            if L==1:
                filename = files_set_upd.copy().pop()
            elif L>1: #temporary?
                filename = max(list(files_set_upd), key= lambda ff: os_path.getmtime(
                               os_path.join(dirTemp,ff)))
            elif L==0:
                if not elem1.is_displayed():
                    raise TimeoutException("Page changed?")
                else:
                    if t > maxTimeOfFileDownloadingStart_s:
                        raise TimeoutException("Page changed?") #elem1= page_prepare(strURL + str_opt)
                    print('.', end='')
                    time.sleep(0.5)
                    continue
            if os_path.splitext(filename)[1]=='.part':
                print("'", end='')
                time.sleep(0.5)
                continue
            elif L==1:
                break
            else:
                print("What's the Hell? ", end='')
                if not elem1.is_displayed():
                    raise TimeoutException("Page changed?")
                time.sleep(0.1)
                break
        except (ValueError, WindowsError): # may be if file moves/renames between getting file name and checking it
            print('.', end='')
            time.sleep(1)
            filename= ""
    if L==0 or filename=="":
        raise TimeoutException('No file')
    # move this file
    filenameE= os_path.splitext(filename)[1]
    if filenameE!='.part':
        filenameF= os_path.join(dirTemp,filename)
        for t in range(100): #more wait
            try:
                filename_new= re_sub("[^\s\w\-\+#&,;\.\(\)']+", "_", str_opt)+filenameE
                filename_newF= os_path.join(dirSave,filename_new)
                filename_newF, filename_new= addNumberIfNonUnique(
                    filename_newF, filename_new, filenameE)
                if os_path.getsize(filenameF)>10:    # check size
                    os_rename(filenameF, filename_newF)
                    msgFile= " > " + filename_new
                    time.sleep(0.5)
                    break
                else:
                    print('Z', end='')
                    time.sleep(1)
            except WindowsError:
                print('*', end='')
                time.sleep(1)
        #except Exception as e:
    else:
        raise(TimeoutException(' - Partial download'))
    return(msgFile)

def main(startName= startName):
    '''
    do it
    '''
    global NoSuchElementException, StaleElementReferenceException, TimeoutException
    global browser
    msg= 'init error'
    browser= browserInit()
    try:

        bRetrieveAllOptions= not os_path.isfile(fileOptionsF)
        if bRetrieveAllOptions:
            raise IOError('No options list. No method implemented to obtain it.')
        else:
            #load options
            with open(fileOptionsF, 'rt') as f: #r
                #tr_option_values= json.load(f)
                tr_option_values = [f.readline().rstrip('\n')] # skip header
                tr_option_values = [line.rstrip('\n') for line in f]
            L= len(tr_option_values)
            if startName and startName[0]=='*': # remove existed files
                startName= ''
                files_set_upd= set(tr_option_values)
                files_set= set([os_path.splitext(filename)[0] for filename in os_listdir(dirSave)])
                files_set_upd.difference_update(files_set)
                tr_option_values = sorted(files_set_upd)
                print(' Loading {0} options (of {1})'.format(len(files_set_upd), L))
            else:
                print(' Loaded {0} options from file'.format(L))


        k= 0
        for k,str_opt in enumerate(tr_option_values):
            if startName:
                if str_opt==startName:
                    startName= ""
                else:
                    continue
            msg= '{index:6d}. {option} '.format(index= k+1, option= str_opt)
            print(msg, end='')
            n_timeout_exceptions_allow= 3
            while True:
                msg_option= ''
                try:
                    msg_option= download_option(str_opt)
                except NoSuchElementException as e:
                    msg_option= " - data not found"
                    l.warninig(msg + msg_option + e.msg)
                    break
                except (TimeoutException, WebDriverException) as e:
                    n_timeout_exceptions_allow-=1 #Try times decrease
                    if n_timeout_exceptions_allow>0:
                        msg_option= " - Error: control not found? retry..."
                        l.warninig(msg + e.msg + msg_option)
                        elem1= page_prepare(strURL + str_opt, bVerbose = True)
                    else:
                        msg_option= "\n- Failed."
                        l.warninig(msg + e.msg + msg_option)
                        break
                except (Socket_error, BadStatusLine, NoSuchWindowException, WebDriverException) as e:
                    n_timeout_exceptions_allow-=1 #Try times decrease
                    if n_timeout_exceptions_allow>0:
                        msg_option= " - Error: browser not found? retry..."
                        l.warninig(msg + (e.msg if hasattr(e,'msg') else '') + msg_option)
                        browser= browserInit(browser)
                        elem1= page_prepare(strURL + str_opt, bVerbose = False)
                    else:
                        msg_option= "\n- Failed."
                        l.warninig(msg + (e.msg if hasattr(e,'msg') else '') + msg_option)
                        break
                except Exception as e:
                    msg_option= "\n- Failed. Unknown error"
                    l.warninig(msg + (e.msg if hasattr(e,'msg') else '') + msg_option)
                else:
                    l.info(msg + msg_option)
                    print(msg_option)
                    break

        l.info("Ok!"); print("Ok!", end='')
    except Exception as e:
        l.warninig(' {}{} {}'.format(msg, ': ' + e.msg + ',' if hasattr(e,'msg') else '',
                                  msg_option))
    finally:
        try:
            l.handlers[0].flush()
            #browser.close()
            browser.quit()
        except:
            pass

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description= '''
1. Opens browser (requires Mozilla Firefox version >= 52.0.3 to be installed)
2. Tries to download data for each "AL_API list.csv" item (this list must be present in current directory).
If starts with first command line argument "*" then already existed files will be skipped.
Else if same name exists, then _(#) will be appended.
Logs to console and file "&scraper(api).log"
''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        version= '0.0.1 - © 2016 Andrey Korzh <ao.korzh@gmail.com>'
    )

    parser.add_argument('startName', nargs='?', type= str, default= "",
                        help='start data download cycle from this name, empty ("") means from first')
    parser.add_argument('outDir', nargs='?', type= str, default='.',
                        help='output dir path')
    args = parser.parse_args()

    init(byWellName= byWellName, outDir= args.outDir)
    main(startName= args.startName)
else:
    init(byWellName= byWellName, outDir= r"d:\DDownloads\scraper")

"""
try:
   browser.find_element_by_name('GridView1')
   #find_element_by_xpath("//a[contains(@href,'http://seleniumhq.org')]")
except NoSuchElementException:
   assert 0, "can't find seleniumhq"
"""
#options_all = browser.find_elements_by_xpath("//select/option") # Find all options
#all_options.send_keys(Keys.RETURN) ARROW_UP
#all_options = browser.find_element_by_name("lstbox_permit") # Find the query box