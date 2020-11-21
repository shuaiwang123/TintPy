#!/usr/bin/env python3
####################################
# Cut all of SLCs using GAMMA      #
# Copyright (c) 2020, Lei Yuan     #
####################################

import os
import re
import argparse
import shutil
import glob
import sys


def cmd_line_parser():
    parser = argparse.ArgumentParser(description='Cut all of co-registered SLCs.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=EXAMPLE)

    parser.add_argument('slc_dir', help='directory path of SLCs')
    parser.add_argument('save_dir',
                        help='directory path of saving cutted SLCs')
    parser.add_argument('roff',
                        help='offset to starting rangle sample',
                        type=int)
    parser.add_argument('nr', help='number of range samples', type=int)
    parser.add_argument('loff', help='offset to starting line', type=int)
    parser.add_argument('nl', help='number of lines to copy', type=int)
    parser.add_argument('--rlks',
                        help='range looks for generating bmp',
                        type=int,
                        default=20)
    parser.add_argument('--alks',
                        help='azimuth looks for generating bmp',
                        type=int,
                        default=5)

    inps = parser.parse_args()

    return inps


EXAMPLE = """Example:
   ./cut_all.py ./slc ./cut_slc 1 1000 1 1000
   ./cut_all.py ./slc ./cut_slc 1 1000 1 1000 --rlks 8 --rlks 2
"""


def read_gamma_par(par_file, keyword):
    value = ''
    with open(par_file, 'r') as f:
        for l in f.readlines():
            if l.count(keyword) == 1:
                tmp = l.split(':')
                value = tmp[1].strip()
    return value


def main():
    inps = cmd_line_parser()
    slc_dir = inps.slc_dir
    save_dir = inps.save_dir
    roff = inps.roff
    nr = inps.nr
    loff = inps.loff
    nl = inps.nl
    rlks = inps.rlks
    alks = inps.alks

    if not os.path.isdir(slc_dir):
        print('{} not exists.'.format(slc_dir))
        sys.exit(1)

    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)

    tmp_files = os.listdir(slc_dir)
    all_date = [i for i in tmp_files if re.findall(r'^\d{8}$', i)]

    if len(all_date) < 1:
        print('no slc in {}'.format(slc_dir))
        sys.exit(1)

    for d in all_date:
        slc = os.path.join(slc_dir, d, d + '.slc')
        slc_par = slc + '.par'

        cut_slc_dir = os.path.join(save_dir, d)
        slc_cut = os.path.join(cut_slc_dir, d + '.slc')
        slc_par_cut = slc_cut + '.par'

        if os.path.isfile(slc) and os.path.isfile(slc_par):
            if not os.path.isdir(cut_slc_dir):
                os.mkdir(cut_slc_dir)

            call_str = f"SLC_copy {slc} {slc_par} {slc_cut} {slc_par_cut} - - {roff} {nr} {loff} {nl} - -"
            os.system(call_str)

            width = read_gamma_par(slc_par_cut, 'range_samples')
            bmp = slc_cut + '.bmp'
            call_str = f"rasSLC {slc_cut} {width} 1 0 {rlks} {alks} 1. .35 1 0 0 {bmp}"
            os.system(call_str)
        else:
            print('slc or slc.par for {} not exists.\n'.format(d))


if __name__ == "__main__":
    main()
