#!/usr/bin/env python
# coding: utf-8

# # Read results processed by MintPy

# ## all functions

# In[ ]:


import os
import h5py
import random
import numpy as np
import matplotlib.pyplot as plt
from xml.dom.minidom import parse
import zipfile
get_ipython().run_line_magic('matplotlib', 'inline')


def read_h5(fname, label):
    with h5py.File(fname, 'r') as f:
        atr = dict(f.attrs)
        data = np.asarray(f[(label)])
    return data, atr


def random_downsample_vel(data, min_vel, max_vel, rate, out_ds_file=None):
    if min_vel > max_vel:
        tmp = min_vel
        min_vel = max_vel
        max_vel = tmp

    less_min = data[:, 3] <= min_vel
    data_less_min = data[less_min, :]
    print(f"number of velocity <= {min_vel} : {data_less_min.shape[0]}")

    more_max = data[:, 3] >= max_vel
    data_more_max = data[more_max, :]
    print(f"number of velocity >= {max_vel} : {data_more_max.shape[0]}")

    min_max = (less_min == more_max)
    data_min_max = data[min_max, :]
    print(
        f"number of velocity in ({min_vel}, {max_vel}) : {data_min_max.shape[0]}"
    )

    index = random.sample(range(data_min_max.shape[0]),
                          int(data_min_max.shape[0] * rate))
    sampled_data = data_min_max[index, :]

    out_data = np.vstack((data_less_min, data_more_max, sampled_data))
    print('max velocity : ', np.max(out_data[:, 3]))
    print('min velocity : ', np.min(out_data[:, 3]))
    print('number of points : ', out_data.shape[0])
    if not out_ds_file is None:
        print('writing data to {}'.format(out_ds_file))
        np.savetxt(out_ds_file, out_data, fmt='%4f')
        print('done.')
    return out_data


def random_downsample_disp(data, min_disp, max_disp, rate, out_ds_file=None):
    if min_disp > max_disp:
        tmp = min_disp
        min_disp = max_disp
        max_disp = tmp

    less_min = data[:, -1] <= min_disp
    data_less_min = data[less_min, :]
    print(
        f"number of cumulative displacement <= {min_disp} : {data_less_min.shape[0]}"
    )

    more_max = data[:, -1] >= max_disp
    data_more_max = data[more_max, :]
    print(
        f"number of cumulative displacement >= {max_disp} : {data_more_max.shape[0]}"
    )

    min_max = (less_min == more_max)
    data_min_max = data[min_max, :]
    print(
        f"number of cumulative displacement in ({min_disp}, {max_disp}) : {data_min_max.shape[0]}"
    )

    index = random.sample(range(data_min_max.shape[0]),
                          int(data_min_max.shape[0] * rate))
    sampled_data = data_min_max[index, :]

    out_data = np.vstack((data_less_min, data_more_max, sampled_data))
    print('max cumulative displacement : ', np.max(out_data[:, -1]))
    print('min cumulative displacement : ', np.min(out_data[:, -1]))
    print('number of points : ', out_data.shape[0])
    if not out_ds_file is None:
        print('writing data to {}'.format(out_ds_file))
        np.savetxt(out_ds_file, out_data, fmt='%4f')
        print('done.')
    return out_data


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


def date2str(date):
    date_str = [str(i) for i in date]
    return date_str


def plot_displacement(num_list,
                      ts_data,
                      date,
                      aspect=0.2,
                      figsize=(15, 7),
                      y_lim=[-100, 100],
                      fig_name=None):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_title('time series displacement', fontsize=40, pad=20)
    ax.set_xlabel('date', fontsize=30, labelpad=10)
    ax.set_ylabel('displacrment (mm)', fontsize=30, labelpad=10)

    ax.set_ylim(y_lim[0], y_lim[1])
    ax.set_aspect(aspect)
    ax.minorticks_on()
    ax.xaxis.grid(True, which='major')
    ax.xaxis.set_tick_params(rotation=30, labelsize=15)
    ax.yaxis.grid(True, which='major')
    ax.yaxis.set_tick_params(rotation=0, labelsize=15)
    ax.set_xmargin(0.02)

    date = date2str(date)

    for num in num_list:
        disp = ts_data[num, 4:]
        ax.plot(date, disp, label=str(num), marker='o')
        ax.xaxis.set_ticks(date[::4])
        ax.yaxis.set_ticks(list(range(y_lim[0], y_lim[1] + 10, 10)))
    ax.legend(loc='best', fontsize=20, ncol=2)
    fig.show()
    if not fig_name is None:
        fig.savefig(fig_name, dpi=200)


