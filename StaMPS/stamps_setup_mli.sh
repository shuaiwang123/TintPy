#!/bin/bash

######################################
### Define Paths and Supermaster
######################################


LiCSdir='/media/ly/3TB/hanyuan-stacking/stamps-test'
supermaster=20181223
stampsdir=/media/ly/3TB/hanyuan-stacking/stamps-test/INSAR_${supermaster}_SB


mkdir $stampsdir


rlks=`cat $LiCSdir/rslc/$supermaster/${supermaster}.slc.mli.par | grep range_looks: | rev | awk '{print substr ($1,1,2)}'| rev`
alks=`cat $LiCSdir/rslc/$supermaster/${supermaster}.slc.mli.par | grep azimuth_looks: | rev | awk '{print substr ($1,1,2)}'| rev`

width=`cat $LiCSdir/rslc/$supermaster/$supermaster.slc.mli.par | grep range_samples: | awk '{print $2}'`
length=`cat $LiCSdir/rslc/$supermaster/$supermaster.slc.mli.par | grep azimuth_lines: | awk '{print $2}'`


######################################
### Create complex rslc directory
######################################

cd $LiCSdir

mkdir rslc_cpx

echo 'Converting multilooked images'

for day in $(ls $LiCSdir/rslc/); do
	cp $LiCSdir/rslc/$day/$day.slc.mli $LiCSdir/rslc_cpx/$day.slc.mli
	real_to_cpx $LiCSdir/rslc_cpx/$day.slc.mli - $LiCSdir/rslc_cpx/$day.slc $width 0
	rm $LiCSdir/rslc_cpx/$day.slc.mli
done

echo 'Multilooked RSLC converted from real to complex'


######################################
### SMALL BASELINES
######################################

echo 'Preparing Small Baselines'

cd $stampsdir

mkdir rslc geo SMALL_BASELINES

ls $LiCSdir/IFG | grep _ | awk '{print substr($1,1,8)}' > dates.txt
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

	cp $LiCSdir/rslc_cpx/$master.slc $stampsdir/SMALL_BASELINES/$ifg/$master.rslc
	cp $LiCSdir/rslc_cpx/$slave.slc $stampsdir/SMALL_BASELINES/$ifg/$slave.rslc	
	cp $LiCSdir/rslc/$supermaster/$supermaster.slc.mli.par $stampsdir/SMALL_BASELINES/$ifg/$supermaster.rslc.par

	cp $LiCSdir/IFG/$ifg/$master-$slave.diff.int $stampsdir/SMALL_BASELINES/$ifg/$master-$slave.diff

	create_offset $LiCSdir/rslc/$master/$master.slc.mli.par $LiCSdir/rslc/$slave/$slave.slc.mli.par $stampsdir/SMALL_BASELINES/$ifg/$master-$slave.off 1 $rlks $alks 0
	base_init $LiCSdir/rslc/$slave/$slave.slc.mli.par $LiCSdir/rslc/$master/$master.slc.par $stampsdir/SMALL_BASELINES/$ifg/$ifg.off - $stampsdir/SMALL_BASELINES/$ifg/$master-$slave.base
	n=$(expr $n + 1) 

	sed -i "s/FLOAT/FCOMPLEX/g" "$stampsdir/SMALL_BASELINES/$ifg/$supermaster.rslc.par"

done

echo 'Copying complex rslc'

for rslc in $(ls $LiCSdir/rslc); do 
	cp $LiCSdir/rslc_cpx/$rslc.slc $stampsdir/rslc/
done

cp $stampsdir/SMALL_BASELINES/$ifg/$supermaster.rslc.par $stampsdir/rslc/$supermaster.slc.par

echo 'Creating .lon and .lat files'

cd $LiCSdir

sh StaMPS_LiCSAR2StaMPS_step_gamma_geo.sh $LiCSdir/geo/EQA.dem_par $LiCSdir/geo/$supermaster.lt_fine $width $length

cd $stampsdir

cp $LiCSdir/geo/$supermaster.lon ./geo/
cp $LiCSdir/geo/$supermaster.lat ./geo/

echo 'Small Baselines ready'

cd $stampsdir
echo "mt_prep_gamma $supermaster $stampsdir 0.6 10 10 50 50"
mt_prep_gamma $supermaster $stampsdir 0.6 2 2 50 50