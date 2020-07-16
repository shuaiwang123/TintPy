#!/usr/bin/env python3
#####################################################
# Stack processing using GAMMA for MintPy           #
# Copyright (c) 2020, Lei Yuan                      #
#####################################################

import os
import re
import sys
import glob
import datetime
import argparse
import shutil

dinsar_script = """Mpath=$slc_dir/$Mdate/
Spath=$slc_dir/$Sdate/
Mslc=${Mpath}${Mdate}.slc
Mpar=${Mpath}${Mdate}.slc.par
Sslc=${Spath}${Sdate}.slc
Spar=${Spath}${Sdate}.slc.par


#####################################################
## 1. Refinement of geocoding lookup table         ##
#####################################################

# echo ${Mpath}${Mdate}.iw11.slc ${Mpath}${Mdate}.iw11.slc.par ${Mpath}${Mdate}.iw11.slc.tops_par > SLC1_tab
# echo ${Spath}${Sdate}.iw11.slc ${Spath}${Sdate}.iw11.slc.par ${Spath}${Sdate}.iw11.slc.tops_par > SLC2_tab

# SLC_mosaic_S1_TOPS SLC1_tab $Mslc $Mpar $rlks $alks
# SLC_mosaic_S1_TOPS SLC2_tab $Sslc $Spar $rlks $alks

# Calculate a multi-look intensity (MLI) image from an SLC image
multi_look $Mslc $Mpar $Mdate\_${rlks}rlks.amp $Mdate\_${rlks}rlks.amp.par $rlks $alks
multi_look $Sslc $Spar $Sdate\_${rlks}rlks.amp $Sdate\_${rlks}rlks.amp.par $rlks $alks

# Calculate SLC/MLI image corners in geodetic latitude and longitude (deg.)
# SLC_corners $Mdate\_${rlks}rlks.amp.par > $Mdate\_${rlks}rlks.amp.corner_full
# SLC_corners $Sdate\_${rlks}rlks.amp.par > $Sdate\_${rlks}rlks.amp.corner_full
# awk 'NR>2&&NR<7 {print $3,$6}' $Mdate\_${rlks}rlks.amp.corner_full > $Mdate\_${rlks}rlks.amp.corner
# awk 'NR>2&&NR<7 {print $3,$6}' $Sdate\_${rlks}rlks.amp.corner_full > $Sdate\_${rlks}rlks.amp.corner

width_amp=`awk '$1=="range_samples:" {print $2}' $Mdate\_${rlks}rlks.amp.par`
length_amp=`awk '$1=="azimuth_lines:" {print $2}' $Mdate\_${rlks}rlks.amp.par`

# Calculate lookup table and DEM related products for terrain-corrected geocoding
gc_map $Mdate\_${rlks}rlks.amp.par - $dem_par $dem $Mdate\_${rlks}rlks.utm.dem.par $Mdate\_${rlks}rlks.utm.dem $Mdate\_${rlks}rlks.utm_to_rdc0 1 1 $Mdate.sim_sar u v inc psi pix ls_map 8 1
width_utm_dem=`awk '$1=="width:" {print $2}' $Mdate\_${rlks}rlks.utm.dem.par`
# Calculate terrain-based sigma0 and gammma0 normalization area in slant-range geometry
pixel_area $Mdate\_${rlks}rlks.amp.par $Mdate\_${rlks}rlks.utm.dem.par $Mdate\_${rlks}rlks.utm.dem $Mdate\_${rlks}rlks.utm_to_rdc0 ls_map inc pix_sigma0 pix_gamma0
raspwr pix_gamma0 $width_amp - - - - - - - pix_gamm0.bmp

# Create DIFF/GEO parameter file for geocoding and differential interferometry
create_diff_par $Mdate\_${rlks}rlks.amp.par - $Mdate\_${rlks}rlks.diff_par 1 0
# Offset tracking between SLC images using intensity cross-correlation
offset_pwrm pix_sigma0 $Mdate\_${rlks}rlks.amp $Mdate\_${rlks}rlks.diff_par $Mdate.offs $Mdate.snr 256 256 offsets 2 64 32 5.0
# Range and azimuth offset polynomial estimation using SVD
offset_fitm $Mdate.offs $Mdate.snr $Mdate\_${rlks}rlks.diff_par coffs coffsets 5.0 1
# Geocoding lookup table refinement using DIFF_par offset polynomials
gc_map_fine $Mdate\_${rlks}rlks.utm_to_rdc0 $width_utm_dem $Mdate\_${rlks}rlks.diff_par $Mdate\_${rlks}rlks.UTM_TO_RDC 1

# Geocoding of image data using lookup table values
geocode_back $Mdate\_${rlks}rlks.amp $width_amp $Mdate\_${rlks}rlks.UTM_TO_RDC geo_$Mdate\_${rlks}rlks.amp $width_utm_dem - 2 0
raspwr geo_$Mdate\_${rlks}rlks.amp $width_utm_dem 1 0 1 1 1. .35 1 geo_$Mdate\_${rlks}rlks.amp.bmp

# Forward geocoding transformation using a lookup table
geocode $Mdate\_${rlks}rlks.UTM_TO_RDC $Mdate\_${rlks}rlks.utm.dem $width_utm_dem $Mdate\_${rlks}rlks.rdc.dem $width_amp $length_amp 1 0 
rashgt $Mdate\_${rlks}rlks.rdc.dem $Mdate\_${rlks}rlks.amp $width_amp 1 1 0 1 1 160.0 1. .35 1 $Mdate\_${rlks}rlks.rdc.dem.bmp

###############################################################
## 2. S1 tops co-registration                                ##
## need iw*.slc iw*.slc.par iw*.slc.tops_par                 ##
###############################################################

# Derive lookup table for SLC/MLI coregistration (considering terrain heights)
rdc_trans $Mdate\_${rlks}rlks.amp.par $Mdate\_${rlks}rlks.rdc.dem $Sdate\_${rlks}rlks.amp.par $Sdate.lt

echo ${Spath}${Sdate}.iw11.slc ${Spath}${Sdate}.iw11.slc.par ${Spath}${Sdate}.iw11.slc.tops_par > SLC2_tab
echo ${Mpath}${Mdate}.iw11.slc ${Mpath}${Mdate}.iw11.slc.par ${Mpath}${Mdate}.iw11.slc.tops_par > SLC1_tab
echo ${Spath}${Sdate}.iw11.rslc ${Spath}${Sdate}.iw11.rslc.par ${Spath}${Sdate}.iw11.rslc.tops_par > RSLC2_tab

# Resample tops (IW mode) SLC using a lookup table and SLC offset polynomials for refinement
SLC_interp_lt_S1_TOPS SLC2_tab $Spar SLC1_tab $Mpar $Sdate.lt $Mdate\_${rlks}rlks.amp.par $Sdate\_${rlks}rlks.amp.par - RSLC2_tab $Sdate.rslc $Sdate.rslc.par

#########################################################
## 2.1 1st iterative process to refine coregistration
#########################################################

# determine now the residual offset between the master SLC mosaic 
# and the slave SLC mosaic using the RSLC cross-correlation method
create_offset $Mpar $Spar $Mdate\_$Sdate.off 1 $rlks $alks 0
offset_pwr $Mslc $Sdate.rslc $Mpar $Sdate.rslc.par $Mdate\_$Sdate.off $Mdate\_$Sdate.offs $Mdate\_$Sdate.snr 64 32 - 4 128 128 7.0 4 0 0
offset_fit $Mdate\_$Sdate.offs $Mdate\_$Sdate.snr $Mdate\_$Sdate.off - - 7.0 4 0

# resample again indicating the .off
SLC_interp_lt_S1_TOPS SLC2_tab $Spar SLC1_tab $Mpar $Sdate.lt $Mdate\_${rlks}rlks.amp.par $Sdate\_${rlks}rlks.amp.par $Mdate\_$Sdate.off RSLC2_tab $Sdate.rslc $Sdate.rslc.par

create_offset $Mpar $Spar $Mdate\_$Sdate.off1 1 $rlks $alks 0
offset_pwr $Mslc $Sdate.rslc $Mpar $Sdate.rslc.par $Mdate\_$Sdate.off1 $Mdate\_$Sdate.offs1 $Mdate\_$Sdate.snr1 64 64 $Mdate\_$Sdate.coreg 4 200 200 7.0 4 0 0
offset_fit $Mdate\_$Sdate.offs1 $Mdate\_$Sdate.snr1 $Mdate\_$Sdate.off1 - - 7.0 4 0

# update the offset parameter file to include the total offset estimated
offset_add $Mdate\_$Sdate.off $Mdate\_$Sdate.off1 $Mdate\_$Sdate.off.total

SLC_interp_lt_S1_TOPS SLC2_tab $Spar SLC1_tab $Mpar $Sdate.lt $Mdate\_${rlks}rlks.amp.par $Sdate\_${rlks}rlks.amp.par $Mdate\_$Sdate.off.total RSLC2_tab $Sdate.rslc $Sdate.rslc.par
# Simulate unwrapped interferometric phase using DEM height and deformation rate using orbit state vectors
phase_sim_orb $Mpar $Spar $Mdate\_$Sdate.off.total $Mdate\_${rlks}rlks.rdc.dem $Mdate\_$Sdate.sim_unw0 $Mpar - - 1 1
# Differential interferogram generation from co-registered SLCs and a simulated interferogram
SLC_diff_intf $Mslc $Sdate.rslc $Mpar $Sdate.rslc.par $Mdate\_$Sdate.off.total $Mdate\_$Sdate.sim_unw0 $Mdate\_$Sdate.diff0 $rlks $alks 0 0 0.25 1 1

rasmph $Mdate\_$Sdate.diff0 $width_amp 1 0 1 1 1. .35 1 $Mdate\_$Sdate.diff0.bmp

###########################################################################################################
## 2.2 2nd iteration: Determine a refinement of the azimuth offset estimation using 
## a spectral diversity method that considers the double difference phase in the burst overlap regions
###########################################################################################################

# estimates an azimuth offset correction based on the phase difference between the two interferograms 
# that can be calculated for the overlap region between subsequent bursts
S1_coreg_overlap SLC1_tab RSLC2_tab $Mdate\_$Sdate $Mdate\_$Sdate.off.total $Mdate\_$Sdate\_${rlks}rlks.off 0.8 100

SLC_interp_lt_S1_TOPS SLC2_tab $Spar SLC1_tab $Mpar $Sdate.lt $Mdate\_${rlks}rlks.amp.par $Sdate\_${rlks}rlks.amp.par $Mdate\_$Sdate\_${rlks}rlks.off RSLC2_tab $Sdate.rslc $Sdate.rslc.par

####################################################
## 2. Differential interferogram generation       ##
####################################################

phase_sim_orb $Mpar $Spar $Mdate\_$Sdate\_${rlks}rlks.off $Mdate\_${rlks}rlks.rdc.dem $Mdate\_$Sdate.sim_unw $Mpar - - 1 1

SLC_diff_intf $Mslc $Sdate.rslc $Mpar $Sdate.rslc.par $Mdate\_$Sdate\_${rlks}rlks.off $Mdate\_$Sdate.sim_unw $Mdate\_$Sdate\_${rlks}rlks.diff $rlks $alks 0 0 0.25 1 1

rasmph $Mdate\_$Sdate\_${rlks}rlks.diff $width_amp 1 0 1 1 1. .35 1 $Mdate\_$Sdate\_${rlks}rlks.diff.bmp 
# Estimate initial baseline using orbit state vectors, offsets, and interferogram phase
base_init $Mpar $Spar $Mdate\_$Sdate\_${rlks}rlks.off $Mdate\_$Sdate\_${rlks}rlks.diff $Mdate\_$Sdate\_${rlks}rlks.baseline 0 1024 1024
# Calculate baseline components perpendicular and parallel to look vector
base_perp $Mdate\_$Sdate\_${rlks}rlks.baseline $Mpar $Mdate\_$Sdate\_${rlks}rlks.off > $Mdate\_$Sdate\_${rlks}rlks.base_perp
# Refine the azimuth offset  
# S1_coreg_overlap SLC1_tab RSLC2_tab $Mdate\_$Sdate $Mdate\_$Sdate\_${rlks}rlks.off $Mdate\_$Sdate\_${rlks}rlks.off2 0.8 100
# SLC_interp_lt_S1_tops SLC2_tab $Spar SLC1_tab $Mpar $Sdate.lt $Mdate\_${rlks}rlks.amp.par $Sdate\_${rlks}rlks.amp.par $Mdate\_$Sdate\_${rlks}rlks.off2 RSLC2_tab $Sdate.rslc $Sdate.rslc.par

width=$(awk '$1=="interferogram_width:" {print $2}' $Mdate\_$Sdate\_${rlks}rlks.off)
length=$(awk '$1=="interferogram_azimuth_lines:" {print $2}' $Mdate\_$Sdate\_${rlks}rlks.off)

###############################################
## 3. Filter Differential Interferogram      ##
###############################################

# Adaptive spectral filtering for complex interferograms
adf $Mdate\_$Sdate\_${rlks}rlks.diff $Mdate\_$Sdate.diff.sm1 $Mdate\_$Sdate.diff.sm1.cc $width 0.3 32 5
adf $Mdate\_$Sdate.diff.sm1 $Mdate\_$Sdate.diff.sm2 $Mdate\_$Sdate.diff.sm2.cc $width 0.3 32 5
adf $Mdate\_$Sdate.diff.sm2 $Mdate\_$Sdate\_${rlks}rlks.diff_filt $Mdate\_$Sdate\_${rlks}rlks.diff_filt.cor $width 0.3 32 5  
# Estimate interferometric coherence
cc_wave $Mdate\_$Sdate\_${rlks}rlks.diff $Mpar $Sdate.rslc.par $Mdate\_$Sdate\_${rlks}rlks.diff.cor $width - - 3 
rascc $Mdate\_$Sdate\_${rlks}rlks.diff.cor - $width 1 1 0 1 1 .1 .9 1. .35 1 $Mdate\_$Sdate\_${rlks}rlks.diff.cor.bmp
rascc $Mdate\_$Sdate\_${rlks}rlks.diff_filt.cor - $width 1 1 0 1 1 .1 .9 1. .35 1 $Mdate\_$Sdate\_${rlks}rlks.diff_filt.cor.bmp
rasmph $Mdate\_$Sdate\_${rlks}rlks.diff_filt $width_amp 1 0 1 1 1. .35 1 $Mdate\_$Sdate\_${rlks}rlks.diff_filt.bmp

########################################################
## 4. Unwrap Differential Flattened Interferogram     ##
########################################################

# Generate phase unwrapping validity mask using correlation and intensity
rascc_mask $Mdate\_$Sdate\_${rlks}rlks.diff_filt.cor $Mdate\_${rlks}rlks.amp $width 1 1 0 1 1 .05 .1 .9 1. .35 1 $Mdate\_$Sdate\_${rlks}rlks.diff_filt.cor_mask.bmp
# Phase unwrapping using Minimum Cost Flow (MCF) and triangulation
mcf $Mdate\_$Sdate\_${rlks}rlks.diff_filt $Mdate\_$Sdate\_${rlks}rlks.diff_filt.cor $Mdate\_$Sdate\_${rlks}rlks.diff_filt.cor_mask.bmp $Mdate\_$Sdate\_${rlks}rlks.diff_filt.unw $width 1 0 0 - - 1 1 - - - 0

##################################################
# 5. geocode                                    ##
##################################################

# Geocoding of image data using lookup table values
# geocode_back $Mdate\_$Sdate\_${rlks}rlks.diff_filt.cor $width $Mdate\_${rlks}rlks.UTM_TO_RDC geo\_$Mdate\_$Sdate\_${rlks}rlks.diff_filt.cor $width_utm_dem - 2 0
# geocode_back $Mdate\_$Sdate\_${rlks}rlks.diff.cor $width $Mdate\_${rlks}rlks.UTM_TO_RDC geo\_$Mdate\_$Sdate\_${rlks}rlks.diff.cor $width_utm_dem - 2 0
# geocode_back $Mdate\_$Sdate\_${rlks}rlks.diff_filt $width $Mdate\_${rlks}rlks.UTM_TO_RDC geo\_$Mdate\_$Sdate\_${rlks}rlks.diff_filt $width_utm_dem - 2 0
# geocode_back $Mdate\_$Sdate\_${rlks}rlks.diff_filt.unw $width $Mdate\_${rlks}rlks.UTM_TO_RDC geo\_$Mdate\_$Sdate\_${rlks}rlks.diff_filt.unw $width_utm_dem - 1 0
# geocode_back $Mdate\_${rlks}rlks.amp $width $Mdate\_${rlks}rlks.UTM_TO_RDC geo\_$Mdate\_$Sdate\_${rlks}rlks.pwr $width_utm_dem - 2 0

# rascc geo\_$Mdate\_$Sdate\_${rlks}rlks.diff.cor - $width_utm_dem 1 1 0 1 1 .1 .9 1. .35 1 geo\_$Mdate\_$Sdate\_${rlks}rlks.diff.cor.bmp
# rascc geo\_$Mdate\_$Sdate\_${rlks}rlks.diff_filt.cor - $width_utm_dem 1 1 0 1 1 .1 .9 1. .35 1 geo\_$Mdate\_$Sdate\_${rlks}rlks.diff_filt.cor.bmp
# rascc geo\_$Mdate\_$Sdate\_${rlks}rlks.diff_filt.unw - $width_utm_dem 1 1 0 1 1 .1 .9 1. .35 1 geo\_$Mdate\_$Sdate\_${rlks}rlks.diff_filt.unw.bmp
# rasmph_pwr geo\_$Mdate\_$Sdate\_${rlks}rlks.diff_filt geo\_$Mdate\_$Sdate\_${rlks}rlks.pwr $width_utm_dem 1 1 0 1 1 1. 0.35 1 geo\_$Mdate\_$Sdate\_${rlks}rlks.diff_filtandpwr.bmp
# rasmph_pwr $Mdate\_$Sdate\_${rlks}rlks.diff_filt.unw geo\_$Mdate\_$Sdate\_${rlks}rlks.pwr $width_utm_dem 1 1 0 1 1 1. 0.35 1 $Mdate\_$Sdate\_${rlks}rlks.diff_filt.unwandpwr.bmp
# rasrmg $Mdate\_$Sdate\_${rlks}rlks.diff_filt.unw $Mdate\_${rlks}rlks.amp $width 1 1 0 1 1 .2 1. .35 .0 1 $Mdate\_$Sdate\_${rlks}rlks.diff_filt.unw.bmp $Mdate\_$Sdate\_${rlks}rlks.diff_filt.cor 1 .2
"""


