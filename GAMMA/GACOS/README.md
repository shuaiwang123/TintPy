# How to correct tropospheric phase using diff_by_baseline_gacos.py

## Step 1

You must install MATLAB, and make sure you can run MATLAB using command `matlab` in terminal. You can add the following code to `.bashrc` file.

```bash
# you need to change the path of MATLAB
export PATH=/usr/local/MATLAB/R2015b/bin:$PATH
```

## Step 2

Create a folder, and move these MATLAB scripts to it, then add this folder to MATLAB PATH(**open MATLAB to check it**). You can add the following code to `.bashrc` file.

```bash
# you need to change the folder path
insar_package="/home/ly/tools/insar_package"
export MATLABPATH=$insar_package:`echo $MATLABPATH`
```

## Step 3

Download Binary grid files from [GACOS Website](http://www.gacos.net/).

## Step 4

Run `diff_by_baseline_gacos.py`.
