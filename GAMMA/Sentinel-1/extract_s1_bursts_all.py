#!/usr/bin/env python3
############################################
# Extract Sentinel-1 bursts using GAMMA    #
# Copyright (c) 2020, Lei Yuan             #
############################################

import os
import glob
import sys
import argparse
import re

EXAMPLE = '''Example:
    # one swath
    python3 extract_s1_bursts.py /ly/slc '1' '1 3'
    (Note: swath1 start_burst: 1 end_burst: 3)
    # multi swath
    python3 extract_s1_bursts.py /ly/slc '1 2' '1 3 2 4' --rlks 8 --alks 2
    (Note: swath1 start_burst: 1 end_burst: 3, swath2 start_burst: 2 end_burst: 4)
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Extract bursts for Sentinel-1 TOPS data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=EXAMPLE)

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


def slc_copy_s1_tops(slc_path, date, iw, start_burst, end_burst, rlks, alks):
    # write SLC_tab
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
    return slc0, slc_par0, tops_par0


def extract_one_swath(slc_path, date, iw, start_burst, end_burst, rlks, alks):
    # SLC_copy_S1_TOPS
    slc1, slc_par1, tops_par1 = slc_copy_s1_tops(slc_path, date, iw,
                                                 start_burst, end_burst, rlks,
                                                 alks)
    # SLC_mosaic_S1_TOPS
    mosaiclist = os.path.join(slc_path, 'mosaiclist')
    call_str = f"echo {slc1} {slc_par1} {tops_par1} > {mosaiclist}"
    os.system(call_str)
    slc_out = os.path.join(slc_path, date + '.slc')
    slc_par_out = os.path.join(slc_path, date + '.slc.par')
    call_str = f"SLC_mosaic_S1_TOPS {mosaiclist} {slc_out} {slc_par_out} {rlks} {alks}"
    os.system(call_str)
    width = read_gamma_par(slc_par_out, 'range_samples:')
    if width:
        bmp = slc_out + '.bmp'
        call_str = f"rasSLC {slc_out} {width} 1 0 {rlks} {alks} 1. .35 1 0 0 {bmp}"
        os.system(call_str)
    # delete files
    SLC1_tab = os.path.join(slc_path, 'SLC1_tab')
    SLC2_tab = os.path.join(slc_path, 'SLC2_tab')
    if os.path.isfile(SLC1_tab):
        os.remove(SLC1_tab)
    if os.path.isfile(SLC2_tab):
        os.remove(SLC2_tab)


def extract_two_swath(slc_path, date, iws, bursts, rlks, alks):
    # SLC_copy_S1_TOPS for first swath
    slc1, slc_par1, tops_par1 = slc_copy_s1_tops(slc_path, date, iws[0],
                                                 bursts[0], bursts[1], rlks,
                                                 alks)
    # SLC_copy_S1_TOPS for second swath
    slc2, slc_par2, tops_par2 = slc_copy_s1_tops(slc_path, date, iws[1],
                                                 bursts[2], bursts[3], rlks,
                                                 alks)
    # SLC_mosaic_S1_TOPS
    mosaiclist = os.path.join(slc_path, 'mosaiclist')
    call_str = f"echo {slc1} {slc_par1} {tops_par1} > {mosaiclist}"
    os.system(call_str)
    call_str = f"echo {slc2} {slc_par2} {tops_par2} >> {mosaiclist}"
    os.system(call_str)
    slc_out = os.path.join(slc_path, date + '.slc')
    slc_par_out = os.path.join(slc_path, date + '.slc.par')
    call_str = f"SLC_mosaic_S1_TOPS {mosaiclist} {slc_out} {slc_par_out} {rlks} {alks}"
    os.system(call_str)
    width = read_gamma_par(slc_par_out, 'range_samples:')
    if width:
        bmp = slc_out + '.bmp'
        call_str = f"rasSLC {slc_out} {width} 1 0 {rlks} {alks} 1. .35 1 0 0 {bmp}"
        os.system(call_str)
    # delete files
    SLC1_tab = os.path.join(slc_path, 'SLC1_tab')
    SLC2_tab = os.path.join(slc_path, 'SLC2_tab')
    if os.path.isfile(SLC1_tab):
        os.remove(SLC1_tab)
    if os.path.isfile(SLC2_tab):
        os.remove(SLC2_tab)
    if os.path.isfile(mosaiclist):
        os.remove(mosaiclist)


def extract_three_swath(slc_path, date, iws, bursts, rlks, alks):
    # SLC_copy_S1_TOPS for first swath
    slc1, slc_par1, tops_par1 = slc_copy_s1_tops(slc_path, date, iws[0],
                                                 bursts[0], bursts[1], rlks,
                                                 alks)
    # SLC_copy_S1_TOPS for second swath
    slc2, slc_par2, tops_par2 = slc_copy_s1_tops(slc_path, date, iws[1],
                                                 bursts[2], bursts[3], rlks,
                                                 alks)
    # SLC_copy_S1_TOPS for third swath
    slc3, slc_par3, tops_par3 = slc_copy_s1_tops(slc_path, date, iws[2],
                                                 bursts[4], bursts[5], rlks,
                                                 alks)
    # SLC_mosaic_S1_TOPS
    mosaiclist = os.path.join(slc_path, 'mosaiclist')
    call_str = f"echo {slc1} {slc_par1} {tops_par1} > {mosaiclist}"
    os.system(call_str)
    call_str = f"echo {slc2} {slc_par2} {tops_par2} >> {mosaiclist}"
    os.system(call_str)
    call_str = f"echo {slc3} {slc_par3} {tops_par3} >> {mosaiclist}"
    os.system(call_str)
    slc_out = os.path.join(slc_path, date + '.slc')
    slc_par_out = os.path.join(slc_path, date + '.slc.par')
    call_str = f"SLC_mosaic_S1_TOPS {mosaiclist} {slc_out} {slc_par_out} {rlks} {alks}"
    os.system(call_str)
    width = read_gamma_par(slc_par_out, 'range_samples:')
    if width:
        bmp = slc_out + '.bmp'
        call_str = f"rasSLC {slc_out} {width} 1 0 {rlks} {alks} 1. .35 1 0 0 {bmp}"
        os.system(call_str)
    # delete files
    SLC1_tab = os.path.join(slc_path, 'SLC1_tab')
    SLC2_tab = os.path.join(slc_path, 'SLC2_tab')
    if os.path.isfile(SLC1_tab):
        os.remove(SLC1_tab)
    if os.path.isfile(SLC2_tab):
        os.remove(SLC2_tab)
    if os.path.isfile(mosaiclist):
        os.remove(mosaiclist)


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
    slc_dir = os.path.abspath(slc_dir)
    if not os.path.exists(slc_dir):
        print('{} not exists.'.format(slc_dir))
        sys.exit(1)

    files = os.listdir(slc_dir)
    all_date = []
    for i in files:
        if re.findall(r'^\d{8}$', i):
            all_date.append(i)

    if all_date:
        for date in all_date:
            slc_path = os.path.join(slc_dir, date)
            if len(iw_num) == 1:
                extract_one_swath(slc_path, date, iw_num[0], burst_num[0],
                                  burst_num[1], rlks, alks)
            if len(iw_num) == 2:
                extract_two_swath(slc_path, date, iw_num, burst_num, rlks,
                                  alks)
            if len(iw_num) == 3:
                extract_three_swath(slc_path, date, iw_num, burst_num, rlks,
                                    alks)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
