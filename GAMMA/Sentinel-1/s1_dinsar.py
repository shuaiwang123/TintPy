#!/usr/bin/env python3
##################################################
# Make D-InSAR with Sentinel-1 SLCs using GAMMA  #
# Copyright (c) 2020, Lei Yuan                   #
##################################################

import os
import argparse
import glob

script = """#!/bin/sh
m_dir=m_dir_flag
s_dir=s_dir_flag
m_date=m_date_flag
s_date=s_date_flag
dem=dem_flag
dem_par=$dem.par
rlks=rlks_flag
alks=alks_flag

m_slc=$m_dir/$m_date.slc
m_par=$m_slc.par
s_slc=$s_dir/$s_date.slc
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
# rashgt $m_date.hgt $m_date.mli $width_mli 1 1 0 $rlks $alks 160.0 1. .35 1 $m_date.hgt.bmp
rashgt $m_date.hgt $m_date.mli $width_mli 1 1 0 1 1 160.0 1. .35 1 $m_date.hgt.bmp

###############################################################
## 2. S1 tops co-registration                                ##
## need *iw**.slc *iw**.slc.par *iw**.slc.tops_par           ##
###############################################################

# Derive lookup table for SLC/MLI coregistration (considering terrain heights)
rdc_trans $m_date.mli.par $m_date.hgt $s_date.mli.par $s_date.lt

iw_info_flag

S1_coreg_TOPS SLC1_tab $m_date SLC2_tab $s_date RSLC2_tab $m_date.hgt $rlks $alks - - 0.8 0.1 0.8 1
# S1_coreg_TOPS SLC1_tab $m_date SLC2_tab $s_date RSLC2_tab $m_date.hgt $rlks $alks - - 0.7 0.01 0.7 1

###############################################
## 3. Filter Differential Interferogram      ##
###############################################

width=$(awk '$1 == "interferogram_width:" {print $2}' ${m_date}_${s_date}.off)

adf ${m_date}_${s_date}.diff ${m_date}_${s_date}.diff_filt1 ${m_date}_${s_date}.diff_filt.cor1 $width 0.3 128
adf ${m_date}_${s_date}.diff_filt1 ${m_date}_${s_date}.diff_filt2 ${m_date}_${s_date}.diff_filt.cor2 $width 0.3 64
adf ${m_date}_${s_date}.diff_filt2 ${m_date}_${s_date}.diff_filt ${m_date}_${s_date}.diff_filt.cor $width 0.3 32

rasmph ${m_date}_${s_date}.diff_filt  $width_mli 1 0 1 1 1. .35 1 ${m_date}_${s_date}.diff_filt.bmp
rasmph_pwr ${m_date}_${s_date}.diff_filt $m_date.mli $width 1 1 0 1 1 1. 0.35 1 ${m_date}_${s_date}.diff_filt.pwr.bmp

########################################################
## 4. Unwrap Differential Flattened Interferogram     ##
########################################################

rascc_mask ${m_date}_${s_date}.diff_filt.cor $m_date.mli $width 1 1 0 1 1 .05 .1 .9 1. .35 1 ${m_date}_${s_date}.diff_filt.cor_mask.bmp
mcf ${m_date}_${s_date}.diff_filt ${m_date}_${s_date}.diff_filt.cor ${m_date}_${s_date}.diff_filt.cor_mask.bmp ${m_date}_${s_date}.diff_filt.unw $width 1 0 0 - - 1 1 - - - 0

rasrmg ${m_date}_${s_date}.diff_filt.unw $m_date.mli $width  - - - - - - - - - -
#########################
## 5. geocode data     ##
#########################
geocode_back ${m_date}_${s_date}.diff_filt.cor $width lookup_table_fine geo_${m_date}_${s_date}.diff_filt.cor $width_dem_seg - 2 0
geocode_back ${m_date}_${s_date}.diff_filt $width lookup_table_fine geo_${m_date}_${s_date}.diff_filt $width_dem_seg - 2 0
geocode_back ${m_date}_${s_date}.diff_filt.unw $width lookup_table_fine geo_${m_date}_${s_date}.diff_filt.unw $width_dem_seg - 1 0

rascc geo_${m_date}_${s_date}.diff_filt.cor - $width_dem_seg 1 1 0 1 1 .1 .9 1. .35 1 geo_${m_date}_${s_date}.diff_filt.cor.bmp
rascc geo_${m_date}_${s_date}.diff_filt.unw - $width_dem_seg 1 1 0 1 1 .1 .9 1. .35 1 geo_${m_date}_${s_date}.diff_filt.unw.bmp
rasmph_pwr geo_${m_date}_${s_date}.diff_filt geo_$m_date.mli $width_dem_seg 1 1 0 1 1 1. 0.35 1 geo_${m_date}_${s_date}.diff_filt.pwr.bmp
"""

DATA_STRUCTURE = """Data structure:
  m_dir----- m_date.iw**.slc
         |-- m_date.iw**.slc.par
         |-- m_date.iw**.slc.tops_par
         |-- m_date.slc
         |-- m_date.slc.par
  s_dir----- s_date.iw**.slc
         |-- s_date.iw**.slc.par
         |-- s_date.iw**.slc.tops_par
         |-- s_date.slc
         |-- s_date.slc.par
  dem_dir--- *.dem
         |-- *.dem.par
"""