def intersect(point, s_point, e_point):
    if s_point[1] == e_point[
            1]:  # parallel and coincident with the ray，s_point coincides with s_point
        return False
    if s_point[1] > point[1] and e_point[1] > point[
            1]:  # line segment is above the ray
        return False
    if s_point[1] < point[1] and e_point[1] < point[
            1]:  # line segment under the ray
        return False
    if s_point[1] == point[
            1] and e_point[1] > point[1]:  # point coincides with s_point
        return False
    if e_point[1] == point[
            1] and s_point[1] > point[1]:  # point coincides with e_point
        return False
    # line segment is to the left of the ray
    if s_point[0] < point[0] and e_point[0] < point[0]:
        return False

    xseg = e_point[0]-(e_point[0]-s_point[0])*(e_point[1]-point[1]) /         (e_point[1]-s_point[1])  # find the intersection
    if xseg < point[0]:  # intersection is to the left of point
        return False
    return True


def inpolygon(point, polygon):
    num = 0  # number of intersection
    for i in range(len(polygon) - 1):
        if intersect(point, polygon[i], polygon[i + 1]):
            num += 1
    return True if num % 2 == 1 else False


# ------------------------------ old functions ------------------------------
# def kml2polygon(kml_file, polygon_file):
#     cmd_str = f"gmt kml2gmt {kml_file} | awk 'NR>1' > {polygon_file}"
#     print(cmd_str)
#     os.system(cmd_str)
#     print("done.")

# def cut_vel(polygon_file, vel_file, out_vel_file):
#     polygon = np.loadtxt(polygon_file)
#     vel = np.loadtxt(vel_file)
#     out_data = np.arange(vel.shape[1])
#     for line in vel:
#         if inpolygon(line[1:3], polygon):
#             out_data = np.vstack((out_data, line))
#     np.savetxt(out_vel_file, out_data[1:, :], fmt='%4f')
#     print('done.')

# def cut_ts(polygon_file, ts_file, out_ts_file):
#     polygon = np.loadtxt(polygon_file)
#     data = np.loadtxt(ts_file)
#     ts = data[1:, :]
#     out_data = data[0, :]
#     for line in ts:
#         if inpolygon(line[1:3], polygon):
#             out_data = np.vstack((out_data, line))
#     np.savetxt(out_ts_file, out_data, fmt='%4f')
#     print('done.')
# ------------------------------ old functions ------------------------------


def kml2polygon(kml_file):
    # unzip kmz to get kml
    if kml_file.endswith('.kmz'):
        dir_name = os.path.dirname(kml_file)
        with zipfile.ZipFile(kml_file, 'r') as f:
            files = f.namelist()
            f.extract(files[0], dir_name)
        kml_file = os.path.join(dir_name, 'doc.kml')

    domTree = parse(kml_file)
    rootNode = domTree.documentElement
    Placemarks = rootNode.getElementsByTagName('Placemark')

    polygon_dict = {}
    j = 0

    for Placemark in Placemarks:
        name = Placemark.getElementsByTagName('name')[0].childNodes[0].data
        ploygon = Placemark.getElementsByTagName('Polygon')[0]
        outerBoundaryIs = ploygon.getElementsByTagName('outerBoundaryIs')[0]
        LinearRing = outerBoundaryIs.getElementsByTagName('LinearRing')[0]
        coordinates = LinearRing.getElementsByTagName(
            'coordinates')[0].childNodes[0].data
        lon_lat = [i.split(',')[0:2] for i in coordinates.strip().split(' ')]
        polygon_dict[name + '-' + str(j)] = np.asarray(lon_lat,
                                                       dtype='float64')
        j += 1
    return polygon_dict


def cut_vel_single(kml_file, vel_file, out_vel_file):
    polygon_dict = kml2polygon(kml_file)
    vel = np.loadtxt(vel_file)
    for _, polygon in polygon_dict.items():
        out_data = np.arange(vel.shape[1])
        for line in vel:
            if inpolygon(line[1:3], polygon):
                out_data = np.vstack((out_data, line))
        if out_data.size > vel.shape[1]:
            np.savetxt(out_vel_file, out_data[1:, :], fmt='%4f')
    print('done.')

    
def cut_ts_single(kml_file, ts_file, out_ts_file):
    polygon_dict = kml2polygon(kml_file)
    data = np.loadtxt(ts_file)
    ts = data[1:, :]
    for _, polygon in polygon_dict.items():
        out_data = data[0, :]
        for line in ts:
            if inpolygon(line[1:3], polygon):
                out_data = np.vstack((out_data, line))
        if out_data.size > ts.shape[1]:
            np.savetxt(out_ts_file, out_data, fmt='%4f')
    print('done.')



