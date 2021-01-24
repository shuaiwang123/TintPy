#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#####################################################
# write diff_tab for Phase-Stacking using GAMMA     #
# Author: Yuan Lei, 2020                            #
#####################################################
import argparse
import datetime
import glob
import os
import re
import sys
import numpy as np

EXAMPLE = """Example:
  ./diff_tab.py /ly/stacking diff.int.sm.unw 0.3 /ly/stacking
"""


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description='write diff_tab for Phase-Stacking using GAMMA.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)

    parser.add_argument('ifg_dir', help='path of ifg directory.')
    parser.add_argument('extension',
                        help='filename extension of unwrapped file.')
    parser.add_argument('coh',
                        help='coherence threshold for Phase-Stacking.',
                        type=float)
    parser.add_argument('out_dir', help='path of directory saving diff_tab.')

    inps = parser.parse_args()

    return inps


def get_baseline(unw):
    name = os.path.basename(unw)
    dates = re.findall(r'\d{8}', name)
    date1 = datetime.datetime.strptime(dates[0], '%Y%m%d')
    date2 = datetime.datetime.strptime(dates[1], '%Y%m%d')
    baseline = (date2 - date1).days
    return baseline


def get_unws_cohs_diff_pars(ifg_dir, unw_extension, coh_extension, diff_par_extension):
    unws = glob.glob(os.path.join(ifg_dir, '*/*' + unw_extension))
    cohs = []
    diff_pars = []
    for unw in unws:
        dir_name = os.path.dirname(unw)
        coh = glob.glob(os.path.join(dir_name, '*' + coh_extension))[0]
        cohs.append(coh)
        diff_par = glob.glob(os.path.join(
            dir_name, '*' + diff_par_extension))[0]
        diff_pars.append(diff_par)
    return unws, cohs, diff_pars


def read_diff_par(diff_par):
    par_key = ['range_samp_1', 'az_samp_1']
    par_value = []
    with open(diff_par, 'r') as f:
        for line in f.readlines():
            for i in par_key:
                if line.strip().startswith(i):
                    par_value.append(int(line.strip().split()[1]))
    return par_value


def read_coh(file, data_type, diff_par):
    # unw, cor, dem_seg -------> float32
    # int               -------> complex64
    # convert into short style
    letter, digit = re.findall(r'(\d+|\D+)', data_type)
    if len(letter) > 1:
        letter = letter[0]
        digit = int(int(digit) / 8)
    # > means big-endian, < means little-endian
    data_type = '>{}{}'.format(letter, digit)
    # read data
    try:
        data = np.fromfile(file, dtype=data_type)
        width, length = read_diff_par(diff_par)
        data = data.reshape(length, width)
    except Exception as e:
        print(e)
    return data


def statistic_coh(cohs, diff_pars):
    print('\nstatisticing coherence:')
    mean_coh_array = np.zeros(len(cohs))
    for coh, diff_par in zip(cohs, diff_pars):
        mean_coh = np.mean(read_coh(coh, 'float32', diff_par))
        mean_coh_array[cohs.index(coh)] = mean_coh

    def count_coh(start, end, coh_array):
        num = 0
        for i in coh_array:
            if i > start and i <= end:
                num += 1
        rate = num / coh_array.shape[0]
        print(str(start) + '~' + str(end) + ': ' + str(round(rate, 2)))

    step = 0.05
    for i in np.arange(0, 1, step):
        start = round(i, 2)
        end = round(start + step, 2)
        count_coh(start, end, mean_coh_array)

    return mean_coh_array


def write_diff_tab(unws, mean_coh_array, coh_thres, out_dir):
    diff_tab = os.path.join(out_dir, 'diff_tab')
    print('\nwriting data to {}'.format(diff_tab))
    unw_used = 0
    with open(diff_tab, 'w+') as f:
        for unw in unws:
            baseline = get_baseline(unw)
            coh = mean_coh_array[unws.index(unw)]
            if coh >= coh_thres:
                f.write(f"{unw} {baseline}\n")
                unw_used += 1
    print('unwrapped file used: {}/{} [{}]'.format(unw_used,
                                                   len(unws), round(unw_used / len(unws), 2)))
    print('\nall done, enjot it.\n')


def main():
    # get inputs
    inps = cmdline_parser()
    ifg_dir = os.path.abspath(inps.ifg_dir)
    unw_extension = inps.extension
    coh_thres = inps.coh
    out_dir = os.path.abspath(inps.out_dir)
    # check out_dir
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    # get unws
    coh_extension = 'diff.sm.cc'
    diff_par_extension = 'diff.par'
    unws, cohs, diff_pars = get_unws_cohs_diff_pars(
        ifg_dir, unw_extension, coh_extension, diff_par_extension)
    if len(unws) == 0:
        print('no unws in {}'.format(ifg_dir))
        sys.exit()
    if len(unws) == len(cohs) and len(unws) == len(diff_pars):
        # statistic coherence
        mean_coh_array = statistic_coh(cohs, diff_pars)
        # write diff_tab
        write_diff_tab(unws, mean_coh_array, coh_thres, out_dir)
    else:
        print('The length of unws cohs and diff_pars are not equal.')
        sys.exit()


if __name__ == "__main__":
    main()
