#!/usr/bin/env python3
#####################################################
# Stack processing using GAMMA for MintPy           #
# Copyright (c) 2020, Lei Yuan                      #
#####################################################

import os
import re
import sys
import glob
import argparse

dinsar_script = """m_slc=$slc_dir/$m_date/$m_date.slc
m_par=$m_slc.par
s_slc=$slc_dir/$s_date/$s_date.slc
s_par=$s_slc.par


#####################################################
## 1. Refinement of geocoding lookup table         ##
#####################################################

multi_look $m_slc $m_par $m_date.mli $m_date.mli.par $rlks $alks
multi_look $s_slc $s_par $s_date.mli $s_date.mli.par $rlks $alks

width_mli=`awk '$1=="range_samples:" {print $2}' $m_date.mli.par`
length_mli=`awk '$1=="azimuth_lines:" {print $2}' $m_date.mli.par`

# generate lookup_table
gc_map $m_date.mli.par - $dem_par $dem dem_seg.par dem_seg lookup_table 1 1 $m_date.sim_sar u v inc psi pix ls_map 8 1
width_dem_seg=`awk '$1=="width:" {print $2}' dem_seg.par`

# Calculate terrain-based sigma0 and gammma0 normalization area in slant-range geometry
pixel_area $m_date.mli.par dem_seg.par dem_seg lookup_table ls_map inc pix_sigma0 pix_gamma0
raspwr pix_gamma0 $width_mli - - - - - - - pix_gamm0.bmp

# correction to the geocoding lookup table is determined and applied
create_diff_par $m_date.mli.par - $m_date.diff_par 1 0
offset_pwrm pix_sigma0 $m_date.mli $m_date.diff_par $m_date.offs $m_date.snr 64 64 offsets 2 100 100 5.0
offset_fitm $m_date.offs $m_date.snr $m_date.diff_par coffs coffsets 5.0 1

# Geocoding lookup table refinement using DIFF_par offset polynomials
gc_map_fine lookup_table $width_dem_seg $m_date.diff_par lookup_table_fine 1

# Use geocoding lookup table to geocode MLI image
geocode_back $m_date.mli $width_mli lookup_table_fine geo_$m_date.mli $width_dem_seg - 2 0

# raspwr geo_$m_date.mli $width_dem_seg 1 0 $rlks $alks 1. .35 1 geo_$m_date.mli.bmp
raspwr geo_$m_date.mli $width_dem_seg 1 0 1 1 1. .35 1 geo_$m_date.mli.bmp

# transform DEM heights into SAR geometry (of the MLI)
geocode lookup_table_fine dem_seg $width_dem_seg $m_date.hgt $width_mli $length_mli 2 0 
#rashgt $m_date.hgt $m_date.mli $width_mli 1 1 0 $rlks $alks 160.0 1. .35 1 $m_date.hgt.bmp
rashgt $m_date.hgt $m_date.mli $width_mli 1 1 0 1 1 160.0 1. .35 1 $m_date.hgt.bmp

###############################################################
## 2. S1 tops co-registration                                ##
## need iw*.slc iw*.slc.par iw*.slc.tops_par                 ##
###############################################################

# Derive lookup table for SLC/MLI coregistration (considering terrain heights)
rdc_trans $m_date.mli.par $m_date.hgt $s_date.mli.par $s_date.lt

echo $slc_dir/$s_date/$s_date.iw$iw$iw.slc $slc_dir/$s_date/$s_date.iw$iw$iw.slc.par $slc_dir/$s_date/$s_date.iw$iw$iw.slc.tops_par > SLC2_tab
echo $slc_dir/$m_date/$m_date.iw$iw$iw.slc $slc_dir/$m_date/$m_date.iw$iw$iw.slc.par $slc_dir/$m_date/$m_date.iw$iw$iw.slc.tops_par > SLC1_tab
echo $s_date.iw$iw.rslc $s_date.iw$iw.rslc.par $s_date.iw$iw.rslc.tops_par > RSLC2_tab

S1_coreg_TOPS SLC1_tab $m_date SLC2_tab $s_date RSLC2_tab $m_date.hgt $rlks $alks - - 0.8 0.1 0.8 1 

###############################################
## 3. Filter Differential Interferogram      ##
###############################################

width=$(awk '$1 == "interferogram_width:" {print $2}' ${m_date}_${s_date}.off)

adf ${m_date}_${s_date}.diff ${m_date}_${s_date}.diff_filt1 ${m_date}_${s_date}.diff_filt.cor1 $width 0.3 128
adf ${m_date}_${s_date}.diff_filt1 ${m_date}_${s_date}.diff_filt2 ${m_date}_${s_date}.diff_filt.cor2 $width 0.3 64
adf ${m_date}_${s_date}.diff_filt2 ${m_date}_${s_date}.diff_filt ${m_date}_${s_date}.diff_filt.cor $width 0.3 32

# rasmph ${m_date}_${s_date}.diff_filt  $width_mli 1 0 1 1 1. .35 1 ${m_date}_${s_date}.diff_filt.bmp
rasmph_pwr ${m_date}_${s_date}.diff_filt $m_date.mli $width 1 1 0 1 1 1. 0.35 1 ${m_date}_${s_date}.diff_filt.pwr.bmp

########################################################
## 4. Unwrap Differential Flattened Interferogram     ##
########################################################

rascc_mask ${m_date}_${s_date}.diff_filt.cor $m_date.mli $width 1 1 0 1 1 .05 .1 .9 1. .35 1 ${m_date}_${s_date}.diff_filt.cor_mask.bmp
mcf ${m_date}_${s_date}.diff_filt ${m_date}_${s_date}.diff_filt.cor ${m_date}_${s_date}.diff_filt.cor_mask.bmp ${m_date}_${s_date}.diff_filt.unw $width 1 0 0 - - 1 1 - - - 0

rasrmg ${m_date}_${s_date}.diff_filt.unw $m_date.mli $width  - - - - - - - - - - 
# rasrmg ${m_date}_${s_date}.diff_filt.unw - $width  - - - - - - - - - - 
"""


