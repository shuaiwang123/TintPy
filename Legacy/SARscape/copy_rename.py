#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copy single burst and rename it for SARscape imported data   #
# Copyright (c) 2020, Lei Yuan                                 #
################################################################

import os
import re
import sys
import shutil
import argparse


def copy_rename(import_path, date, burst, save_path):
    '''
    :param import_path: directory path of SARSCAPE imported data
    :param date: date of Sentinel-1 (list)
    :param burst: burst info of Sentinel-1 (list)
    :param save_path: directory path of saveing slc
    :return: date_copyed (list)
    '''
    date_copyed = ''
    files = os.listdir(import_path)
    for file in files:
        dir_path = os.path.join(import_path, file)
        is_dir = os.path.isdir(dir_path)
        if date in file and is_dir and 'VV' in file:
            iw_files = os.listdir(dir_path)
            for f in iw_files:
                if not f.endswith('.enp'):
                    if burst in f:
                        old_burst_path = os.path.join(dir_path, f)
                        new_burst_path = os.path.join(save_path,
                                                      f.replace(burst, date))
                        # copy rename
                        shutil.copy(old_burst_path, new_burst_path)
                        date_copyed = date
    return date_copyed


def get_date_burst(burst_info):
    '''
    :param burst_info: file including date and burst information of Seltinel-1
    :return date_list: all dates
    :return burst_list: all burst names
    '''
    date_list = []
    burst_list = []
    # file format: two colums splited by space (20141102 burst_IW1_1)
    with open(burst_info, encoding='utf-8') as f:
        for line in f.readlines():
            # search date
            s_d = re.search(r'\d{8}', line)
            # search burst
            s_b = re.search(r'burst_IW\d_\d', line)
            if s_d and s_b:
                line_text = re.split(r'\s+', line.strip())
                if line_text[0] not in date_list:
                    date_list.append(line_text[0])
                    burst_list.append(line_text[1])
    return date_list, burst_list



EXAMPLE = '''Example:
  python copy_rename.py -b D:\\burst.txt -i D:\\xsc -s D:\\slc
'''


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description=
        'Copy single burst and rename it for SARscape imported data.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)
    parser.add_argument('-b',
                        dest='burst_info',
                        required=True,
                        type=str,
                        help='text file including date and burst name')
    parser.add_argument('-i',
                        dest='imported_path',
                        required=True,
                        type=str,
                        help='directory path of SARscape imported data')
    parser.add_argument('-s',
                        dest='save_path',
                        type=str,
                        required=True,
                        help='path of saving slc')
    return parser


def main():
    # argument parser
    parser = cmdline_parser()
    args = parser.parse_args()
    burst_info = args.burst_info
    imported_path = args.imported_path
    save_path = args.save_path
    # check burst_info
    if not os.path.isfile(burst_info):
        print('Error file, please reset it!')
    # check imported_path
    if not os.path.isdir(imported_path):
        print('Error directory, please reset it!')
    # check save_path
    if not os.path.isdir(save_path):
        print('Error directory, please reset it!')
    # get dates bursts
    dates, bursts = get_date_burst(burst_info)
    if len(dates) == 0 or len(bursts) == 0:
        print(f'Cannot find burst or date from {burst_info}')
        sys.exit()
    elif len(dates) != len(bursts):
        print('The number of date and burst are not equal!')
        sys.exit()
    else:
        print(f'Burst needed to copy and rename: {len(dates)}')
        for d, b in zip(dates, bursts):
            print(f'{d} {b}')
    # copy rename
    for d, b in zip(dates, bursts):
        date_copyed = copy_rename(imported_path, d, b, save_path)
        if date_copyed:
            index = dates.index(date_copyed)
            print(f'{date_copyed} {bursts[index]}')

if __name__ == "__main__":
    main()
