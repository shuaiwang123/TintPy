# How to run SBAS using StaMPS (GMT is required)

## 1. Select points based on coherence

1. prepare required data structure (`sbas_mli_cc.py`)
2. enter `SMALL_BASELINES` folder
3. run `mt_ml_select_gamma` in MATLAB
4. run `ps_info` to check point number (you can rerun step 3 until you are satisfied)
5. run `getparm` to get all parameters
6. you can set these parametars
`setparm('scla_deramp','y')`
`setparm('unwrap_method','3d')`
7. run `stamps(6,8)`
8. run `ps_plot('V-do')` to view velocity, `ps_plot('V-do', -1)` to save it
9. run `ps_plot('V-do', ts)` to view and save time-series displacement


## 2. Select points based on amplitude dispersion

1. prepare required data structure (`sbas_mli_ad.py`)
2. run `mt_prep_gamma` in terminal, and open MATLAB
3. run `getparm` to get all parameters, and you can set these parameters
`setparm('density_rand', 20)`
`setparm('weed_standard_dev',2)`
4. run `stamps(1,5)`
5. you can set these parametars
`setparm('scla_deramp','y')`
`setparm('unwrap_method','3d')`
6. run `stamps(6,8)`
7. run `ps_plot('V-do')` to view velocity, `ps_plot('V-do', -1)` to save it
8. run `ps_plot('V-do', ts)` to view and save time-series displacement

## 3. Tropospheric correction

### 3.1 Phase-based-Linear tropospheric correction

1. create a folder named **supermaster_date**
2. copy **supermaster_date.rslc.par** to **supermaster_date**
3. `getparm_aps`
4. `load('parms.mat')`
5. `save('parms_aps.mat', 'heading','lambda','-append')`
6. `aps_linear`
7. `setparm('subtr_tropo', 'y')`, `setparm('tropo_method', 'a_l')`
8. `stamps(7,8)`
9. `ps_plot('V-dao', 'a_linear')`, `ps_plot('V-dao', 'a_linear', 'ts')`

### 3.2 GACOS-based tropospheric correction

1. create a folder named **supermaster_date**
2. copy **supermaster_date.rslc.par** to **supermaster_date**
3. `getparm_aps`
4. `load('parms.mat')`
5. `save('parms_aps.mat', 'heading','lambda','-append')`
6. `setparm_aps('gacos_datapath', './APS')`
7. `aps_weather_model('gacos',1,3)`
8. `setparm('subtr_tropo', 'y')`, `setparm('tropo_method', 'a_gacos')`
9. `stamps(7,8)`
10. `ps_plot('V-dao', 'a_gacos')`, `ps_plot('V-dao', 'a_gacos', 'ts')`

## 4 Fix error

### 4.1 run mt_ml_select_gamma

``` matlab
Error using  >= 
Matrix dimensions must agree.
Error in mt_ml_select_gamma (line 147)
```

**change the code of `mt_ml_select_gamma.m`**

```matlab
coh=coh';
if ischar(coh_thresh)
    coh_thresh=str2double(coh_thresh);
end
ix(:,:,i1)=coh>=coh_thresh;
```

### 4.2 run stamps(1,1)

**change the code of `sb_load_initial_gamma.m` [line141]**

```matlab
xy=llh2local(lonlat',ll0)'*1000
```