EXAMPLE = """Example:
  # one IW
  ./s1_dinsar.py -m /ly/slc/20201111 -s /ly/slc/20201229 -i 1 -d /ly/dem -o /ly/dinsar
  ./s1_dinsar.py -m /ly/slc/20201111 -s /ly/slc/20201229 -i 1 -d /ly/dem -o /ly/dinsar --rlks 8 --alks 2
  # two IWs
  ./s1_dinsar.py -m /ly/slc/20201111 -s /ly/slc/20201229 -i 1 2 -d /ly/dem -o /ly/dinsar
  # three IWs
  ./s1_dinsar.py -m /ly/slc/20201111 -s /ly/slc/20201229 -i 1 2 3 -d /ly/dem -o /ly/dinsar
"""


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description="Make D-InSAR with Sentinel-1 SLCs using GAMMA.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE + '\n' + DATA_STRUCTURE)
    parser.add_argument('-m',
                        dest='m_dir',
                        help='path of master SLC directory',
                        type=str,
                        required=True)
    parser.add_argument('-s',
                        dest='s_dir',
                        help='path of slave SLC directory',
                        type=str,
                        required=True)
    parser.add_argument('-i',
                        dest='iw_num',
                        help='number of IW (1 or 2 or 3)',
                        type=int,
                        nargs='+',
                        required=True)
    parser.add_argument('-d',
                        dest='dem_dir',
                        help='path of dem directory',
                        type=str,
                        required=True)
    parser.add_argument('-o',
                        dest='output_dir',
                        help='path of output directory',
                        type=str,
                        required=True)
    parser.add_argument('--rlks',
                        help='range looks (defaults: 20)',
                        default=20,
                        type=int)
    parser.add_argument('--alks',
                        help='azimuth looks (defaults: 5)',
                        default=5,
                        type=int)
    inps = parser.parse_args()
    return inps


def get_date(slc_dir):
    """get slc date"""
    slc = glob.glob(os.path.join(slc_dir, '*.slc'))[0]
    slc_name = os.path.basename(slc)
    date = slc_name[0:8]
    return date


def run_dinsar():
    inps = cmdline_parser()
    # get parameters
    m_dir = inps.m_dir
    m_dir = os.path.abspath(m_dir)
    s_dir = inps.s_dir
    s_dir = os.path.abspath(s_dir)
    iw_num = inps.iw_num
    dem_dir = inps.dem_dir
    dem_dir = os.path.abspath(dem_dir)
    output_dir = inps.output_dir
    output_dir = os.path.abspath(output_dir)
    rlks = inps.rlks
    alks = inps.alks
    # get date
    m_date = get_date(m_dir)
    s_date = get_date(s_dir)
    # get dem
    dem = glob.glob(os.path.join(dem_dir, '*.dem'))[0]
    # prepare iw info
    iw1 = str(iw_num[0])
    iw_info = f"echo $s_dir/$s_date.iw{iw1*2}.slc $s_dir/$s_date.iw{iw1*2}.slc.par $s_dir/$s_date.iw{iw1*2}.slc.tops_par > SLC2_tab"
    iw_info += f"\necho $m_dir/$m_date.iw{iw1*2}.slc $m_dir/$m_date.iw{iw1*2}.slc.par $m_dir/$m_date.iw{iw1*2}.slc.tops_par > SLC1_tab"
    iw_info += f"\necho $s_date.iw{iw1}.rslc $s_date.iw{iw1}.rslc.par $s_date.iw{iw1}.rslc.tops_par > RSLC2_tab"
    if len(iw_num) >= 2:
        for iw in iw_num[1:]:
            iw_info += f"\necho $s_dir/$s_date.iw{iw*2}.slc $s_dir/$s_date.iw{iw*2}.slc.par $s_dir/$s_date.iw{iw*2}.slc.tops_par >> SLC2_tab"
            iw_info += f"\necho $m_dir/$m_date.iw{iw*2}.slc $m_dir/$m_date.iw{iw*2}.slc.par $m_dir/$m_date.iw{iw*2}.slc.tops_par >> SLC1_tab"
            iw_info += f"\necho $s_date.iw{iw}.rslc $s_date.iw{iw}.rslc.par $s_date.iw{iw}.rslc.tops_par >> RSLC2_tab"
    # write D-InSAR script
    script.replace('m_dir_flag', m_dir).replace('s_dir_flag', s_dir)
    script.replace('m_date_flag', m_date).replace('s_date_flag', s_date)
    script.replace('rlks_flag', rlks).replace('alks_flag', alks)
    script.replace('dem_flag', dem).replace('iw_info_flag', iw_info)
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    script_path = os.path.join(output_dir, f"{m_date}-{s_date}_DInSAR.sh")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script)
    # run D-InSAR
    os.chdir(output_dir)
    os.system(f"sh {m_date}-{s_date}_DInSAR.sh")


if __name__ == "__main__":
    run_dinsar()
