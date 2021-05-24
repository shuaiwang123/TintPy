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
  python3 diff_tab.py /ly/stacking diff.int.gacos.sm.sub.unw 0.3 /ly/res
  python3 diff_tab.py /ly/stacking diff.int.gacos.sm.sub.unw 0.3 /ly/res --ce diff.gacos.sm.cc --de diff.par
"""


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description='write diff_tab for Phase-Stacking using GAMMA.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)

    parser.add_argument('ifg_dir', help='path of ifg directory.')
    parser.add_argument('unw_extension',
                        help='filename extension of unwrapped file.')
    parser.add_argument('coh',
                        help='coherence threshold (smaller than this will not be used) for Phase-Stacking.',
                        type=float)
    parser.add_argument('out_dir', help='directory path for saving diff_tab.')
    parser.add_argument('--ce', dest='coh_extension',
                        help='filename extension of coherence file (default: diff.sm.cc).', default='diff.sm.cc')
    parser.add_argument('--de', dest='diff_par_extension',
                        help='filename extension of diff.par file (default: diff.par).', default='diff.par')
    inps = parser.parse_args()

    return inps


def get_baseline(unw):
    name = os.path.basename(unw)
    dates = re.findall(r'\d{8}', name)
    date1 = datetime.datetime.strptime(dates[0], '%Y%m%d')
    date2 = datetime.datetime.strptime(dates[1], '%Y%m%d')
    baseline = (date2 - date1).days
    return baseline


def get_unws_cohs(ifg_dir, unw_extension, coh_extension):
    unws = glob.glob(os.path.join(ifg_dir, '*', '*' + unw_extension))
    cohs = []
    for unw in unws:
        dir_name = os.path.dirname(unw)
        coh_files = glob.glob(os.path.join(dir_name, '*' + coh_extension))
        if coh_files:
            cohs.append(coh_files[0])
    return unws, cohs


def get_diff_par(ifg_dir, diff_par_extension):
    diff_pars = glob.glob(os.path.join(ifg_dir, '*', '*' + diff_par_extension))
    if diff_pars:
        return diff_pars[0]
    return None


def read_diff_par(diff_par):
    par_key = ['range_samp_1', 'az_samp_1']
    par_value = []
    with open(diff_par, 'r') as f:
        for line in f.readlines():
            for i in par_key:
                if line.strip().startswith(i):
                    par_value.append(int(line.strip().split()[1]))
    return par_value


def read_coh(file, data_type, width, length):
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
        data = data.reshape(length, width)
    except Exception as e:
        print(e)
    return data


def get_mean_coh(cohs, diff_par):
    print('\nstatisticing coherence:')
    mean_coh_array = np.zeros(len(cohs))
    width, length = read_diff_par(diff_par)
    for coh in cohs:
        mean_coh = np.mean(read_coh(coh, 'float32', width, length))
        mean_coh_array[cohs.index(coh)] = mean_coh
    np.save('mean_coh_array', mean_coh_array)
    return mean_coh_array


def statistic_coh(mean_coh, step=0.05):
    def count_coh(start, end, coh_array):
        num = 0
        for i in coh_array:
            if i > start and i <= end:
                num += 1
        rate = num / coh_array.shape[0]
        print(str(start) + '~' + str(end) + ': ' + str(round(rate, 2)))

    for i in np.arange(0, 1, step):
        start = round(i, 2)
        end = round(start + step, 2)
        count_coh(start, end, mean_coh)


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
    unw_extension = inps.unw_extension
    coh_thres = inps.coh
    out_dir = os.path.abspath(inps.out_dir)
    coh_extension = inps.coh_extension
    diff_par_extension = inps.diff_par_extension

    # check out_dir
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    # get diff.par
    diff_par = get_diff_par(ifg_dir, diff_par_extension)
    if not diff_par:
        print('Cannot find any {} file'.format(diff_par_extension))
        sys.exit()

    # get unws
    unws, cohs = get_unws_cohs(ifg_dir, unw_extension, coh_extension)
    if len(unws) == 0:
        print('no unws in {}'.format(ifg_dir))
        sys.exit()

    if len(unws) == len(cohs):
        # statistic coherence
        if os.path.isfile('mean_coh_array.npy'):
            mean_coh_array = np.load('mean_coh_array.npy')
        else:
            mean_coh_array = get_mean_coh(cohs, diff_par)
        statistic_coh(mean_coh_array)

        # write diff_tab
        write_diff_tab(unws, mean_coh_array, coh_thres, out_dir)
    else:
        print('The length of unws cohs and diff_pars are not equal.')
        sys.exit()


if __name__ == "__main__":
    main()