def cmd_line_parser():
    parser = argparse.ArgumentParser(description='Stack processing of Sentinel-1 slc.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('slc_dir', help='directory path of slc')
    parser.add_argument('stacking_dir', help='directory path of stacking')
    parser.add_argument('dem_dir', help='directory path of dem and dem.par')
    parser.add_argument(
        'num_connections',
        help='number of interferograms between each date and subsequent dates',
        type=int)
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
   Stack processing of Sentinel-1 slc.
'''

EXAMPLE = """Usage:
  
  ./stacking_multi_bursts_old.py /ly/slc /ly/stacking /ly/dem 4
  ./stacking_multi_bursts_old.py /ly/slc /ly/stacking /ly/dem 4 --rlks 8 --alks 8
  
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

    if not os.path.isdir(stacking_dir):
        os.mkdir(stacking_dir)

    # get all date
    tmp_files = os.listdir(slc_dir)
    slc_date = [i for i in tmp_files if re.match(r'\d{8}', i)]

    # generate ifg_pair
    ifg_pairs = gen_ifg_pairs(slc_date, num_connections)

    for i in ifg_pairs:
        # make ifg_pair dir
        path = os.path.join(stacking_dir, i)
        if not os.path.isdir(path):
            os.mkdir(path)

        # write dinsar script
        m_date = i.split('-')[0]
        s_date = i.split('-')[1]
        str_m_date = f"Mdate={m_date}\n"
        str_s_date = f"Sdate={s_date}\n"
        str_slc_dir = f"slc_dir={slc_dir}\n"
        str_dem = f"dem={dem}\n"
        str_dem_par = f"dem_par={dem_par}\n"
        str_rlks = f"rlks={rlks}\n"
        str_alks = f"alks={alks}\n"

        out_script = '#!/bin/sh\n\n' + str_m_date + str_s_date + str_slc_dir + str_dem + str_dem_par + str_rlks + str_alks + dinsar_script
        out_script_path = os.path.join(path, i + '_DInSAR.sh')
        with open(out_script_path, 'w+') as f:
            f.write(out_script)

        # run dinsar script
        os.chdir(path)
        call_str = 'sh ' + i + '_DinSAR.sh'
        os.system(call_str)


if __name__ == "__main__":
    main()
