#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Purpose:  parse well production report pdf
  Author:   Andrey Korzh <ao.korzh@gmail.com>
  Created:  08.08.2017
"""
import logging
import re
# outfp = StringIO()
# from collections import deque
from csv import DictWriter as csv_DictWriter  # csvfile,

from os import path as os_path, environ as os_environ
from subprocess import Popen, PIPE, STDOUT
from sys import argv as sys_argv
from operator import itemgetter

from dateutil import parser as dateutil_parser
from h5toGrid.utils2init import init_logging

l  = None  # global logging
cfg= None

# import numpy as np
try:
    from setuptools_scm import get_version

    version = get_version(root='..', relative_to=__file__)
except:  # LookupError
    version = 'x.x.x'

class Task(object):
    def __init__(self, task, pdfF= None):
        def gen_next(task):
            """

            :rtype: str or None
            """
            def get_field_of_branch(task):
                return self.get_prefix_of_branch(task) + task

            # number of not empty rows which need to skip till reach row of current task
            self.rows_skip = 0
            while True:
                try:

                    for t in cfg['input_files'][get_field_of_branch(task)]:
                        if t=='': # may be rows which need to skip
                            self.rows_skip += 1
                            continue
                        self.name = t
                        self.re = cfg['input_files']['re_' + t]
                        yield t
                        self.rows_skip = 0
                    task = get_field_of_branch(t)
                except KeyError as e:
                    return None  # end of useful data in file

        self.gen_name = gen_next(task)

        if pdfF:
            def gen_source_lines(pdfF):
                line_next = ''
                line = ''
                codec = 'utf-8'
                maxNoLines = 100
                proc = Popen(cfg['program']['pdftotext_command'].format(file=pdfF), stdout=PIPE,
                             stderr=STDOUT)  # , bufsize=1
                while True:
                    # Save prev line and look ahead (helps find footer after new line)
                    if line_next:
                        line = line_next
                        line_next = ''
                    try:  # if True:

                        k = 0
                        while not line_next:
                            line_next = proc.stdout.readline().decode(codec)
                            if line_next:
                                break
                            else: # Skip empty lines, check file end (many empty)
                                k += 1
                                if k > maxNoLines:
                                    break
                        if not line_next:
                            proc.stdout.close()
                            proc.wait()
                            break

                        line_next = line_next.strip('\r\n ')
                        if not line_next:
                            continue

                        # - PageStart ahead
                        if line_next[0] == chr(12):  # Form Feed
                            print('.', end='')
                            continue  # never try get other data from first string

                        yield line, line_next

                    except Exception as e:
                        l.warning('Task"{:<10}"> Error when decode line "{}"'.format(task, line_next))
                        l.debug(e.args)
                        raise e
            self.ge_source_lines = gen_source_lines(pdfF)
            # to get ready assign line:
            self.line, self.line_next = self.ge_source_lines.__next__()

            def gen_parse(self):
                b_after_bad_line= False
                try:
                    for self.line, self.line_next in self.ge_source_lines:
                        out = self.re.match(self.line)
                        if out:  # all([out[k] for k in self.re.groupindex.keys()])
                            yield out.groupdict()
                            continue
                        if self.rows_skip:
                            self.rows_skip -= 1
                            continue

                        if b_after_bad_line:
                            # 2nd bad line => try next task (may be previous is corrupted)
                            try:
                                self.gen_name.__next__()
                            except StopIteration as e:
                                return None
                            b_after_bad_line = False
                            out = self.re.match(self.line)
                            if out:  # all([out[k] for k in self.re.groupindex.keys()])
                                yield out.groupdict()
                            continue
                        b_after_bad_line = True
                        # may be inserted bad line: try line_next, but warn
                        l.warning('Task"{:<10}": Error find in line "{}"'.format(self.name, self.line))
                        # try skip line (use line_next)
                        out = self.re.match(self.line_next)
                        if out and all([out[k] is not None for k in self.re.groupindex.keys()]):
                            b_after_bad_line= False
                            try:
                                self.line, self.line_next = self.ge_source_lines.__next__()
                            except StopIteration as e:
                                return None
                            yield out.groupdict()
                            continue

                        continue
                        #               l.warning('Task"{:<10}": nothing in "{}"'.format(self.name, self.line_next))
                    return out.groupdict()
                except (AttributeError, TypeError) as e:
                    l.debug(e.args)  # sys_exc_info()
                    l.debug('Task"{:<10}": nothing in "{}"'.format(self.name, self.line))
                    return None

            self.parse= gen_parse(self)
        else:
            self.ge_source_lines = lambda : (None, None) #dummy
            self.parse= lambda : None #dummy



    def get_prefix_of_branch(self, task):
        self.b_try_next_if_ok = ('task01_' + task) in cfg['input_files']
        return 'task01_' if self.b_try_next_if_ok else 'task10_'

def proc_data(pdfF, csv_dict_writer, fn=None, *args):
    """
    Parse pdf line by line using globl cfg
    :param pdfF:
    :param csv_dict_writer:
    :param fn:
    :param args:
    :return:
    """

    # task order ini
    taskRe = Task(cfg['input_files']['task_first'], pdfF)

    # Get data:
    data = {'File': pdfF}
    for task in taskRe.gen_name:
        # Collect common fields (which will not overwites)
        if taskRe.b_try_next_if_ok:
            data.update(taskRe.parse.__next__())
        else:
            break

    if not data:
        # No data found
        l.warning('Nothing in file before table. Last line: "{}"'.format(taskRe.line))
        return

    if 'nodata' in data:
        del data['nodata'] # remove headers
    assert 'Quad' in data
    for dict_from_row_of_table in taskRe.parse:
    # dict_from_row_of_table= True
    # while :
    #     # For each line in table
    #     dict_from_row_of_table = .__next__()
        if not dict_from_row_of_table:
            break
        data.update(dict_from_row_of_table)

        try:
            csv_dict_writer.writerow(data)
            l.debug('Task"{:<10}": "{}" data saved'.format(task, taskRe.line))
        except Exception as e:
            l.warning('Task"{:<10}": Error save line "{}": {}'.format(
                task, taskRe.line, '\n==> '.join([ a for a in e.args if isinstance(a, str)])))
    return data  # includes only last last table row

################################################################################
################################################################################
from h5toGrid.utils2init import ini2dict, init_file_names, name_output_file, \
    Ex_nothing_done, set_cfg_path_filemask, getDirBaseOut, dir_create_if_need, set_field_if_no



def parse_cfg():
    import configargparse

    #p = configargparse.get_argument_parser(
    p = configargparse.ArgumentParser(
        default_config_files=['scrxPDF1707.ini'], #../
        description='Convert *.pdf to *.csv',
        formatter_class= configargparse.ArgumentDefaultsRawHelpFormatter,
        # formatter_class= configargparse.ArgumentDefaultsHelpFormatter,
        epilog='If use special characters then insert arguments in quotes',
        version=r'''scrxPDF1707 version 0.0.1 - (c) 2017 Andrey Korzh <ao.korzh@gmail.com>.

Program uses the GPL Xpdf software copyrighted 1996-2014 Glyph & Cog, LLC.
(Email: derekn@foolabs.com, WWW: http://www.foolabs.com/xpdf/)''',
        args_for_writing_out_config_file=["-w", "--write-out-config-file"])
    # Fill configuration sections
    # Most argumets of type str (default for add_argument...), because of
    # custom postprocessing based of args names in ini2dict
    p_input_files= p.add_argument_group('input_files', 'Parameters of input files')
    p_input_files.add_argument(
        '--path', nargs='?', default='.',
        help='Path to pdf or dir with pdf files to parse. Use patterns in Unix shell style')
    p_input_files.add_argument(
        '--b_search_in_subdirs', default='True', help= 'search in subdirectories')

    p_input_files.add_argument(
        '--emptyfield',
        default='Unassigned Field', help= 'unassigned field value')
    p_input_files.add_argument(
        '--unknownfield',
        default='######', help= 'field wich value can not be determined')

    # Task order
    p_input_files.add_argument(
        '--task_first', default='County_Quad_Pool',
        help='name of first regular expression to check in file')
    p_input_files.add_argument(
        '--task01_County_Quad_Pool_list', # nargs='+' for list of lists
        default='County_Quad_Pool, Buyer_Lease_Type_Active, , Permit_Well_header, '
                 'Permit_Well, , Product_by_month_header, Product_by_month',
        help='''
"Try next if ok" list: if parced: then switch to next rule else: try next line while not parsed
''')
    p_input_files.add_argument(
        '--task10_Product_by_month_list',
        default='Product_by_month',
        help='''
"Try again if ok" list - useful for tables with regular structure
if parced: keep rule.
else: go next line and if not parsed then swich rule and try it.
if no next rule: end of document
        ''')

    # Regular expressions for each task
    p_input_files.add_argument(
        '--re_County_Quad_Pool',
        default=" *(?P<County>.*?)(?: *County;) +(?P<Quad>.*?)(?: *Quad;)"
        " +(?P<Pool>.*?)(?: +Field +Pool.*)$",
        help= 'regular expression with named fields'
    'get last field even it has no last identification suffix')
    p_input_files.add_argument(
        '--re_Buyer_Lease_Type_Active',
        default="(?:Buyer: +)(?P<Buyer>.*?)(?:,? *(Buyer's|) *Lease#: +)(?P<Lease>.*?)"
                "(?: *Production +Type +)(?P<Type>[^ ]*?)(?: *Production +Unit.*| .*|$)")
    #Wells In Production Uni
    p_input_files.add_argument(
        '--re_Permit_Well_header',
        default="(?P<nodata>Permit +#? +Well +Name)",
        help="It checks but not saves <nodata> fields")
    p_input_files.add_argument(
        '--re_Permit_Well',
        default="((?P<Permit>[^ ]{1,10})| )((?: +(?P<Well>.*))|$)")
    p_input_files.add_argument(
        '--re_Product_by_month_header',
        default="(?P<nodata> *Year +Jan +Feb +Mar +Apr +May +Jun +Jul +Aug +Sep +Oct +Nov +Dec +Totals)")
    p_input_files.add_argument(
        '--re_Product_by_month',
        default=" *(?P<Year>\d{2,4}|Totals) +(?P<Jan>[\d.#]{1,10}) +(?P<Feb>[\d.#]{1,10})"
        " +(?P<Mar>[\d.#]{1,10}) +(?P<Apr>[\d.#]{1,10}) +(?P<May>[\d.#]{1,10})"
        " +(?P<Jun>[\d.#]{1,10}) +(?P<Jul>[\d.#]{1,10}) +(?P<Aug>[\d.#]{1,10})"
        " +(?P<Sep>[\d.#]{1,10}) +(?P<Oct>[\d.#]{1,10}) +(?P<Nov>[\d.#]{1,10})"
        " +(?P<Dec>[\d.#]{1,10}) +(?P<Totals>[\d.#]{1,10})")

    p_output_files= p.add_argument_group('output_files', 'Parameters of output files')
    p_output_files.add_argument(
        '--out_path', '-o', nargs='?', type=str, default='./<filename>.csv',
        help='''Output dir/path.
Join data from all found input files to single output if extension provided. If
"<filename>" found it will be sabstituted with [1st file name]+, "<dir>" -
with last directory name.
Else, if no extension provided then ".csv" will be used, "<filename>" strings
will be sabstituted with correspondng input file names.
''')  # .csv
    re_items= re.compile(p_input_files._option_string_actions['--re_Product_by_month'].default).groupindex
    task10_keys= [k for k,v in sorted(re_items.items(), key=itemgetter(1))]
    p_output_files.add_argument(
        '--header_list', default= 'Buyer,Pool,Permit,Well,Quad,County,Type,Lease,'
                                  + ','.join(task10_keys)+ ',File',  # Total,Active
        help= 'Columns order. Names must be taken from regex defined in [input_files].'
              'task01_* lists. Names from [input_files].[re_Product_by_month] list added automatically.'
              'File field added automatically')
    p_output_files.add_argument(
        '--min_size_to_overwrite', default= 0)
    p_program= p.add_argument_group('program', 'Program behaviour')
    p_program.add_argument(
        '--verbose', '-v', nargs=1, type=str, default=['INFO'],
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'],
        help='Verbosity of messages in log file')
    p_program.add_argument(
        '--log', type=str, default='<prog>.log',
        help='log dir/path.')
    p_program.add_argument(
        '--b_ask_to_start', type=str, default='True',
        help= 'stops and show found source files')
    args= vars(p.parse_args())
    args['verbose'] = args['verbose'][0]
    # groupsection by
    cfg_strings= {}
    #cfg= {section: {} for section in ['input_files', 'output_files', 'program']}
    for gr in p._action_groups:
        # skip argparse argument groups
        if gr.title.split(' ')[-1] == 'arguments':
            continue
        cfg_strings[gr.title]= {
            key: args[key] for key in args.keys() & [a.dest for a in gr._group_actions]}

    # delete output files with sizes less:
    try:
        cfg= ini2dict(cfg_strings)
    except IOError as e:
        print('Configuration file ({}) error:'.format(args.cfgFile), end=' ')
        print('\n==> '.join([s for s in e.args if isinstance(s, str)])) #e.message
        raise(e)

    return(cfg)

def cycle_files(fun_on_files= None):
    """
    Find source files, apply function 
    :param fun_on_files: function to apply
    :return: 
    """
    global cfg, l
    bInteract = False  # cfg['program']['verbose']=='DEBUG'


    ############################################################################
    try:
        cfg['input_files']= init_file_names(cfg['input_files'], cfg['program']['b_ask_to_start'])
    except Ex_nothing_done as e:
        print(e.message)
        exit(0)
    cfg['output_files']['path']= cfg['output_files']['out_path'] # next function requires 'path' 
    set_cfg_path_filemask(cfg['output_files'])

    namesFE0= os_path.basename(cfg['input_files']['namesFull'][0])
    cfg['output_files']['base'] = os_path.splitext(namesFE0)[0]
    # Check target exists-
    file_out, writeMode, msg_name_output_file = name_output_file(
        cfg['output_files']['path'], cfg['output_files']['filemask'].replace(
        '<filename>', cfg['output_files']['base'] + '+'), None,
        bInteract, cfg['output_files']['min_size_to_overwrite'])
    with open(file_out, writeMode, newline='') as fp_out:
        csv_dict_writer = csv_DictWriter(
            fp_out, fieldnames= cfg['output_files']['header'],
            extrasaction= 'ignore'  # ignore fieds not specified in cfg['output_files']['header']
            )
        csv_dict_writer.writeheader()

        str_print = '{msg_name} Saving all to {out}:'.format(
            msg_name=msg_name_output_file, out=os_path.abspath(file_out))
        print(str_print)

        l= init_logging(logging, cfg['output_files']['path'], None, cfg['program']['verbose'])
        l.info(str_print)

        bFirst = True
        n_disp_dots = 3

    # Process and write data
        for n, nameFull in enumerate(cfg['input_files']['namesFull'], start=1):
            nameFE = os_path.split(nameFull)[0]
            str_print = ' {n:3d}. File "{f}"'.format(n=n, f=nameFE)
            print('\n' + str_print, end='')
            l.info(str_print)
            try:
                file_data = fun_on_files(nameFull, csv_dict_writer)
            except (AttributeError, ValueError, IOError, TypeError) as e:  # Exception as e:
                l.warning(nameFE + ": " + getattr(e,'message','') + '\n==> '.join([
                    a for a in e.args if isinstance(a, str)]) +
                       '\n - Skip (rest) file data')
    try:
        l.info("Ok!")
        print('\nOk!', end='')
        # try:
        pass
    except Ex_nothing_done as e:
        print(e.message)
    except Exception as e:
        l.error((e.msg if hasattr(e, 'msg') else '') + " when process " + msg_name_output_file)
    finally:
        try:
            # l.handlers[0].flush()
            logging.shutdown()
        except:
            pass

def correct_lowered_fields_of_cfg(cfg):
    '''
    Correct lower case fields of cfg['input_files']: 'task??_*' and 're_*'
    :param cfg: cfg with exact or lower cased fields of items contained in
    cfg['input_files']['task??_*'] lists
    :return: cfg with lower case fields replaced by data specified in
             cfg['input_files']['task??_*'] lists
    '''

    # Functions to correct lower case fields cfg['input_files']['task??_*']
    def prefix_of_replaced_field(t):
        """
        Returns prefix same as Task.get_prefix_of_branch, but also works with t = task.lower()
        end deliberate side effect: replases cfg['input_files']['task.._'+t] key with
        cfg['input_files']['task.._'+task]
        :param t: lower of 'task name'
        :return: prefix 'task.._' or '-' when all traversed
        """
        t_low = t.lower()
        if 'task01_' + t_low in cfg['input_files']:
            prefix = 'task01_'
        else:
            prefix = 'task10_'
            if 'task10_' + t_low not in cfg['input_files']:
                # returns not existed field to finish if field already not lowered:
                if 'task01_' + t in cfg['input_files']:
                    prefix = 'task01_' # need only to trverse not lowered field first
                return prefix

        field_low = prefix + t_low
        cfg['input_files'][prefix + t]= cfg['input_files'][field_low]
        del cfg['input_files'][field_low]
        return prefix

    def gen_traverse_tasks(task):
        """
        Generator to traverse tasks.
        Same as Task.gen_next but not doing any other actions
        :param task:
        :return:
        """
        get_field_of_branch = lambda t: prefix_of_replaced_field(t) + t
        while True:
            try:
                for t in cfg['input_files'][get_field_of_branch(task)]:
                    yield t
                task = get_field_of_branch(t)
            except KeyError as e:
                return  # end of useful data in file

    #task_gen_traverse = gen_traverse_tasks(cfg['input_files']['task_first'])

    # Correct lower case fields of cfg['input_files']: 'task??_*' and 're_*'
    for t in gen_traverse_tasks(cfg['input_files']['task_first']):
        t_low=t.lower()
        if t!=t_low:
            field_low = 're_' + t_low
            try:
                cfg['input_files']['re_' + t]= cfg['input_files'][field_low]
                del cfg['input_files'][field_low]
            except Exception as e:
                raise ValueError(
                'Bad [input_files] configuration: no "re_" field corresponded to {}'
                'listed in [input_files].task01_County_Quad_Pool'.format(t))
    return cfg
#if __name__ == '__main__':  #####################################################
def main():
    global cfg, l

    cfg = parse_cfg()
    cfg = correct_lowered_fields_of_cfg(cfg)

    # More configuration (fixed: no access to change by user)
    def is64Windows():
        return 'PROGRAMFILES(X86)' in os_environ
    path_xpdf_pdftotext = os_path.join(
        os_path.dirname(os_path.realpath(sys_argv[0])),
        'pdftotext64.exe' if is64Windows() else 'pdftotext.exe')
    if not os_path.isfile(path_xpdf_pdftotext):
        raise IOError('pdftotext.exe not found')
    cfg['program']['pdftotext_command'] = path_xpdf_pdftotext + ' -table "{file}" -'

    cycle_files(proc_data)

if __name__ == '__main__':
    main()

# Trash #######################################################################

# except Exception as e:
# print('The end. There are errors: ', e.message)
# exc_class, exc,traceback = sys_exc_info() #
##my_exc = StuffCachingError('Caching error: ' + e)
# raise exc.__class__, exc, traceback
##raw_input('')

# print_out= ','.join(['{{{}}}'.format(col_name) for col_name in col_names])

# dtype_in= dtype_out.copy().update({'Page': '>i2', 'DateStr': '|S60'})
# del(dtype_in['Year'])
# del(dtype_in['Month'])

# x = np.array(dType)
# cfg_input_files['colmn_names']= ('stime', 'latitude', 'longitude')
# a[i]= np.fromstring(s, dtype=np.uint16, sep="\t")
# out_dtype= #dtype=('i4,f4,a10'))
# np.zeros((2,),dtype=('i4,f4,a10'))
