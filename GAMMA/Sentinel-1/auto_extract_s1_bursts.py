#!/usr/bin/env python3
#######################################################
# Extract automatically Sentinel-1 bursts using GAMMA #
# Copyright (c) 2020, Lei Yuan                        #
#######################################################

import argparse
import os
import re
import sys

try:
    import cv2
except ImportError:
    print(
        'cannot find model named cv2, you can install it using command pip install opencv-python'
    )
    sys.exit(1)

EXAMPLE = '''Example:
  # one swath
  ./extract_s1_bursts.py -s /ly/slc -o /ly/slc_cat -in 1 -bn 3 -bl 1 -bi iw1.png
  # two swath
  ./extract_s1_bursts.py -s /ly/slc -o /ly/slc_cat -in 1 2 -bn 3 4 -bl 1 2 -bi iw1.png iw2.png
  # three swath
  ./extract_s1_bursts.py -s /ly/slc -o /ly/slc_cat -in 1 2 3 -bn 3 4 3 -bl 1 2 1 -bi iw1.png iw2.png iw3.png
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(
        description='Extract automatically Sentinel-1 bursts using GAMMA.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)

    parser.add_argument('-s',
                        dest='slc_dir',
                        help='directory path including slc.',
                        type=str,
                        required=True)
    parser.add_argument('-o',
                        dest='out_slc_dir',
                        help='directory path saving extracted slc.',
                        type=str,
                        required=True)
    parser.add_argument('-in',
                        dest='iw_num',
                        help='IW num (from 1 2 3).',
                        type=int,
                        nargs='+',
                        required=True)
    parser.add_argument('-bn',
                        dest='burst_num',
                        help='number of extracted bursts.',
                        type=int,
                        nargs='+',
                        required=True)
    parser.add_argument('-bi',
                        dest='burst_image',
                        help='single burst image for finding relative location in bursts image (characteristic image is recommended).',
                        type=str,
                        nargs='+',
                        required=True)
    parser.add_argument('-bl',
                        dest='burst_location',
                        help='location of provided single burst in extracted slc (bigger than 0).',
                        type=int,
                        nargs='+',
                        required=True)
    parser.add_argument(
        '--rlks',
        help='range looks for SLC_mosaic_S1_TOPS (default: 20).',
        type=int,
        default=20)
    parser.add_argument(
        '--alks',
        help='azimuth looks for SLC_mosaic_S1_TOPS (default: 5).',
        type=int,
        default=5)

    inps = parser.parse_args()

    return inps


def read_gamma_par(par_file, keyword):
    """read gamma parmaeter using keyword"""
    value = ''
    with open(par_file, 'r') as f:
        for l in f.readlines():
            if l.count(keyword) == 1:
                tmp = l.split(':')
                value = tmp[1].strip()
    return value


def slc_copy_s1_tops(slc_path, out_slc_path, date, iw, start_burst, end_burst,
                     rlks, alks):
    """copy SLCs"""
    # write SLC_tab
    iw = str(iw)
    SLC1_tab = os.path.join(out_slc_path, 'SLC1_tab')
    SLC2_tab = os.path.join(out_slc_path, 'SLC2_tab')
    slc = os.path.join(slc_path, date + '.iw' + iw + '.slc')
    slc_par = os.path.join(slc_path, date + '.iw' + iw + '.slc.par')
    tops_par = os.path.join(slc_path, date + '.iw' + iw + '.slc.tops_par')
    slc0 = os.path.join(out_slc_path, date + '.iw' + iw * 2 + '.slc')
    slc_par0 = os.path.join(out_slc_path, date + '.iw' + iw * 2 + '.slc.par')
    tops_par0 = os.path.join(out_slc_path,
                             date + '.iw' + iw * 2 + '.slc.tops_par')
    # SLC_copy_S1_TOPS
    os.chdir(out_slc_path)
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


def extract_one_swath(slc_path, out_slc_path, date, iw, start_burst, end_burst,
                      rlks, alks):
    """copy and mosaic SLCs for one swath"""
    # SLC_copy_S1_TOPS
    slc1, slc_par1, tops_par1 = slc_copy_s1_tops(slc_path, out_slc_path, date,
                                                 iw, start_burst, end_burst,
                                                 rlks, alks)
    # SLC_mosaic_S1_TOPS
    os.chdir(out_slc_path)
    mosaiclist = os.path.join(out_slc_path, 'mosaiclist')
    call_str = f"echo {slc1} {slc_par1} {tops_par1} > {mosaiclist}"
    os.system(call_str)
    slc_out = os.path.join(out_slc_path, date + '.slc')
    slc_par_out = os.path.join(out_slc_path, date + '.slc.par')
    call_str = f"SLC_mosaic_S1_TOPS {mosaiclist} {slc_out} {slc_par_out} {rlks} {alks}"
    os.system(call_str)
    width = read_gamma_par(slc_par_out, 'range_samples:')
    if width:
        bmp = slc_out + '.bmp'
        call_str = f"rasSLC {slc_out} {width} 1 0 {rlks} {alks} 1. .35 1 0 0 {bmp}"
        os.system(call_str)
    # delete files
    SLC1_tab = os.path.join(out_slc_path, 'SLC1_tab')
    SLC2_tab = os.path.join(out_slc_path, 'SLC2_tab')
    if os.path.isfile(SLC1_tab):
        os.remove(SLC1_tab)
    if os.path.isfile(SLC2_tab):
        os.remove(SLC2_tab)
    if os.path.isfile(mosaiclist):
        os.remove(mosaiclist)


def extract_two_swath(slc_path, out_slc_path, date, iws, bursts, rlks, alks):
    """copy and mosaic SLCs for two swath"""
    # SLC_copy_S1_TOPS for first swath
    slc1, slc_par1, tops_par1 = slc_copy_s1_tops(slc_path, out_slc_path, date,
                                                 iws[0], bursts[0], bursts[1],
                                                 rlks, alks)
    # SLC_copy_S1_TOPS for second swath
    slc2, slc_par2, tops_par2 = slc_copy_s1_tops(slc_path, out_slc_path, date,
                                                 iws[1], bursts[2], bursts[3],
                                                 rlks, alks)
    # SLC_mosaic_S1_TOPS
    os.chdir(out_slc_path)
    mosaiclist = os.path.join(out_slc_path, 'mosaiclist')
    call_str = f"echo {slc1} {slc_par1} {tops_par1} > {mosaiclist}"
    os.system(call_str)
    call_str = f"echo {slc2} {slc_par2} {tops_par2} >> {mosaiclist}"
    os.system(call_str)
    slc_out = os.path.join(out_slc_path, date + '.slc')
    slc_par_out = os.path.join(out_slc_path, date + '.slc.par')
    call_str = f"SLC_mosaic_S1_TOPS {mosaiclist} {slc_out} {slc_par_out} {rlks} {alks}"
    os.system(call_str)
    width = read_gamma_par(slc_par_out, 'range_samples:')
    if width:
        bmp = slc_out + '.bmp'
        call_str = f"rasSLC {slc_out} {width} 1 0 {rlks} {alks} 1. .35 1 0 0 {bmp}"
        os.system(call_str)
    # delete files
    SLC1_tab = os.path.join(out_slc_path, 'SLC1_tab')
    SLC2_tab = os.path.join(out_slc_path, 'SLC2_tab')
    if os.path.isfile(SLC1_tab):
        os.remove(SLC1_tab)
    if os.path.isfile(SLC2_tab):
        os.remove(SLC2_tab)
    if os.path.isfile(mosaiclist):
        os.remove(mosaiclist)


def extract_three_swath(slc_path, out_slc_path, date, iws, bursts, rlks, alks):
    """copy and mosaic SLCs for three swath"""
    # SLC_copy_S1_TOPS for first swath
    slc1, slc_par1, tops_par1 = slc_copy_s1_tops(slc_path, out_slc_path, date,
                                                 iws[0], bursts[0], bursts[1],
                                                 rlks, alks)
    # SLC_copy_S1_TOPS for second swath
    slc2, slc_par2, tops_par2 = slc_copy_s1_tops(slc_path, out_slc_path, date,
                                                 iws[1], bursts[2], bursts[3],
                                                 rlks, alks)
    # SLC_copy_S1_TOPS for third swath
    slc3, slc_par3, tops_par3 = slc_copy_s1_tops(slc_path, out_slc_path, date,
                                                 iws[2], bursts[4], bursts[5],
                                                 rlks, alks)
    # SLC_mosaic_S1_TOPS
    os.chdir(out_slc_path)
    mosaiclist = os.path.join(out_slc_path, 'mosaiclist')
    call_str = f"echo {slc1} {slc_par1} {tops_par1} > {mosaiclist}"
    os.system(call_str)
    call_str = f"echo {slc2} {slc_par2} {tops_par2} >> {mosaiclist}"
    os.system(call_str)
    call_str = f"echo {slc3} {slc_par3} {tops_par3} >> {mosaiclist}"
    os.system(call_str)
    slc_out = os.path.join(out_slc_path, date + '.slc')
    slc_par_out = os.path.join(out_slc_path, date + '.slc.par')
    call_str = f"SLC_mosaic_S1_TOPS {mosaiclist} {slc_out} {slc_par_out} {rlks} {alks}"
    os.system(call_str)
    width = read_gamma_par(slc_par_out, 'range_samples:')
    if width:
        bmp = slc_out + '.bmp'
        call_str = f"rasSLC {slc_out} {width} 1 0 {rlks} {alks} 1. .35 1 0 0 {bmp}"
        os.system(call_str)
    # delete files
    SLC1_tab = os.path.join(out_slc_path, 'SLC1_tab')
    SLC2_tab = os.path.join(out_slc_path, 'SLC2_tab')
    if os.path.isfile(SLC1_tab):
        os.remove(SLC1_tab)
    if os.path.isfile(SLC2_tab):
        os.remove(SLC2_tab)
    if os.path.isfile(mosaiclist):
        os.remove(mosaiclist)


def match_burst(dest_burst, src_burst, burst_num):
    """get number of start burst using image of start burst"""
    # read image
    img_target = cv2.imread(dest_burst, 0)
    img_src = cv2.imread(src_burst, 0)
    w_src, h_src = img_src.shape[::-1]
    h_burst = round(h_src / burst_num)
    w_burst = w_src
    # resize dest_burst
    img_target = cv2.resize(img_target, (w_burst, h_burst))
    # match image
    res = cv2.matchTemplate(img_src, img_target, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    # get start burst
    matched_burst_loc = round(top_left[1] / h_burst) + 1
    return matched_burst_loc


def get_start_end_burst(dest_burst, src_burst, tops_par_file,
                        extracted_burst_num, burst_loc):
    """get start burst and end burst"""
    all_burst_num = int(read_gamma_par(tops_par_file, 'number_of_bursts:'))
    matched_burst_loc = match_burst(dest_burst, src_burst, all_burst_num)
    start_burst = matched_burst_loc - burst_loc + 1
    end_burst = start_burst + extracted_burst_num - 1
    if end_burst > all_burst_num:
        end_burst = all_burst_num
    return start_burst, end_burst


def main():
    # parse args
    inps = cmdLineParse()
    slc_dir = inps.slc_dir
    slc_dir = os.path.abspath(slc_dir)
    out_slc_dir = inps.out_slc_dir
    out_slc_dir = os.path.abspath(out_slc_dir)
    iw_num = inps.iw_num
    extracted_burst_num = inps.burst_num
    burst_image = inps.burst_image
    burst_image = [os.path.abspath(i) for i in burst_image]
    burst_locs = inps.burst_location
    rlks = inps.rlks
    alks = inps.alks
    # check slc_dir
    if not os.path.isdir(slc_dir):
        print('{} does not exist.'.format(slc_dir))
        sys.exit(1)
    # check out_slc_dir
    if not os.path.isdir(out_slc_dir):
        os.mkdir(out_slc_dir)
    # check burst_image
    for i in burst_image:
        if not os.path.isfile(i):
            print('{} does not exist.'.format(i))
            sys.exit(1)
    # check iw_num
    if len(iw_num) != len(extracted_burst_num):
        print('length of iw_num must be equal to burst_num.')
        sys.exit(1)
    if len(iw_num) == 1:
        if iw_num[0] not in [1, 2, 3]:
            print('Error iw_num for one IW, must be 1 or 2 or 3.')
            sys.exit(1)
    if len(iw_num) == 2:
        if iw_num == [1, 2] and [2, 3]:
            pass
        else:
            print('Error iw_num for two IWs, must be 1 2 or 2 3.')
            sys.exit(1)
    if len(iw_num) == 3:
        if iw_num != [1, 2, 3]:
            print('Error iw_num for three IWs, must be 1 2 3.')
            sys.exit(1)
    # get all date
    files = os.listdir(slc_dir)
    all_date = []
    for i in files:
        if re.findall(r'^\d{8}$', i):
            all_date.append(i)
    all_date = sorted(all_date)
    # copy and mosaic slcs
    if all_date:
        for date in all_date:
            slc_path = os.path.join(slc_dir, date)
            out_slc_path = os.path.join(out_slc_dir, date)
            if not os.path.isdir(out_slc_path):
                os.mkdir(out_slc_path)
            if len(iw_num) == 1:
                tops_par_file = os.path.join(
                    slc_path, date + '.iw' + str(iw_num[0]) + '.slc.tops_par')
                slc_bmp = os.path.join(
                    slc_path, date + '.iw' + str(iw_num[0]) + '.slc.bmp')
                start_burst, end_burst = get_start_end_burst(
                    burst_image[0], slc_bmp, tops_par_file,
                    extracted_burst_num[0], burst_locs[0])
                extract_one_swath(slc_path, out_slc_path, date, iw_num[0],
                                  start_burst, end_burst, rlks, alks)
            if len(iw_num) == 2 or len(iw_num) == 3:
                burst_num = []
                for i in iw_num:
                    tops_par_file = os.path.join(
                        slc_path, date + '.iw' + str(i) + '.slc.tops_par')
                    slc_bmp = os.path.join(slc_path,
                                           date + '.iw' + str(i) + '.slc.bmp')
                    index = iw_num.index(i)
                    start_burst, end_burst = get_start_end_burst(
                        burst_image[index], slc_bmp, tops_par_file,
                        extracted_burst_num[index], burst_locs[index])
                    burst_num.append(start_burst)
                    burst_num.append(end_burst)
                if len(iw_num) == 2:
                    extract_two_swath(slc_path, out_slc_path, date, iw_num,
                                      burst_num, rlks, alks)
                else:
                    extract_three_swath(slc_path, out_slc_path, date, iw_num,
                                        burst_num, rlks, alks)
        print('\nall done, enjoy it.\n')
    else:
        print('\ncannot find any data in {}.\n'.format(slc_dir))


if __name__ == "__main__":
    main()
