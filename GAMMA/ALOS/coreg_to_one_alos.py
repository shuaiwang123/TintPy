#!/usr/bin/env python3
################################################################################
# co-register all of SLCs to a reference SLC using GAMMA for MintPy            #
# Copyright (c) 2020, Lei Yuan                                                 #
################################################################################

import os
import re
import argparse
import shutil
import glob
import sys


def cmd_line_parser():
    parser = argparse.ArgumentParser(description='Co-register all of the ALOS SLCs to a reference SLC.',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('slc_dir', help='directory path of SLCs', type=str)
    parser.add_argument('rslc_dir', help='directory path of RSLCs', type=str)
    parser.add_argument('--rlks',
                        help='range looks (defaults: 8)',
                        default='8', type=int)
    parser.add_argument('--alks',
                        help='azimuth looks (defaults: 16)',
                        default='16', type=int)
    parser.add_argument('--ref_slc',
                        help='reference SLC.(default: the first slc)',
                        default='0', type=str)
    inps = parser.parse_args()

    return inps


INTRODUCTION = '''
-------------------------------------------------------------------------
   Co-register all of the ALOS SLCs to a reference SLC.
'''

EXAMPLE = """Usage:
  
  ./coreg_to_one.py /ly/slc /ly/rslc
  ./coreg_to_one.py /ly/slc /ly/rslc --rlks 8 --alks 16 --ref_slc 20201111
  
-------------------------------------------------------------------------
"""


def read_gamma_par(par_file, keyword):
    value = ''
    with open(par_file, 'r') as f:
        for l in f.readlines():
            if l.count(keyword) == 1:
                tmp = l.split(':')
                value = tmp[1].strip()
    return value


def gen_bmp(slc, slc_par, rlks, alks):
    width = read_gamma_par(slc_par, 'range_samples')
    bmp = slc + '.bmp'
    call_str = f"rasSLC {slc} {width} 1 0 {rlks} {alks} 1. .35 1 0 0 {bmp}"
    os.system(call_str)


def main():
    inps = cmd_line_parser()
    slc_dir = inps.slc_dir
    rslc_dir = inps.rslc_dir
    rlks = inps.rlks
    alks = inps.alks
    ref_slc = inps.ref_slc

    # check slc_dir
    slc_dir = os.path.abspath(slc_dir)
    if not os.path.isdir(slc_dir):
        print("{} doesn't exists.".format(slc_dir))
        sys.exit(1)

    # check rslc_dir
    rslc_dir = os.path.abspath(rslc_dir)
    if not os.path.isdir(rslc_dir):
        os.mkdir(rslc_dir)

    # get all date
    tmp_files = os.listdir(slc_dir)
    all_date = sorted([i for i in tmp_files if re.findall(r'^\d{8}$', i)])
    if len(all_date) < 2:
        print('not enough SLCs.')
        sys.exit(1)

    # check ref_slc
    if ref_slc == '0':
        ref_slc = all_date[0]
    else:
        if re.findall(r'^\d{8}$', ref_slc):
            if not ref_slc in all_date:
                print('no slc for {}.'.format(ref_slc))
                sys.exit(1)
        else:
            print('error date.')
            sys.exit(1)

    m_date = ref_slc
    m_slc_dir = os.path.join(slc_dir, m_date)
    m_slc = os.path.join(m_slc_dir, m_date + '.slc')
    m_slc_par = m_slc + '.par'

    s_dates = all_date
    s_dates.remove(m_date)

    # copy reference slc to rsl_dir
    m_rslc_dir = os.path.join(rslc_dir, m_date)
    if not os.path.isdir(m_rslc_dir):
        os.mkdir(m_rslc_dir)
    # shutil.copy(m_slc, m_rslc_dir)
    # shutil.copy(m_slc_par, m_rslc_dir)

    for s_date in s_dates:
        s_slc_dir = os.path.join(slc_dir, s_date)
        s_slc = os.path.join(s_slc_dir, s_date + '.slc')
        s_slc_par = s_slc + '.par'
        s_rslc_dir = os.path.join(rslc_dir, s_date)

        if not os.path.isdir(s_rslc_dir):
            os.mkdir(s_rslc_dir)

        # change current directory
        os.chdir(s_rslc_dir)

        with open('create_offset', 'w+') as f:
            f.write(f"{m_date}-{s_date}\n")
            f.write(' 0 0\n')
            f.write(' 32 32\n')
            f.write(' 64 64\n')
            f.write(' 10.0\n')
            f.write(' 0')

        off = f'{m_date}-{s_date}.off'

        call_str = f'create_offset {m_slc_par} {s_slc_par} {off} 1 1 1 < create_offset'
        os.system(call_str)
        os.remove('create_offset')

        call_str = f'init_offset_orbit {m_slc_par} {s_slc_par} {off}'
        os.system(call_str)

        call_str = f'init_offset {m_slc} {s_slc} {m_slc_par} {s_slc_par} {off} 1 1'
        os.system(call_str)

        offs = f'{m_date}-{s_date}.offs'
        off_snr = f'{m_date}-{s_date}.off.snr'
        offsets = f'{m_date}-{s_date}.offsets'
        coffs = f'{m_date}-{s_date}.coffs'
        coffsets = f'{m_date}-{s_date}.coffsets'

        # estimate offsets for the first time
        call_str = f'offset_pwr {m_slc} {s_slc} {m_slc_par} {s_slc_par} {off} {offs} {off_snr} 256 256 {offsets} 2 200 200 7.0 1'
        os.system(call_str)
        call_str = f'offset_fit {offs} {off_snr} {off} {coffs} {coffsets} 9.0 6 0'
        os.system(call_str)

        shutil.copy(offsets, 'offsets_pwr_1')
        shutil.copy(coffsets, 'coffsets_pwr_1')

        os.remove(offs)
        os.remove(off_snr)
        os.remove(coffs)
        os.remove(coffsets)
        os.remove(offsets)

        # estimate offsets for the second time
        call_str = f'offset_pwr {m_slc} {s_slc} {m_slc_par} {s_slc_par} {off} {offs} {off_snr} 128 128 {offsets} 4 300 300 7.0 1'
        os.system(call_str)
        call_str = f'offset_fit {offs} {off_snr} {off} {coffs} {coffsets} 10.0 6 0'
        os.system(call_str)

        shutil.copy(offsets, 'offsets_pwr_2')
        shutil.copy(coffsets, 'coffsets_pwr_2')

        os.remove(offs)
        os.remove(off_snr)
        os.remove(coffs)
        os.remove(coffsets)
        os.remove(offsets)

        # co-registration of the tow SLC images
        s_rslc = s_date + '.rslc'
        s_rslc_par = s_rslc + '.par'
        call_str = f'SLC_interp {s_slc} {m_slc_par} {s_slc_par} {off} {s_rslc} {s_rslc_par}'
        os.system(call_str)

        gen_bmp(s_rslc, s_rslc_par, rlks, alks)

        # delete files
        save_files = []
        save_files.append(s_rslc)
        save_files.append(s_rslc_par)
        save_files.append(s_rslc + '.bmp')
        for f in os.listdir(s_rslc_dir):
            if f not in save_files:
                os.remove(f)

        # rename files
        os.rename(s_rslc, s_date + '.slc')
        os.rename(s_rslc_par, s_date + '.slc.par')
        os.rename(s_rslc + '.bmp', s_date + '.slc.bmp')

    print('\nAll done.\n')


if __name__ == "__main__":
    main()