def cmd_line_parser():
    parser = argparse.ArgumentParser(description='Stack processing of Sentinel-1 SLCs.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('slc_dir', help='directory path of slc')
    parser.add_argument('stacking_dir', help='directory path of stacking')
    parser.add_argument('dem_dir', help='directory path of dem and dem.par')
    parser.add_argument(
        'num_connections',
        help='number of interferograms between each date and subsequent dates',
        type=int)
    parser.add_argument('iw', help='iw ID for co-registration', type=int)
    parser.add_argument('--rlks',
                        help='range looks (defaults: 20)',
                        default='20',
                        type=int)
    parser.add_argument('--alks',
                        help='azimuth looks (defaults: 5)',
                        default='5',
                        type=int)
    inps = parser.parse_args()

    return inps


INTRODUCTION = '''
-------------------------------------------------------------------
   Stack processing of Sentinel-1 SLCs.
'''

EXAMPLE = """Usage:
  
  ./stacking.py /ly/slc /ly/stacking /ly/dem 4 2
  ./stacking.py /ly/slc /ly/stacking /ly/dem 4 2 --rlks 8 --alks 2
  
------------------------------------------------------------------- 
"""


def gen_ifg_pairs(slc_date, num_connections):
    slc_date = sorted(slc_date)
    ifg_pairs = []
    length = len(slc_date)
    for i in range(length):
        if i < length - num_connections:
            for j in range(num_connections):
                ifg_pairs.append(f"{slc_date[i]}-{slc_date[i + j + 1]}")
        else:
            for k in range(length - i - 1):
                ifg_pairs.append(f"{slc_date[i]}-{slc_date[i + k + 1]}")
    return ifg_pairs


def main():
    inps = cmd_line_parser()
    # get inputs
    slc_dir = inps.slc_dir
    stacking_dir = inps.stacking_dir
    num_connections = inps.num_connections
    dem_dir = inps.dem_dir
    rlks = inps.rlks
    alks = inps.alks
    iw = inps.iw

    slc_dir = os.path.abspath(slc_dir)
    stacking_dir = os.path.abspath(stacking_dir)
    dem_dir = os.path.abspath(dem_dir)

    # check dem and dem.par
    if os.path.isdir(dem_dir):
        dem = glob.glob(dem_dir + '/*.dem')
        dem_par = glob.glob(dem_dir + '/*.dem.par')
        if dem and dem_par:
            dem = dem[0]
            dem_par = dem_par[0]
        else:
            print('dem or dem.par not exists.')
            sys.exit(1)
    else:
        print('{} not exists.'.format(dem_dir))
        sys.exit(1)

    # check iw
    if not iw in [1, 2, 3]:
        print('error iw ID.')
        sys.exit(1)

    # get all date
    tmp_files = os.listdir(slc_dir)
    slc_date = [i for i in tmp_files if re.findall(r'^\d{8}$', i)]

    # check num_connections
    if num_connections > 0:
        if len(slc_date) - 1 < num_connections:
            print('not enough slcs to connect.')
            sys.exit(1)
    else:
        print('cannot set num_connections to 0.')
        sys.exit(1)

    if not os.path.isdir(stacking_dir):
        os.mkdir(stacking_dir)

    # generate ifg_pair
    ifg_pairs = gen_ifg_pairs(slc_date, num_connections)
    for i in ifg_pairs:
        # make ifg_pair dir
        path = os.path.join(stacking_dir, i)
        if not os.path.isdir(path):
            os.mkdir(path)

    for i in ifg_pairs:
        path = os.path.join(stacking_dir, i)

        # write dinsar script
        m_date = i.split('-')[0]
        s_date = i.split('-')[1]

        str_m_date = f"m_date={m_date}\n"
        str_s_date = f"s_date={s_date}\n"
        str_slc_dir = f"slc_dir={slc_dir}\n"
        str_dem = f"dem={dem}\n"
        str_dem_par = f"dem_par={dem_par}\n"
        str_rlks = f"rlks={rlks}\n"
        str_alks = f"alks={alks}\n"
        str_iw = f"iw={iw}\n"

        out_script = '#!/bin/sh\n\n' + str_m_date + str_s_date + str_slc_dir + str_dem + str_dem_par + str_rlks + str_alks + str_iw + dinsar_script
        out_script_path = os.path.join(path, i + '_DInSAR.sh')
        with open(out_script_path, 'w+') as f:
            f.write(out_script)

        # run dinsar script
        os.chdir(path)
        call_str = 'sh ' + i + '_DInSAR.sh'
        os.system(call_str)

        # delete files to save space
        save_files = [
            'lookup_table_fine', f'{m_date}.diff_par', f'{m_date}.hgt',
            'dem_seg', 'dem_seg.par', f'{m_date}_{s_date}.off',
            f'{m_date}.mli.par', f'{s_date}.mli.par',
            f'{m_date}_{s_date}.diff_filt.cor',
            f'{m_date}_{s_date}.diff_filt.unw',
            f'{m_date}_{s_date}.diff_filt.pwr.bmp',
            f'{m_date}_{s_date}.diff_filt.unw.bmp'
        ]
        all_files = os.listdir(path)
        for file in all_files:
            if file not in save_files:
                os.remove(file)


if __name__ == "__main__":
    main()
