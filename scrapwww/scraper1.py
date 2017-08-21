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

strURL= "http://www2.gsa.state.al.us/ogb/production.aspx"
# "http://www.gsa.state.al.us/ogb/production.aspx"
maxTimeOfFileDownloading_s=200 #s

path_geckodriver= os_path.join(os_path.dirname(os_path.realpath(sys_argv[0])),
    'geckodriver64.exe' if 'PROGRAMFILES(X86)' in os_environ and os_path.isfile(
        r'c:\Program Files\Mozilla Firefox\firefox.exe')
    else 'geckodriver.exe')
if not os_path.isfile(path_geckodriver):
    raise IOError(path_geckodriver + ' not found')

def init(byWellName, outDir):
    global dirSave, dirTemp, fileOptionsF
    global l
    nameAdd= ('--wellnm' if byWellName else '--permit')
    dirSave= os_path.join(os_path.abspath(outDir), strURL.partition(
        '://')[-1].replace('/','-'))+nameAdd
    dirTemp= os_path.join(dirSave,'temp')

        #b_dirSaveCreated= True
    #else:
        #b_dirSaveCreated= False

    # Logging
    logging.basicConfig(filename=os_path.join(outDir, '&scraper'+nameAdd+'.log'),
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
        l.warn('dir "%s" created to fill with data', dirSave)
    if not os_path.isdir(dirTemp):
        os_path.os.mkdir(dirTemp)
    fileOptionsF= os_path.join(outDir, '&options' + nameAdd + '.json')



def browserInit():
    '''
    Opens Firefox browser
    # set something on the profile...
    :return: browser driver
    '''
    fp = webdriver.FirefoxProfile()

    fp.set_preference("browser.download.folderList",2)
    fp.set_preference("browser.download.manager.showWhenStarting",False)
    fp.set_preference("browser.download.dir", dirTemp)

    #fp.set_preference("browser.helperApps.neverAsk.openFile", "")
    fp.set_preference("browser.helperApps.neverAsk.openFile","application/excel")
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/xls,application/vnd.ms-excel,application/xml,application/x-msexcel,application/excel,application/x-excel,text/csv,text/plain,text/xml,image/png,image/jpeg,text/html,text/plain,application/msword,application/xml")
    fp.set_preference("browser.helperApps.alwaysAsk.force", False)
    fp.set_preference("browser.download.manager.focusWhenStarting", False)

    '''
    fp.set_preference("pdfjs.disabled", True)
    fp.set_preference("plugin.disable_full_page_plugin_for_types", "application/pdf")
    '''
    #fp.update_preferences()
    #firefox_capabilities=
    #gecko = os.path.normpath(os.path.join(os.path.dirname(__file__), 'geckodriver'))
    #binary = FirefoxBinary(r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe')
    #driver = webdriver.Firefox(firefox_binary=binary, executable_path=gecko + '.exe')
    #driver = webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.FIREFOX, browser_profile=fp
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

def page_prepare(strURL, bRetrieveAllOptions= True):
    """"""
    global NoSuchElementException, StaleElementReferenceException, TimeoutException
    global browser
    for n_timeout_exceptions_allow in range(3):
        print('go to ' + strURL, end='.')
        try:
            browser.get(strURL) # Load page
            time.sleep(0.1)     # Let the page load, will be added to the API
            assert "GSA" in browser.title
            if byWellName:
                elem1 = browser.find_element_by_xpath("//input[@value='rdo_wellnm']")
                elem1.click()

            #webdriver.execute_script("window.scrollTo(0, 0.9*document.body.scrollHeight);")
            elem1 = browser.find_element_by_xpath("//form//input[@type='text']")#find_element_by_name("txtbox_permit") # Find the query box
            if bRetrieveAllOptions:
                elem1.send_keys("%" + Keys.RETURN)
                #time.sleep(9)
                print('. Loading full options list...')
                options_box = browser.find_element_by_xpath("//form//option[1]") #find_element_by_name("lstbox_permit")   # Find the query box
                #options_box.click()

                html = browser.page_source
                tree = etree.fromstring(html, parser=etree.HTMLParser())
                tr_options_all = tree.xpath("//select/option")
                tr_option_values= sorted(set([list(option.values())[0] for option in tr_options_all]))
                str_print= 'found {0} distinct options (in {1})'.format(len(tr_option_values),len(tr_options_all))
                print(str_print)
                l.info(str_print)
                return(tr_option_values)
            else:
                return
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
            l.warn(e.msg)
        except Socket_error as e:
            l.warn(e.msg)
            browser= browserInit()
    #time.sleep(9)

def process_option(str_opt):
    '''
    Inputs 'str_opt' in page, finds corresponding data and clicks to save
    '''
    global NoSuchElementException, StaleElementReferenceException, TimeoutException
    global browser
    if strURL not in browser.current_url:
        raise TimeoutException("Error - Page is not opened!")
    try:
        elem1= browser.find_element_by_xpath("//form//input[@type='text']") # Find the query box
        elem1.clear()
        elem1.send_keys(str_opt + Keys.RETURN)

        dropdown= Select(browser.find_element_by_xpath('//form//select'))
        try:
            dropdown.select_by_value(str_opt)
        except NoSuchElementException:
            dropdown.select_by_index(0)
            dropdown= Select(browser.find_element_by_xpath('//form//select'))
            msgFile= str_opt
            str_opt= dropdown.options[0].get_attribute("value")
            l.warning("%s - not found in list, use 1st available: %s", msgFile, str_opt)

        '''

        #select = Select(WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//div[@id="operations_add_process_list_tab_groups_tab_standard_1"]//select'))))

        options0_now= WebDriverWait(browser, 100).until(
            EC.presence_of_element_located((By.XPATH, "//select/option[@value='"+str_opt+"']")))
        #browser.find_element_by_xpath("//select/option[@value="+str_opt+"]")
        options0_now.click()
        options0_now= WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//select/option[@value='"+str_opt+"']")))

        str_opt0_now= options0_now.get_attribute("value")
        if str_opt0_now<>str_opt:
            l.warning("Error - Values changed! " + str_opt + " -> " + str_opt0_now)
        #option.click()
        #str_opt= option.get_attribute("value")
        '''
    except (StaleElementReferenceException, NoSuchElementException) as e:
        raise TimeoutException(" - No such control on page!")

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

    # Fast skip if can guess that no data
    if byWellName:
        elemTest= browser.find_elements_by_xpath("//form//tr[th='Well Name']")
        if len(elemTest)==1:
            return(" - no data (skip)") #must be second tables to proceed
    else:
        try:
            browser.implicitly_wait(0.01)
            elemTest = browser.find_element_by_xpath("//tr[td='There are no production records for this well.']")
            browser.implicitly_wait(10)
            return(" - no data (skip)") #not need save
        except NoSuchElementException:
            pass # no indicators of absent data
        finally:
            browser.implicitly_wait(10)

    # Download data
    #elemTest = WebDriverWait(browser, 2).until(
        #EC.element_selection_state_to_be((By.XPATH, "//form//tr[th='Well Name']")))
    try:# Find data character
        browser.implicitly_wait(2)
        #if byWellName:
        elemTest = WebDriverWait(browser, 2).until(
        EC.presence_of_element_located((By.XPATH, "//form//tr[th='Pool Name']")))
        #else:
            #elemTest = WebDriverWait(browser, 2).until(
            #EC.presence_of_element_located((By.XPATH, "//th")))
    except TimeoutException:
        raise TimeoutException(" - Page have not data table for option")
    finally:
        browser.implicitly_wait(10)
    elemE = WebDriverWait(browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//form//input[@type='submit' and  @value='Export']")))
    #browser.find_element_by_name("btn_export") # Find button Export
    elemE.click() #send_keys(Keys.RETURN)
    time.sleep(0.2)

    # Looping until file is retrieved
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
            else:
                print('.', end='')
                time.sleep(1)
                continue
            if L==0:
                raise TimeoutException('No file')
            if os_path.splitext(filename)[1]=='.part':
                print('.', end='')
                time.sleep(1)
            else:
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
    try:
        msg = "Initialise browser."
        msg_option = " when starting browsing"
        browser = browserInit()
        bRetrieveAllOptions= not os_path.isfile(fileOptionsF)
        if bRetrieveAllOptions:
            msg = 'Getting all options'
            tr_option_values= page_prepare(strURL)
            #save options
            with open(fileOptionsF, 'w') as f:
                json.dump(tr_option_values, f)
            with open(fileOptionsF+'.txt', 'w') as f:
                f.write("\n".join(tr_option_values))
        else:
            msg = 'Getting remaining data'
            page_prepare(strURL, False)
            #load options
            with open(fileOptionsF, 'r') as f:
                tr_option_values= json.load(f)
                #tr_option_values = [line for line in f]
            print(' Loaded {0} options from file'.format(len(tr_option_values)))

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
                    msg_option= process_option(str_opt)
                except NoSuchElementException as e:
                    msg_option= " - data not found"
                    l.warn(msg + msg_option + e.msg)
                    break
                except TimeoutException as e:
                    n_timeout_exceptions_allow-=1 #Try times decrease
                    if n_timeout_exceptions_allow>0:
                        msg_option= " - Error: control not found? retry..."
                        l.warn(msg + e.msg + msg_option)
                        page_prepare(strURL, bRetrieveAllOptions= False)
                    else:
                        msg_option= "\n- Failed."
                        l.warn(msg + e.msg + msg_option)
                        break
                except (Socket_error, BadStatusLine, NoSuchWindowException, WebDriverException) as e:
                    n_timeout_exceptions_allow-=1 #Try times decrease
                    if n_timeout_exceptions_allow>0:
                        msg_option= " - Error: browser not found? retry..."
                        l.warn(msg + (e.msg if hasattr(e,'msg') else '') + msg_option)
                        browser= browserInit()
                        page_prepare(strURL, bRetrieveAllOptions= False)
                    else:
                        msg_option= "\n- Failed."
                        l.warn(msg + (e.msg if hasattr(e,'msg') else '') + msg_option)
                        break
                except Exception as e:
                    msg_option= "\n- Failed. Unknown error"
                    l.warn(msg + (e.msg if hasattr(e,'msg') else '') + msg_option)
                else:
                    l.info(msg + msg_option)
                    print(msg_option)
                    break

        l.info("Ok!"); print("Ok!", end='')
    except Exception as e:
        l.warn(' {}{} {}'.format(msg, ': ' + e.msg + ',' if hasattr(e,'msg') else '',
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
    parser = argparse.ArgumentParser(description= 'Load all files from ' +
        strURL + ''' or only specified by &options[WellName/Permit#].json file \
in download folder. If file not exists it'll be created and filled in sorted order.

''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog= '''requriments: Mozilla Firefox version >= 52.0.3.''',
        version= '0.0.1 - © 2016 Andrey Korzh <ao.korzh@gmail.com>'
    )
    parser.add_argument('list_by', nargs='?', choices=['well','W','w','permit','P','p'],
                        help='W/P - list by Well Name/by Permit #', default= 'W')
    parser.add_argument('startName', nargs='?', type= str, default= "",
                        help='start data download cycle from this name, empty ("") means from first')
    parser.add_argument('outDir', nargs='?', type= str, default='.',
                        help='output dir path')
    args = parser.parse_args()
    byWellName= args.list_by in ['W','w','well']

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