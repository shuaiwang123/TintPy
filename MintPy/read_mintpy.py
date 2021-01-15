#!/usr/bin/env python3
#############################################################
# Read velocity and time-series files processed by MintPy   #
# Copyright (c) 2021, Lei Yuan                              #
#############################################################

import os
import h5py
import argparse
import sys
import numpy as np


def read_h5(fname, label):
    with h5py.File(fname, 'r') as f:
        atr = dict(f.attrs)
        data = np.asarray(f[label])
    return data, atr


def read_vel(vel_file, mask_file, out_vel_file=None):
    vel, atr = read_h5(vel_file, 'velocity')

    lon = float(atr['X_FIRST'])
    lat = float(atr['Y_FIRST'])

    lon_step = float(atr['X_STEP'])
    lat_step = float(atr['Y_STEP'])

    lon_tmp = np.linspace(lon, lon + lon_step * vel.shape[1], vel.shape[1])
    lat_tmp = np.linspace(lat, lat + lat_step * vel.shape[0], vel.shape[0])
    lons, lats = np.meshgrid(lon_tmp, lat_tmp)

    mask, _ = read_h5(mask_file, 'mask')

    lons = lons[mask].reshape((-1, 1))
    lats = lats[mask].reshape((-1, 1))
    vel = vel[mask].reshape((-1, 1))

    num = np.arange(vel.shape[0]).reshape((-1, 1))

    vel *= 1000

    print('max velocity : ', np.max(vel))
    print('min velocity : ', np.min(vel))
    print('number of points : ', vel.shape[0])

    out_data = np.hstack((num, lons, lats, vel))
    if not out_vel_file is None:
        print('writing data to {}'.format(out_vel_file))
        np.savetxt(out_vel_file, out_data, fmt='%4f')
        print('done.')
    return out_data


def read_vel_ts(ts_file,
                vel_file,
                mask_file,
                out_vel_file=None,
                out_ts_file=None):
    mask, _ = read_h5(mask_file, 'mask')
    mask = np.asarray(mask)

    vel, _ = read_h5(vel_file, 'velocity')
    vel = np.asarray(vel) * 1000

    date, _ = read_h5(ts_file, 'date')
    date = date.astype(np.int64)
    ts, atr = read_h5(ts_file, 'timeseries')
    ts = np.asarray(ts)
    ts = ts.reshape((date.shape[0], -1, 1)) * 1000

    lon = float(atr['X_FIRST'])
    lon_step = float(atr['X_STEP'])

    lat = float(atr['Y_FIRST'])
    lat_step = float(atr['Y_STEP'])

    lon_tmp = np.linspace(lon, lon + lon_step * vel.shape[1], vel.shape[1])
    lat_tmp = np.linspace(lat, lat + lat_step * vel.shape[0], vel.shape[0])

    lons, lats = np.meshgrid(lon_tmp, lat_tmp)

    lons = lons.reshape((-1, 1))
    lats = lats.reshape((-1, 1))
    vels = vel.reshape((-1, 1))
    mask = mask.reshape((-1, 1))

    lons = lons[mask].reshape((-1, 1))
    lats = lats[mask].reshape((-1, 1))
    vels = vels[mask].reshape((-1, 1))
    num = np.arange(lons.shape[0]).reshape((-1, 1))

    print('number of points : ', lons.shape[0])
    print('max velocity : ', np.max(vels))
    print('min velocity : ', np.min(vels))
    out_vel = np.hstack((num, lons, lats, vels))
    if not out_vel_file is None:
        print('writing data to {}'.format(out_vel_file))
        np.savetxt(out_vel_file, out_vel, fmt='%4f')
        print('done.')

    out_ts = out_vel
    for i in range(ts.shape[0]):
        data = ts[i]
        out_ts = np.hstack((out_ts, data[mask].reshape((-1, 1))))

    tmp = out_ts[:, 4:]
    tmp = tmp - tmp[:, 0].reshape((-1, 1))
    tmp = np.hstack((out_vel, tmp))

    out_ts = tmp
    print('max cumulative displacement: ', np.max(out_ts[:, -1]))
    print('min cumulative displacement: ', np.min(out_ts[:, -1]))
    if not out_ts_file is None:
        print('writing data to {}'.format(out_ts_file))
        np.savetxt(out_ts_file, out_ts, fmt='%4f')
        print('done.')

    return out_ts, date


def prep_data_for_kmz(ts_data, date, out_vel_file=None, out_ts_file=None):
    first_line = np.asarray([[-1, -1, -1, -1]])
    first_line = np.hstack((first_line, date.reshape((1, -1))))
    out_ts = np.vstack((first_line, ts_data))
    out_vel = ts_data[0:, 0:4]
    if not out_vel_file is None:
        print('writing data to {}'.format(out_ts_file))
        np.savetxt(out_ts_file, out_ts, fmt='%4f')
        print('done.')
    if not out_ts_file is None:
        print('writing data to {}'.format(out_vel_file))
        np.savetxt(out_vel_file, out_vel, fmt='%4f')
        print('done.')


vel_file = 'geo_velocity.h5'
mask_file = 'geo_maskTempCoh.h5'

velocity = read_vel(vel_file, mask_file, out_vel_file=None)

ts_file = 'geo_timeseries_tropHgt_ramp_demErr.h5'
vel_file = 'geo_velocity.h5'
mask_file = 'geo_maskTempCoh.h5'

ts_data, date = read_vel_ts(ts_file,
                            vel_file,
                            mask_file,
                            out_vel_file=None,
                            out_ts_file=None)

prep_data_for_kmz(ts_data, date, out_vel_file='vel.txt', out_ts_file='ts.txt')
