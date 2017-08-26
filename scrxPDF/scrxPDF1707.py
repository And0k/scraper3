#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Purpose:  parse well production report pdf
  Author:   Andrey Korzh <ao.korzh@gmail.com>
  Created:  08.08.2017
"""
import logging
import re

from os import path as os_path, environ as os_environ
from sys import argv as sys_argv, exit, path
from subprocess import Popen, PIPE, STDOUT
from csv import DictWriter as csv_DictWriter  # csvfile,
from collections import defaultdict
from operator import itemgetter

path.append(r'../..')  # this is need to next import work:
from h5toGrid.utils2init import init_logging
from h5toGrid.utils2init import ini2dict, init_file_names, name_output_file, \
    Ex_nothing_done, set_cfg_path_filemask

l = None  # global logging
cfg = None

try:
    from setuptools_scm import get_version

    version = get_version(root='..', relative_to=__file__)
except:  # LookupError
    version = 'x.x.x'


class Task(object):
    def __init__(self, pdfF=None):
        self.name = ''
        self.b_last = False  # True if last branch in task activated

        def gen_next():
            """

            :rtype: str or None
            """
            last_task_from_index = len(cfg['input_files']['tasks_from']) - 1

            def branch_to(task):
                try:
                    i = cfg['input_files']['tasks_from'].index(task)
                    self.b_switching_tasks = False
                    self.b_last = i == last_task_from_index
                    return cfg['input_files']['tasks_to'][i]
                except ValueError:  # when x is not found
                    self.b_switching_tasks = True
                    return None

            # number of not empty rows which need to skip till reach row of current task
            self.rows_skip = 0
            for task in cfg['input_files']['tasks']:
                if task == '':  # may be rows which need to skip
                    self.rows_skip += 1
                    continue
                task = branch_to(task) or task
                self.name = task
                self.re = cfg['input_files']['re_' + task]
                while self.b_last:  # not change last task (wait end of file)
                    yield task  #
                else:
                    while True:
                        b_break = (yield task)
                        if b_break:
                            break
                self.rows_skip = 0

        self.gen_name = gen_next()

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
                            else:  # Skip empty lines, check file end (many empty)
                                k += 1
                                if k > maxNoLines:
                                    break
                        if not line_next:
                            proc.stdout.close()
                            proc.wait()
                            self.gen_name.close()
                            break

                        line_next = line_next.strip('\r\n')  # keep leading spaces
                        if not line_next:
                            continue

                        # - PageStart ahead
                        if line_next[0] == chr(12):  # Form Feed
                            print('.', end='')
                            continue  # never try get other data from first string

                        yield line, line_next

                    except Exception as e:
                        l.warning('Task"{:<10}"> Error when decode line "{}"'.format(self.name, line_next))
                        l.debug(e.args)
                        raise e

            self.ge_source_lines = gen_source_lines(pdfF)
            # to get ready assign line:
            self.line, self.line_next = self.ge_source_lines.__next__()
            self.gen_name.__next__()

            def gen_parse(self):
                """

                :param self:
                :return:
                """
                b_after_bad_line = False
                for self.line, self.line_next in self.ge_source_lines:
                    try:
                        out = self.re.match(self.line)
                        if out:  # all([out[k] for k in self.re.groupindex.keys()])
                            yield out.groupdict()
                            self.gen_name.send(self.b_switching_tasks)  # next task
                            continue
                        if self.rows_skip:
                            self.rows_skip -= 1
                            continue

                        for do_first in (
                                [True, False] if self.b_switching_tasks else [False, True]):
                            if do_first:
                                # Try skip line (use line_next)
                                # (may be inserted bad line: try line_next, but warn)
                                out = self.re.match(self.line_next)
                                if out and all([out.group(k) is not None for k in
                                                self.re.groupindex.keys()]):
                                    l.warning('Task"{:<10}": Skipped bad line "{}"'.format(
                                        self.name, self.line))
                                    b_after_bad_line = False
                                    try:
                                        self.line, self.line_next = \
                                            self.ge_source_lines.__next__()
                                    except StopIteration as e:
                                        return None
                                    yield out.groupdict()
                                    self.gen_name.send(self.b_switching_tasks)  # next task?
                                    break
                                l.warning('Task"{:<10}": Error find in line "{}" and\nnext line '
                                          '"{}"'.format(self.name, self.line, self.line_next))
                            else:
                                # Swith task - normal operation to end of table tasks
                                # and for all tasks if have 2nd bad line (because previous is corrupted)
                                if self.b_switching_tasks and not b_after_bad_line:
                                    b_after_bad_line = True
                                    continue
                                try:
                                    self.gen_name.send(True)  # next task
                                    b_after_bad_line = False
                                except StopIteration as e:
                                    return None
                                out = self.re.match(self.line)
                                if out:  # all([out[k] for k in self.re.groupindex.keys()])
                                    yield out.groupdict()
                                    self.gen_name.send(self.b_switching_tasks)  # next task
                                    break

                    except (AttributeError, TypeError) as e:
                        l.debug(e.args)  # sys_exc_info()
                        l.debug('Task"{:<10}": nothing in "{}"'.format(self.name, self.line))
                        yield None
                        self.gen_name.send(self.b_switching_tasks)  # next task
                    except Exception as e:
                        l.warning('Task"{:<10}": Error read line "{}": {}'.format(
                            self.name, self.line, '\n==> '.join([a for a in e.args if
                                                                 isinstance(a, str)])))
                        self.gen_name.send(self.b_switching_tasks)  # next task

                return None

            self.parse = gen_parse(self)
        else:
            self.ge_source_lines = lambda: (None, None)  # dummy
            self.parse = lambda: None  # dummy


def proc_data(pdfF, csv_dict_writer, fn=None, *args):
    """
    Parse pdf line by line using globl cfg
    :param pdfF:
    :param csv_dict_writer:
    :param fn:
    :param args:
    :return:
    """
    # new task class
    taskRe = Task(pdfF)

    def relace_hashes_in_dict_if_w_digits(d):
        """
        Removes hashes from dict fields which have both hash and digits
        :param d: dict
        :return: nothing
        """
        for k, v in d.items():
            if '#' in v and re.search('\d', v):
                d[k] = v.replace('#', '')

    def save(dict_data, dict_new={}, task=taskRe.name):
        if not dict_data:
            # No data found
            l.warning('Nothing in file before table. Last line: "{}"'.format(taskRe.line))
            return

        relace_hashes_in_dict_if_w_digits(dict_new)
        dict_data.update(dict_new)
        try:
            csv_dict_writer.writerow(dict_data)
            l.debug('Task"{:<10}": "{}" data saved'.format(task, taskRe.line))
        except Exception as e:
            l.warning('Task"{:<10}": Error save line "{}": {}'.format(
                task, taskRe.line, '\n==> '.join([a for a in e.args if isinstance(a, str)])))

    # Get data:
    def constant_factory(value):
        return lambda: value

    data = {}  # defaultdict(constant_factory(''))
    if '<File>' in cfg['output_files']['header']:
        data['<File>'] = pdfF
    try:
        for new_data in taskRe.parse:  # Cycle by row (each row have same fields)
            # Collect common fields (which will not overwites)
            if taskRe.b_switching_tasks:
                data.update(new_data)
                continue

            if 'nodata' in data:
                del data['nodata']  # remove headers
            assert 'Quad' in data
            if new_data:
                if any([True for v in new_data.values() if v is None]):
                    l.warning('Task"{:<10}": Bad parameters ({}) from line "{}"'.format(
                        taskRe.name, '; '.join(['{}={}'.format(k, v) for k, v in new_data.items()]), taskRe.line))
                    for k, v in new_data.items():
                        new_data[k] = str(v)  # convert None to 'None'
                if taskRe.b_last:
                    save(data, new_data)
                else:
                    for k, v in new_data.items():
                        try:
                            data[k] += ('; ' + v)
                        except KeyError:
                            data[k] = v

            l.debug('Task"{:<10}": "{}" data saved'.format(taskRe.name, taskRe.line))
    except Exception as e:
        l.warning('Task"{:<10}": Error save line "{}": {}'.format(
            taskRe.name, taskRe.line, '\n==> '.join([a for a in e.args if isinstance(a, str)])))
    return data  # data includes only last last table row


################################################################################
################################################################################


def parse_cfg():
    global cfg
    import configargparse

    # p = configargparse.get_argument_parser(
    p = configargparse.ArgumentParser(
        default_config_files=['scrxPDF1707.ini'],  # ../
        description="---------------------------------\n"
                    "Extract *.pdf text data to *.csv.\n"
                    "---------------------------------\n",
        formatter_class=configargparse.ArgumentDefaultsRawHelpFormatter,
        # formatter_class= configargparse.ArgumentDefaultsHelpFormatter,
        epilog='',
        args_for_writing_out_config_file=["-w", "--write-out-config-file"],
        write_out_config_file_arg_help_message=
        "takes the current command line args and writes them out to a config file "
        "the given path, then exits. But this file have no section headers. So to "
        "use this file you need to add sections manually. Sections are listed here "
        "in help message: [input_files], [output_files] ..."
    )
    p.add_argument('--version', '-v', action='version', version=
    'scrxPDF1707 version ' + version + ' - (c) 2017 Andrey Korzh <ao.korzh@gmail.com>.\n\nProgram uses the GPL Xpdf software copyrighted 1996-2014 Glyph & Cog, LLC.\n(Email: derekn@foolabs.com, WWW: http://www.foolabs.com/xpdf/)')
    # Fill configuration sections
    # All argumets of type str (default for add_argument...), because of
    # custom postprocessing based of args names in ini2dict
    p_input_files = p.add_argument_group('input_files', 'Parameters of input files')
    p_input_files.add_argument(
        '--path', default='.', #nargs=?,
        help='path to pdf file or dir with pdf files to parse. Use patterns in Unix shell style')
    p_input_files.add_argument(
        '--b_search_in_subdirs', default='True', help='search in subdirectories')

    # p_input_files.add_argument(
    #     '--emptyfield',
    #     default='Unassigned Field', help= 'unassigned field value')
    # p_input_files.add_argument(
    #     '--unknownfield',
    #     default='######', help= 'field wich value can not be determined')

    # Task order
    p_input_files.add_argument(
        '--tasks_list',  # nargs='+' for list of lists
        default='County_Quad_Pool, Buyer_Lease_Type_Active, , Permit_Well_header, '
                'Permit_Well, Permit_Well_end, Product_by_month_header, Product_by_month',
        help='list of tasks (rows to parse). Each task must have regular expression "re_<Name>" (see below). Empty items is for skip lines without warning (besides of empty lines which skipped silently)')
    p_input_files.add_argument(
        '--tasks_branch_from_to_list',
        default='Permit_Well, Permit_Well, Product_by_month, Product_by_month',
        help='''list where odd items are tasks to branch "from" and even items
are tasks to branch "to":
[from taskX1, to taskY1, from taskX2, to taskY2, ...]. If task is listed in
TaskX then it will be repeated while it will not pass. Then task will be
switched to next adjasent taskY and continues to change with tasks_list order.
I.e. this list change defaut "Try next if ok" behavour to "Try again if ok" if
taskN repeats.
        ''')
    # Regular expressions for each task
    p_input_files.add_argument(
        '--re_County_Quad_Pool',
        default=" *(?P<County>.*?)(?: *County;) +(?P<Quad>.*?)(?: *Quad;)"
                " +(?P<Pool>.*?)(?: +Field +Pool.*)$",
        help='regular expression with named fields')
    p_input_files.add_argument(
        '--re_Buyer_Lease_Type_Active',
        default=" *(?:Buyer: +)(?P<Buyer>.*?)(?:,? *(Buyer's|) *Lease#: +)(?P<Lease>.*?)"
                "(?: *Production +Type +)(?P<Type>[^ ]*?)(?: *Production +Unit.*| .*|$)")
    # Wells In Production Uni
    p_input_files.add_argument(
        '--re_Permit_Well_header',
        default=" *(?P<nodata>Permit +#? +Well +Name)",
        help="it checks but not saves <nodata> fields")
    p_input_files.add_argument(
        '--re_Permit_Well',
        default="(?! *Edit)((?P<Permit>[^ ]{1,10})| {8})((?: +(?P<Well>.*))|$)"
    )
    p_input_files.add_argument(
        '--re_Permit_Well_end',
        default="(?P<nodata> *Edit *Wells)"
    )
    p_input_files.add_argument(
        '--re_Product_by_month_header',
        default="(?P<nodata> *Year +Jan +Feb +Mar +Apr +May +Jun +Jul +Aug +Sep +Oct +Nov +Dec +Totals)")
    p_input_files.add_argument(
        '--re_Product_by_month',
        default= \
          "[^\dT]*(?P<Year>[\d]{2,4}|Totals)(?:[# ]{,9})(?: {1,17})"
        "(?=[\d.# ]{,15})(?P<Jan>[\d.]{,9})(?:[# ]{,9})(?: {1,17})"
        "(?=[\d.# ]{,15})(?P<Feb>[\d.]{,9})(?:[# ]{,9})(?: {1,17})"
        "(?=[\d.# ]{,15})(?P<Mar>[\d.]{,9})(?:[# ]{,9})(?: {1,17})"
        "(?=[\d.# ]{,15})(?P<Apr>[\d.]{,9})(?:[# ]{,9})(?: {1,17})"
        "(?=[\d.# ]{,15})(?P<May>[\d.]{,9})(?:[# ]{,9})(?: {1,17})"
        "(?=[\d.# ]{,15})(?P<Jun>[\d.]{,9})(?:[# ]{,9})(?: {1,17})"
        "(?=[\d.# ]{,15})(?P<Jul>[\d.]{,9})(?:[# ]{,9})(?: {1,17})"
        "(?=[\d.# ]{,15})(?P<Aug>[\d.]{,9})(?:[# ]{,9})(?: {1,17})"
        "(?=[\d.# ]{,15})(?P<Sep>[\d.]{,9})(?:[# ]{,9})(?: {1,17})"
        "(?=[\d.# ]{,15})(?P<Oct>[\d.]{,9})(?:[# ]{,9})(?: {1,17})"
        "(?=[\d.# ]{,15})(?P<Nov>[\d.]{,9})(?:[# ]{,9})(?: {1,17})"
        "(?=[\d.# ]{,15})(?P<Dec>[\d.]{,9})(?:[# ]{,9})(?: {1,17})"
    "(?=[\d.# ]{,15})(?P<Totals>[\d.]{,10})(?:[# ]{,10})$")


    p_output_files = p.add_argument_group('output_files', 'Parameters of output files')
    p_output_files.add_argument(
        '--out_path', '-o', type=str, default='./<File_in>.csv',
        help='''output dir/path.
Join data from all found input files to single output. PATH can contain special string:
 "<File_in>": to sabstitute with [1st file name]+.
If no extension provided then ".csv" will be used.
''')  # .csv "<dir>":      last directory name.
    p_output_files.add_argument(
        '--header_list', default='Buyer,Pool,Permit,Well,Quad,County,Type,Lease,'
                                 '<Product_by_month>,<File>',  # Total,Active
        help='''
columns order. List of comma separated element which are
1) named regex fields i.e. Name from (?P<Name>) elements of [input_files].re_* lists or/and 
2) this lists names without "re_" enclosed in angle brackets: all named fields from 
them will be added automatically.'
3) <File> field: to include path/name of parsed file
''')
    p_output_files.add_argument(
        '--min_size_to_overwrite', default=0, metavar='BYTES',
        help= 'overwrite small output files: with the sizes less given value [bytes]')
    p_program = p.add_argument_group('program', 'Program behaviour')
    p_program.add_argument(
        '--verbose', '-V', type=str, default='INFO', #nargs=1,
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'],
        help='verbosity of messages in log file')
    p_program.add_argument(
        '--log', type=str, default='&<prog>.log', metavar='PATH',
        help='dir/path of log relative to output path')
    p_program.add_argument(
        '--b_ask_to_start', type=str, default='True',
        help='stops and show found source files')
    try:
        args = vars(p.parse_args())
        #args['verbose'] = args['verbose'][0]
        # groupsection by
        cfg_strings = {}
        # cfg= {section: {} for section in ['input_files', 'output_files', 'program']}
        for gr in p._action_groups:
            # skip argparse argument groups
            if gr.title.split(' ')[-1] == 'arguments':
                continue
            cfg_strings[gr.title] = {key: args[key].replace('<prog>', p.prog) if \
                isinstance(args[key], str) else args[key] for key in \
                args.keys() & [a.dest for a in gr._group_actions]}

        cfg = ini2dict(cfg_strings)
    except Exception as e: #IOError
        print('Configuration ({}) error:'.format(p._default_config_files), end=' ')
        print('\n==> '.join([s for s in e.args if isinstance(s, str)]))  # e.message
        raise (e)
    except SystemExit as e:
        pass
    return(cfg)


def cycle_files(fun_on_files=None):
    """
    Find source files, apply function 
    :param fun_on_files: function to apply
    :return: 
    """
    global cfg, l
    bInteract = False  # cfg['program']['verbose']=='DEBUG'

    ############################################################################
    try:
        cfg['input_files'] = init_file_names(cfg['input_files'], cfg['program']['b_ask_to_start'])
    except Ex_nothing_done as e:
        print(e.message)
        exit(0)

    cfg['output_files']['path'], cfg['output_files']['ext'] = os_path.splitext(
        cfg['output_files']['out_path'])  # set_cfg_path_filemask requires 'path'
    if not cfg['output_files']['ext']:    # set_cfg_path_filemask requires some ext in path or in 'ext'
        cfg['output_files']['ext']= '.csv'
    cfg['output_files']['path'] = cfg['output_files']['out_path']
    set_cfg_path_filemask(cfg['output_files'])

    namesFE0 = os_path.basename(cfg['input_files']['namesFull'][0])
    cfg['output_files']['base'] = os_path.splitext(namesFE0)[0]
    # Check target exists-
    file_out, writeMode, msg_name_output_file = name_output_file(
        cfg['output_files']['path'], cfg['output_files']['filemask'].replace(
            '<File_in>', cfg['output_files']['base'] + '+'), None,
        bInteract, cfg['output_files']['min_size_to_overwrite'])
    with open(file_out, writeMode, newline='') as fp_out:
        csv_dict_writer = csv_DictWriter(
            fp_out, fieldnames=cfg['output_files']['header'],
            extrasaction='ignore'  # ignore fieds not specified in cfg['output_files']['header']
        )
        csv_dict_writer.writeheader()

        str_print = '{msg_name} Saving all to {out}:'.format(
            msg_name=msg_name_output_file, out=os_path.abspath(file_out))
        print(str_print)

        l = init_logging(logging, cfg['output_files']['path'], cfg['program']['log'], cfg['program']['verbose'])
        l.info(str_print)

        bFirst = True
        n_disp_dots = 3

        # Process and write data
        for n, nameFull in enumerate(cfg['input_files']['namesFull'], start=1):
            nameFE = os_path.split(nameFull)[1]
            str_print = ' {n:3d}. File "{f}"'.format(n=n, f=nameFE)
            print('\n' + str_print, end='')
            l.info(str_print)
            try:
                file_data = fun_on_files(nameFull, csv_dict_writer)
            except (AttributeError, ValueError, IOError, TypeError) as e:  # Exception as e:
                l.warning(nameFE + ": " + getattr(e, 'message', '') + '\n==> '.join([
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


def gen_traverse_tasks():
    """
    Generator to traverse tasks.
    Same as Task.gen_next but not doing any other actions
    :param task:
    :return:
    """
    for task in cfg['input_files']['tasks']:
        if not task:
            continue
        yield task


def correct_lowered_fields_of_cfg(cfg):
    '''
    Correct lower case fields of cfg['input_files']: 'task??_*' and 're_*'
    :param cfg: cfg with exact or lower cased fields of items contained in
    cfg['input_files']['task??_*'] lists
    :return: cfg with lower case fields replaced by data specified in
             cfg['input_files']['task??_*'] lists
    '''

    # Correct lower case fields of cfg['input_files']['re_*']
    for t in gen_traverse_tasks():
        t_low = t.lower()
        if t != t_low:
            field_low = 're_' + t_low
            if not field_low in cfg['input_files'] and ('re_' + t) in cfg['input_files']:
                continue  # It is all right with the field already
            try:
                cfg['input_files']['re_' + t] = cfg['input_files'][field_low]
                del cfg['input_files'][field_low]
            except Exception as e:
                raise ValueError(
                    'Bad [input_files] configuration: no "re_" field corresponded to {} '
                    'listed in [input_files].tasks_list'.format(t))
    return cfg


# if __name__ == '__main__':  #####################################################
def main():
    global cfg, l

    cfg = parse_cfg()
    if not cfg:
        return
    cfg = correct_lowered_fields_of_cfg(cfg)
    cfg['input_files']['tasks_from'] = cfg['input_files']['tasks_branch_from_to'][::2]
    cfg['input_files']['tasks_to'] = cfg['input_files']['tasks_branch_from_to'][1::2]
    del cfg['input_files']['tasks_branch_from_to']

    # More configuration
    ###########################################

    # Expand special fields in cfg['output_files']['header']
    h_expanded = []
    for t in cfg['output_files']['header']:
        if not t.startswith('<') or t == '<File>':  # need expand
            h_expanded.append(t)
            continue
        re_items = cfg['input_files']['re_' + t[1:-1]].groupindex
        re_named_fields = [k for k, v in sorted(re_items.items(), key=itemgetter(1))]
        h_expanded.extend(re_named_fields)
    cfg['output_files']['header'] = h_expanded

    # add fixed configuration (have no access to change by user)
    def is64Windows():
        return 'PROGRAMFILES(X86)' in os_environ

    path_xpdf_pdftotext = os_path.join(
        os_path.dirname(os_path.realpath(sys_argv[0])),
        'pdftotext64.exe' if is64Windows() else 'pdftotext.exe')
    if not os_path.isfile(path_xpdf_pdftotext):
        raise IOError('pdftotext.exe not found')
    cfg['program']['pdftotext_command'] = path_xpdf_pdftotext + ' -table -clip "{file}" -'

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
