#!/usr/bin/env python3

import os
import glob
import sys
import argparse
import re

INTRODUCTION = '''
#############################################################################
   
   Extract the bursts for S1 TOPs data.
'''

EXAMPLE = '''
    Usage:
            ./extract_s1_bursts.py slc_dir iw_num burst_num
            
    Examples:
            ./extract_s1_bursts.py /ly/slc '1 2' '1 3 2 4'
            (IW1 start_burst: 1 end_burst: 3)
            (IW2 start_burst: 2 end_burst: 4)
##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Extract the bursts for S1 TOPs data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('slc_dir', help='directory path including slc.')
    parser.add_argument('iw_num', help='IW num.', type=str)
    parser.add_argument('burst_num', help='burst_num.', type=str)
    parser.add_argument(
        '--rlks',
        help='range looks for SLC_mosaic_S1_TOPS (default: 20)',
        type=int,
        default=20)
    parser.add_argument(
        '--alks',
        help='azimuth looks for SLC_mosaic_S1_TOPS (default: 5)',
        type=int,
        default=5)

    inps = parser.parse_args()

    return inps


def read_gamma_par(par_file, keyword):
    value = ''
    with open(par_file, 'r') as f:
        for l in f.readlines():
            if l.count(keyword) == 1:
                tmp = l.split(':')
                value = tmp[1].strip()
    return value


def extract_one_swath(slc_path, date, iw, start_burst, end_burst, rlks, alks):
    SLC1_tab = os.path.join(slc_path, 'SLC1_tab')
    SLC2_tab = os.path.join(slc_path, 'SLC2_tab')
    slc = os.path.join(slc_path, date + '.iw' + iw + '.slc')
    slc_par = os.path.join(slc_path, date + '.iw' + iw + '.slc.par')
    tops_par = os.path.join(slc_path, date + '.iw' + iw + '.slc.tops_par')
    slc0 = os.path.join(slc_path, date + '.iw' + iw * 2 + '.slc')
    slc_par0 = os.path.join(slc_path, date + '.iw' + iw * 2 + '.slc.par')
    tops_par0 = os.path.join(slc_path, date + '.iw' + iw * 2 + '.slc.tops_par')
    # SLC_copy_S1_TOPS
    call_str = f"echo {slc} {slc_par} {tops_par} > {SLC1_tab}"
    os.system(call_str)
    call_str = f"echo {slc0} {slc_par0} {tops_par0} > {SLC2_tab}"
    os.system(call_str)
    call_str = f"SLC_copy_S1_TOPS {SLC1_tab} {SLC2_tab} 1 {start_burst} 1 {end_burst}"
    os.system(call_str)
    width = read_gamma_par(slc_par0, 'range_samples:')
    if width:
        bmp = slc0 + '.bmp'
        call_str = f"rasSLC {slc0} {width} 1 0 {rlks} {alks} 1. .35 1 0 0 {bmp}"
        os.system(call_str)
    # SLC_mosaic_S1_TOPS
    slc_out = os.path.join(slc_path, date + '.slc')
    slc_par_out = os.path.join(slc_path, date + '.slc.par')
    call_str = f"SLC_mosaic_S1_TOPS {SLC2_tab} {slc_out} {slc_par_out} {rlks} {alks}"
    os.system(call_str)
    width = read_gamma_par(slc_par_out, 'range_samples:')
    if width:
        bmp = slc_out + '.bmp'
        call_str = f"rasSLC {slc_out} {width} 1 0 {rlks} {alks} 1. .35 1 0 0 {bmp}"
        os.system(call_str)
    # delete files
    if os.path.isfile(SLC1_tab):
        os.remove(SLC1_tab)
    if os.path.isfile(SLC2_tab):
        os.remove(SLC2_tab)


def main():
    inps = cmdLineParse()
    slc_dir = inps.slc_dir
    slc_dir = os.path.abspath(slc_dir)
    iw_num = inps.iw_num
    iw_num = iw_num.split()
    burst_num = inps.burst_num
    burst_num = burst_num.split()
    rlks = inps.rlks
    alks = inps.alks

    # check input
    if not os.path.exists(slc_dir):
        print('{} not exists.'.format(slc_dir))
        sys.exit(1)

    files = os.listdir(slc_dir)
    all_date = []
    for i in files:
        if re.match(r'\d{8}', i):
            all_date.append(i)

    if all_date:
        for date in all_date:
            slc_path = os.path.join(slc_dir, date)
            if len(iw_num) == 1:
                extract_one_swath(slc_path, date, iw_num[0], burst_num[0], burst_num[1], rlks, alks)
            if len(iw_num) == 2:
                pass
            if len(iw_num) == 3:
                pass
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
