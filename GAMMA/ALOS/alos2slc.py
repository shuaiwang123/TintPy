#!/usr/bin/env python3
########################################################################################################
# Reformat EORC PALSAR + PALSAR2 level 1.1 CEOS format SLC data and generate the ISP parameter file    #
# Copyright (c) 2020, Lei Yuan                                                                         #
########################################################################################################
import argparse
import glob
import os
import re
import sys


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description=
        'Reformat EORC PALSAR + PALSAR2 level 1.1 CEOS format SLC data and generate the ISP parameter file',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-s', dest='slc_dir', help='directory including ALOS raw data (**unzip data first**)')
    parser.add_argument('-o', dest='output_dir', help='directory saving ALOS SLC')
    parser.add_argument('--rlks',
                        help='range looks (defaults: 8)',
                        default=8,
                        type=int)
    parser.add_argument('--alks',
                        help='azimuth looks (defaults: 16)',
                        default=16,
                        type=int)

    inps = parser.parse_args()
    return inps


def get_raw_slc(slc_dir):
    all_slc = []
    files = os.listdir(slc_dir)
    for file in files:
        if re.search(r'\d{10}_\d{6}_ALOS\d{10}-\d{6}', file):
            if os.path.isdir(os.path.join(slc_dir, file)):
                all_slc.append(file)
    return all_slc


def read_gamma_par(par_file, keyword):
    value = ''
    with open(par_file, 'r') as f:
        for l in f.readlines():
            if l.count(keyword) == 1:
                tmp = l.split(':')
                value = tmp[1].strip()
    return value


def view_amp(slc, slc_par, rlks, alks):
    width = read_gamma_par(slc_par, 'range_samples')
    if width:
        bmp = slc + '.bmp'
        call_str = f"rasSLC {slc} {width} 1 0 {rlks} {alks} 1. .35 1 0 0 {bmp}"
        os.system(call_str)
    else:
        print('cannot find range_samples in {}'.format(slc_par))


def reformat_alos(slc_dir, output_dir, rlks, alks):
    # get absolute path
    slc_dir = os.path.abspath(slc_dir)
    output_dir = os.path.abspath(output_dir)
    # check slc_dir
    if not os.path.isdir(slc_dir):
        print('cannot find this directory: {}'.format(slc_dir))
        sys.exit()
    # check output_dir
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    # get all slc
    all_raw_slc = get_raw_slc(slc_dir)
    # reformat alos data
    if all_raw_slc:
        for slc in all_raw_slc:
            slc_path = os.path.join(slc_dir, slc)
            img = glob.glob(os.path.join(slc_path, 'IMG-HH-ALOS*'))
            led = glob.glob(os.path.join(slc_path, 'LED-ALOS*'))
            date = '20' + slc[-6:]
            output_path = os.path.join(output_dir, date)
            if not os.path.isdir(output_path):
                os.mkdir(output_path)
            if os.path.isfile(img[0]) and os.path.isfile(led[0]):
                out_slc = os.path.join(output_path, date + '.slc')
                out_slc_par = os.path.join(output_path, date + '.slc.par')
                cmd_str = f"par_EORC_PALSAR {led[0]} {out_slc_par} {img[0]} {out_slc}"
                os.system(cmd_str)
                # quickview amplitude
                view_amp(out_slc, out_slc_par, rlks, alks)
    else:
        print('cannot find any slc in {}'.format(output_dir))
        sys.exit()



def main():
    inps = cmdline_parser()
    slc_dir = inps.slc_dir
    output_dir = inps.output_dir
    rlks = inps.rlks
    alks = inps.alks
    reformat_alos(slc_dir, output_dir, rlks, alks)


if __name__ == "__main__":
    main()

