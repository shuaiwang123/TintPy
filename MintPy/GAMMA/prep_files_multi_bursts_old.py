#!/usr/bin/env python3

import os
import re
import argparse
import shutil
import glob
import sys


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Prepare files for MintPy time series processing.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument(
        'mintpy_dir', help='directory path for MintPy time series processing.')
    parser.add_argument('stacking_dir', help='directory path of stacking.')
    inps = parser.parse_args()

    return inps


INTRODUCTION = '''
-------------------------------------------------------------------  
   Prepare files for MintPy time series processing.
'''

EXAMPLE = """Usage:
  
  ./prep_files_multi_bursts_old.py /ly/mintpy /ly/stacking
  
------------------------------------------------------------------- 
"""


def copy_file(src, dst):
    if os.path.isfile(src):
        print('copy {} into {}'.format(src, dst))
        shutil.copy(src, dst)
    else:
        print("\n{} not exists.\n".format(src))


def main():
    inps = cmdLineParse()
    # get inputs
    mintpy_dir = inps.mintpy_dir
    stacking_dir = inps.stacking_dir
    mintpy_dir = os.path.abspath(mintpy_dir)
    stacking_dir = os.path.abspath(stacking_dir)
    if not os.path.isdir(mintpy_dir):
        os.mkdir(mintpy_dir)
    if not os.path.isdir(stacking_dir):
        print("{} not exists.".format(stacking_dir))
        sys.exit(1)

    # dir for mintpy
    geom_master_dir = os.path.join(mintpy_dir, 'geom_master')
    interferograms_dir = os.path.join(mintpy_dir, 'interferograms')
    if not os.path.isdir(geom_master_dir):
        os.mkdir(geom_master_dir)
    if not os.path.isdir(interferograms_dir):
        os.mkdir(interferograms_dir)

    tmp_files = os.listdir(stacking_dir)
    ifg_pairs = [i for i in tmp_files if re.match(r'\d{8}-\d{8}', i)]
    if len(ifg_pairs) < 1:
        print('no ifg_pair in {}.'.format(stacking_dir))
        sys.exit(1)
    # get range looks
    ifg_pair0 = os.path.join(stacking_dir, ifg_pairs[0])
    tmp_files = glob.glob(os.path.join(ifg_pair0, '*rlks*'))
    rlks = re.search(r'\d{2}rlks', tmp_files[0]).group()[0:-4]
    # flag for copying files into geom_master_dir
    flag = True

    for ifg in ifg_pairs:
        ifg_dir = os.path.join(stacking_dir, ifg)
        dst_ifg_dir = os.path.join(interferograms_dir, ifg)

        if not os.path.isdir(dst_ifg_dir):
            os.mkdir(dst_ifg_dir)

        if flag:
            # just copy once
            UTM_TO_RDC = ifg[0:8] + '_' + rlks + 'rlks.UTM_TO_RDC'
            UTM_TO_RDC_path = os.path.join(ifg_dir, UTM_TO_RDC)
            dst_UTM_TO_RDC_path = os.path.join(geom_master_dir,
                                               'sim_' + UTM_TO_RDC)
            copy_file(UTM_TO_RDC_path, dst_UTM_TO_RDC_path)

            diff_par = ifg[0:8] + '_' + rlks + 'rlks.diff_par'
            diff_par_path = os.path.join(ifg_dir, diff_par)
            dst_diff_par_path = os.path.join(geom_master_dir,
                                             'sim_' + diff_par)
            copy_file(diff_par_path, dst_diff_par_path)

            rdc_dem = ifg[0:8] + '_' + rlks + 'rlks.rdc.dem'
            rdc_dem_path = os.path.join(ifg_dir, rdc_dem)
            dst_rdc_dem_path = os.path.join(geom_master_dir, 'sim_' + rdc_dem)
            copy_file(rdc_dem_path, dst_rdc_dem_path)

            utm_dem = ifg[0:8] + '_' + rlks + 'rlks.utm.dem'
            utm_dem_path = os.path.join(ifg_dir, utm_dem)
            dst_utm_dem_path = os.path.join(geom_master_dir, 'sim_' + utm_dem)
            copy_file(utm_dem_path, dst_utm_dem_path)

            utm_dem_par = utm_dem + '.par'
            utm_dem_par_path = os.path.join(ifg_dir, utm_dem_par)
            dst_utm_dem_par_path = os.path.join(geom_master_dir, 'sim_' + utm_dem_par)
            copy_file(utm_dem_par_path, dst_utm_dem_par_path)

            flag = False

        off = ifg.replace('-', '_') + '_' + rlks + 'rlks.off'
        off_path = os.path.join(ifg_dir, off)
        dst_off_path = os.path.join(dst_ifg_dir, off)
        copy_file(off_path, dst_off_path)

        m_amp_par = ifg[0:8] + '_' + rlks + 'rlks.amp.par'
        m_amp_par_path = os.path.join(ifg_dir, m_amp_par)
        dst_m_amp_par_path = os.path.join(dst_ifg_dir, m_amp_par)
        copy_file(m_amp_par_path, dst_m_amp_par_path)

        s_amp_par = ifg[-8:] + '_' + rlks + 'rlks.amp.par'
        s_amp_par_path = os.path.join(ifg_dir, s_amp_par)
        dst_s_amp_par_path = os.path.join(dst_ifg_dir, s_amp_par)
        copy_file(s_amp_par_path, dst_s_amp_par_path)
        # copy cor in rdc
        cor = ifg.replace('-', '_') + '_' + rlks + 'rlks.diff_filt.cor'
        cor_path = os.path.join(ifg_dir, cor)
        dst_cor_path = os.path.join(dst_ifg_dir, 'filt_' + cor.replace('diff_filt.', ''))
        copy_file(cor_path, dst_cor_path)
        # copy unw in rdc
        unw = ifg.replace('-', '_') + '_' + rlks + 'rlks.diff_filt.unw'
        unw_path = os.path.join(ifg_dir, unw)
        dst_unw_path = os.path.join(dst_ifg_dir, 'diff_filt_' + unw.replace('diff_filt.', ''))
        copy_file(unw_path, dst_unw_path)

    print('\nall done.')
    sys.exit(1)


if __name__ == "__main__":
    main()