def cut_vel_multi(kml_file, vel_file):
    vel = np.loadtxt(vel_file)
    polygon_dict = kml2polygon(kml_file)
    num = len(polygon_dict)
    i = 0
    for name, polygon in polygon_dict.items():
        i += 1
        print(f'\rProcessing: {i}/{num}', end=" ", flush=True)
        out_data = np.arange(vel.shape[1])
        for line in vel:
            if inpolygon(line[1:3], polygon):
                out_data = np.vstack((out_data, line))
        out_file = name + '-vel.txt'
        if out_data.size > vel.shape[1]:
            np.savetxt(out_file, out_data[1:, :], fmt='%4f')
    print(f'\rProcessed: {i}/{num}', end=" ", flush=True)


def cut_ts_multi(kml_file, ts_file):
    data = np.loadtxt(ts_file)
    ts = data[1:, :]
    polygon_dict = kml2polygon(kml_file)
    num = len(polygon_dict)
    i = 0
    for name, polygon in polygon_dict.items():
        i += 1
        print(f'\rProcessing: {i}/{num}', end="", flush=True)
        out_data = data[0, :]
        for line in ts:
            if inpolygon(line[1:3], polygon):
                out_data = np.vstack((out_data, line))
        out_file = name + '-ts.txt'
        if out_data.size > ts.shape[1]:
            np.savetxt(out_file, out_data, fmt='%4f')
    print(f'\rProcessed: {i}/{num}', end=" ", flush=True)


# ## read velocity

# In[ ]:


vel_file = 'geo_velocity.h5'
mask_file = 'geo_maskTempCoh.h5'

velocity = read_vel(vel_file, mask_file, out_vel_file=None)


# In[ ]:


velocity_ds = random_downsample_vel(velocity, -10, 10, 0.2, out_ds_file=None)


# ## read time-series and velocity

# In[ ]:


os.chdir('/media/ly/file/sc_prj/cut')

ts_file = 'geo_timeseries_tropHgt_ramp_demErr.h5'
vel_file = 'geo_velocity.h5'
mask_file = 'geo_maskTempCoh.h5'

ts_data, date = read_vel_ts(ts_file, vel_file, mask_file, out_vel_file=None, out_ts_file=None)


# In[ ]:


# sampled_ts = random_downsample_vel(ts_data, 9, -9, 0.15, out_ds_file=None)
# sampled_ts = random_downsample_disp(ts_data, 9, -9, 0.15, out_ds_file=None)


# ## make kmz

# In[ ]:


prep_data_for_kmz(ts_data, date, out_vel_file='vel.txt', out_ts_file='ts.txt')
# prep_data_for_kmz(sampled_ts, date, out_vel_file='vel_ds.txt', out_ts_file='ts_ds.txt')


# In[ ]:


get_ipython().system('python3 make_kmz_timeseries.py -t ts_ds.txt -o ts_ds.kmz')


# In[ ]:


get_ipython().system('python3 make_kmz.py -v vel_ds.txt -o vel_ds.kmz')


# ## cut velocity

# ### single

# In[ ]:


cut_vel_single('single.kml', 'vel.txt', 'vel_cut.txt')


# In[ ]:


get_ipython().system('python3 make_kmz.py -v vel_cut.txt -o vel_cut -s 0.6')


# ### multiple

# In[ ]:


cut_vel_multi('cut.kmz', 'vel.txt')


# In[ ]:


import glob
files = glob.glob('Untitled Polygon-*-vel.txt')
for file in files:
    print(f'\rProcessing: {files.index(file) + 1}/{len(files)}', end=" ", flush=True)
    cmd_str = f"python3 make_kmz.py -v '{file}' -o '{file[:-4]}' -s 0.6"
    os.system(cmd_str)
print(f'\rProcessed: {len(files)}/{len(files)}', end=" ", flush=True)


# ## cut timeseries

# ### single

# In[ ]:


cut_ts_single('single.kml', 'ts.txt', 'ts_cut.txt')


# In[ ]:


get_ipython().system('python3 make_kmz_timeseries.py -t ts_cut.txt -o ts_cut -s 0.6')


# ### multiple

# In[ ]:


cut_ts_multi('cut.kml', 'ts.txt')


# In[ ]:


import glob
files = glob.glob('Untitled Polygon-*-ts.txt')
for file in files:
    print(f'\rProcessing: {files.index(file) + 1}/{len(files)}', end=" ", flush=True)
    cmd_str = f"python3 make_kmz_timeseries.py -t '{file}' -o '{file[:-4]}' -s 0.6"
    os.system(cmd_str)
print(f'\rProcessed: {len(files)}/{len(files)}', end=" ", flush=True)


# ## plot timeseries displacement

# getting displacement by number, must use complete ts_data (not downsampled)

# In[ ]:


num_list = [1000]
plot_displacement(num_list, ts_data, date, aspect=0.4,
                  figsize=(30, 15), y_lim=[-100, 50], fig_name=None)


# In[ ]:




