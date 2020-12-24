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
  ./extract_s1_bursts.py -s /ly/slc -o /ly/slc_extract -i 1 -t iw1.png -n 3
  # two swath
  ./extract_s1_bursts.py -s /ly/slc -o /ly/slc_extract -i 1 2 -t iw1.png iw2.png -n 3 4
  # three swath
  ./extract_s1_bursts.py -s /ly/slc -o /ly/slc_extract -i 1 2 3 -t iw1.png iw2.png iw3.png -n 3 4 3
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(
        description='Extract automatically Sentinel-1 bursts using GAMMA.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)

    parser.add_argument('-s',
                        dest='slc_dir',
                        help='directory path including original slc.',
                        type=str,
                        required=True)
    parser.add_argument('-o',
                        dest='out_slc_dir',
                        help='directory path saving extracted slc.',
                        type=str,
                        required=True)
    parser.add_argument('-i',
                        dest='iw_num',
                        help='IW num (from 1 2 3).',
                        type=int,
                        nargs='+',
                        choices=[1, 2, 3],
                        required=True)
    parser.add_argument(
        '-t',
        dest='template_burst',
        help=
        'template bursts image for finding relative location in original slc bursts image.',
        type=str,
        nargs='+',
        required=True)
    parser.add_argument('-n',
                        dest='burst_num',
                        help='burst number in template image.',
                        type=int,
                        nargs='+',
                        required=True)
    parser.add_argument(
        '--rlks',
        help='range looks (default: 20).',
        type=int,
        default=20)
    parser.add_argument(
        '--alks',
        help='azimuth looks (default: 5).',
        type=int,
        default=5)
    parser.add_argument(
        '--slc_num',
        help='number of slc used to extract bursts (default: -1, for all slcs)',
        type=int,
        default=-1)

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


def slc_copy_s1_tops(slc_path, out_slc_path, date, iw, start_burst_loc,
                     end_burst_loc, rlks, alks):
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
    call_str = f"SLC_copy_S1_TOPS {SLC1_tab} {SLC2_tab} 1 {start_burst_loc} 1 {end_burst_loc}"
    os.system(call_str)
    width = read_gamma_par(slc_par0, 'range_samples:')
    if width:
        bmp = slc0 + '.bmp'
        call_str = f"rasSLC {slc0} {width} 1 0 {rlks} {alks} 1. .35 1 0 0 {bmp}"
        os.system(call_str)
    return slc0, slc_par0, tops_par0


def extract_one_swath(slc_path, out_slc_path, date, iw, start_burst_loc,
                      end_burst_loc, rlks, alks):
    """copy and mosaic SLCs for one swath"""
    # SLC_copy_S1_TOPS
    slc1, slc_par1, tops_par1 = slc_copy_s1_tops(slc_path, out_slc_path, date,
                                                 iw, start_burst_loc,
                                                 end_burst_loc, rlks, alks)
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


def match_burst(temp_burst, temp_burst_num, orig_burst, orig_burst_num):
    """get location of start burst in original bursts image"""
    # read image
    img_temp = cv2.imread(temp_burst, 0)
    img_orig = cv2.imread(orig_burst, 0)
    w_orig, h_orig = img_orig.shape[::-1]
    h_single_burst = round(h_orig / orig_burst_num)
    h_temp = h_single_burst * temp_burst_num
    w_temp = w_orig
    # resize temp_burst
    img_temp = cv2.resize(img_temp, (w_temp, h_temp))
    # match image
    res = cv2.matchTemplate(img_orig, img_temp, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    # get start burst location
    start_burst_loc = round(top_left[1] / h_single_burst) + 1
    return start_burst_loc


def get_start_end_burst(temp_burst, temp_burst_num, orig_burst, tops_par_file):
    """get location of start burst and end burst"""
    orig_burst_num = int(read_gamma_par(tops_par_file, 'number_of_bursts:'))
    start_burst_loc = match_burst(temp_burst, temp_burst_num, orig_burst,
                                  orig_burst_num)
    end_burst_loc = start_burst_loc + temp_burst_num - 1
    if end_burst_loc > orig_burst_num:
        end_burst_loc = orig_burst_num
    return start_burst_loc, end_burst_loc


def main():
    # parse args
    inps = cmdLineParse()
    slc_dir = inps.slc_dir
    slc_dir = os.path.abspath(slc_dir)
    out_slc_dir = inps.out_slc_dir
    out_slc_dir = os.path.abspath(out_slc_dir)
    iw_num = inps.iw_num
    temp_burst_num = inps.burst_num
    temp_burst = inps.template_burst
    temp_burst = [os.path.abspath(i) for i in temp_burst]
    rlks = inps.rlks
    alks = inps.alks
    slc_num = inps.slc_num
    # check slc_dir
    if not os.path.isdir(slc_dir):
        print('{} does not exist.'.format(slc_dir))
        sys.exit(1)
    # check out_slc_dir
    if not os.path.isdir(out_slc_dir):
        os.mkdir(out_slc_dir)
    # check temp_burst
    for i in temp_burst:
        if not os.path.isfile(i):
            print('{} does not exist.'.format(i))
            sys.exit(1)
    # check iw_num
    if len(iw_num) != len(temp_burst_num):
        print('length of iw_num must be equal to burst_num.')
        sys.exit(1)
    if len(iw_num) != len(temp_burst):
        print('length of iw_num must be equal to template_burst.')
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
    # check slc_num
    if slc_num < -1:
        print('slc_num must bigger than -1.')
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
        if slc_num == -1 or slc_num >= len(all_date):
            length = len(all_date)
        else:
            length = slc_num
        for date in all_date[0:length]:
            slc_path = os.path.join(slc_dir, date)
            out_slc_path = os.path.join(out_slc_dir, date)
            if not os.path.isdir(out_slc_path):
                os.mkdir(out_slc_path)
            if len(iw_num) == 1:
                tops_par_file = os.path.join(
                    slc_path, date + '.iw' + str(iw_num[0]) + '.slc.tops_par')
                orig_burst = os.path.join(
                    slc_path, date + '.iw' + str(iw_num[0]) + '.slc.bmp')
                start_burst_loc, end_burst_loc = get_start_end_burst(
                    temp_burst[0], temp_burst_num[0], orig_burst,
                    tops_par_file)
                extract_one_swath(slc_path, out_slc_path, date, iw_num[0],
                                  start_burst_loc, end_burst_loc, rlks, alks)
            if len(iw_num) == 2 or len(iw_num) == 3:
                burst_num = []
                for i in iw_num:
                    tops_par_file = os.path.join(
                        slc_path, date + '.iw' + str(i) + '.slc.tops_par')
                    orig_burst = os.path.join(
                        slc_path, date + '.iw' + str(i) + '.slc.bmp')
                    index = iw_num.index(i)
                    start_burst_loc, end_burst_loc = get_start_end_burst(
                        temp_burst[index], temp_burst_num[index], orig_burst,
                        tops_par_file)
                    burst_num.append(start_burst_loc)
                    burst_num.append(end_burst_loc)
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
