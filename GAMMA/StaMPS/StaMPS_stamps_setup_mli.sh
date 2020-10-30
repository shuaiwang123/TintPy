#!/bin/bash

######################################
# Script to take multi-looked outputs from LiCSAR and prepare them for StaMPS
# Assumes small baseline IFGs are in folder IFG and single master
# IFGs in folder IFG_SM
#
# Jack McGrath
#
# 2019 Sept: Initial Commit
# 2019 Dec : Include rslc real_to_cpx
######################################


######################################
### Define Paths and Supermaster
######################################


LiCSdir='/scratch/eejdm/023A/LiCSAR'
supermaster=20161225
stampsdir=`pwd`/INSAR_${supermaster}_SB
psdir=`pwd`/INSAR_${supermaster}_PS

mkdir $stampsdir
mkdir $psdir

rlks=`cat $LiCSdir/SLC/$supermaster/${supermaster}.slc.mli.par | grep range_looks: | rev | awk '{print substr ($1,1,2)}'| rev`
alks=`cat $LiCSdir/SLC/$supermaster/${supermaster}.slc.mli.par | grep azimuth_looks: | rev | awk '{print substr ($1,1,2)}'| rev`

width=`cat $LiCSdir/SLC/$supermaster/$supermaster.slc.mli.par | grep range_samples: | awk '{print $2}'`
length=`cat $LiCSdir/SLC/$supermaster/$supermaster.slc.mli.par | grep azimuth_lines: | awk '{print $2}'`


######################################
### Create complex rslc directory
######################################

cd $LiCSdir

mkdir RSLC_cpx

echo 'Converting multilooked images'

for day in $(ls $LiCSdir/RSLC/); do
	cp $LiCSdir/RSLC/$day/$day.rslc.mli $LiCSdir/RSLC_cpx/$day.rslc.mli
	real_to_cpx $LiCSdir/RSLC_cpx/$day.flt.rslc - $LiCSdir/RSLC_cpx/$day.rslc $width 0
	rm $LiCSdir/RSLC_cpx/$day.rslc.mli
done

echo 'Multilooked RSLC converted from real to complex'


######################################
### SMALL BASELINES
######################################

echo 'Preparing Small Baselines'

cd $stampsdir

mkdir rslc diff0 geo SMALL_BASELINES

ls $LiCSdir/IFG | grep _ | awk '{print substr($1,1,8)}' >dates.txt
ls $LiCSdir/IFG | grep _ > ifg.txt

nfiles=$(cat dates.txt | wc -l)
echo $nfiles

n=1


echo 'Copying DEM'

cp $LiCSdir/geo/$supermaster.hgt $stampsdir/geo/$supermaster\_dem.rdc
cp $LiCSdir/geo/EQA.dem_par $stampsdir/geo/EQA.dem_par


echo 'Making SMALL_BASELINES/IFG folders'

for ifg in $(ls $LiCSdir/IFG/| grep _2); do mkdir $stampsdir/SMALL_BASELINES/$ifg ; done

while [ $n -le $nfiles ]
do
	master=`awk '(NR=='$n'){print $1}' dates.txt`
	slave=`awk '(NR=='$n'){print substr ($1,10,17)}' ifg.txt`	
	ifg=`awk '(NR=='$n'){print $1}' ifg.txt`
	echo " "
	echo "##### "
	echo $master $slave $ifg
	echo "##### "
	echo " "

	cp $LiCSdir/RSLC_cpx/$master/$master.rslc $stampsdir/SMALL_BASELINES/$ifg/$master.rslc
	cp $LiCSdir/RSLC_cpx/$slave/$slave.rslc $stampsdir/SMALL_BASELINES/$ifg/$slave.rslc	
	cp $LiCSdir/RSLC/$supermaster/$supermaster.rslc.mli.par $stampsdir/SMALL_BASELINES/$ifg/$supermaster.rslc.par

	cp $LiCSdir/IFG/$ifg/$ifg.diff $stampsdir/SMALL_BASELINES/$ifg/

	create_offset $LiCSdir/RSLC/$master/$master.rslc.mli.par $LiCSdir/RSLC/$slave/$slave.rslc.mli.par $stampsdir/SMALL_BASELINES/$ifg/$master\_$slave.off 1 $rlks $alks 0
	base_init $LiCSdir/RSLC/$slave/$slave.rslc.mli.par $LiCSdir/RSLC/$master/$master.rslc.par $stampsdir/SMALL_BASELINES/$ifg/$ifg.off - $stampsdir/SMALL_BASELINES/$ifg/$master\_$slave.base
	n=$(expr $n + 1) 

	sed -i "s/FLOAT/FCOMPLEX/g" "$stampsdir/SMALL_BASELINES/$ifg/$supermaster.rslc.par"

done

echo 'Copying complex RSLC'

for rslc in $(ls $LiCSdir/RSLC); do 
	cp $LiCSdir/RSLC_cpx/$rslc.rslc $stampsdir/rslc/
done

cp $stampsdir/SMALL_BASELINES/$ifg/$supermaster.rslc.par $stampsdir/rslc/$supermaster.slc.par

echo 'Copying diffs and making offsets'

for ifg in $(ls $LiCSdir/IFG_SM/ | grep $supermaster); 
	do 
		slave=`echo $ifg | awk '{print substr ($1,10,17)}'`
		echo $slave
		cp $LiCSdir/IFG_SM/$ifg/$ifg.diff $stampsdir/diff0/$slave.diff
		create_offset $LiCSdir/RSLC/$supermaster/$supermaster.rslc.mli.par $LiCSdir/RSLC/$slave/$slave.rslc.mli.par $stampsdir/diff0/$supermaster\_$slave.off 1 $rlks $alks 0
		base_init $LiCSdir/RSLC/$slave/$slave.rslc.mli.par $LiCSdir/RSLC/$supermaster/$supermaster.rslc.mli.par $stampsdir/diff0/$ifg.off - $stampsdir/diff0/$slave.base
		
	done

echo 'Creating .lon and .lat files'

cd $LiCSdir

~/scripts/insar/StaMPS/LiCSAR2StaMPS_step_gamma_geo.sh $LiCSdir/geo/EQA.dem_par $LiCSdir/geo/$supermaster.lt_fine $width $length

cd $stampsdir

cp $LiCSdir/geo/$supermaster.lon ./geo/
cp $LiCSdir/geo/$supermaster.lat ./geo/

echo 'Small Baselines ready'

######################################
### PERMENANT SCATTERS
######################################

echo 'Preparing Permenant Scatter folder'


echo 'Small Baselines Complete'
echo " "
echo 'Copying to PS directory'

cp -rf $stampsdir/geo $psdir/
cp -rf $stampsdir/rslc $psdir/
cp -rf $stampsdir/diff0 $psdir/

echo " "
echo 'PS Complete'

cd $psdir

source /nfs/see-fs-02_users/eejdm/StaMPS-4.1-beta/StaMPS_CONFIG.bash

echo "mt_prep_gamma $supermaster $psdir 0.4 10 10 50 50"
mt_prep_gamma $supermaster $psdir 0.4 10 10 50 50

cd $stampsdir
echo "mt_prep_gamma $supermaster $stampsdir 0.6 10 10 50 50"
mt_prep_gamma $supermaster $stampsdir 0.6 10 10 50 50

