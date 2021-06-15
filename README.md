[![Language](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/)

## TintPy ##

The Thorly InSAR Tools in Python (TintPy) is an package for Interferometric Synthetic Aperture Radar (InSAR) time series processing. It mainly based on [GAMMA](https://www.gamma-rs.ch/no_cache/software.html), [MintPy](https://github.com/insarlab/MintPy), [StaMPS](https://github.com/dbekaert/StaMPS), [GMT](https://www.generic-mapping-tools.org/).

## Download and setup MintPy ##

To use the package, you need to setup the environment a) by adding ${TintPy_HOME} to your $PYTHONPATH to make TintPy importable in Python and b) by adding ${TintPy_HOME} to your $PATH to make application scripts executable in command line, as shown below.

Add to your ~/.bashrc file for bash user. Source the file for the first time. It will be sourced automatically next time when you login.

```Bash
# >>> TintPy >>>
export TintPy_HOME=/home/ly/TintPy
export PATH=${PATH}:${TintPy_HOME}/CUT:${TintPy_HOME}/DEM:${TintPy_HOME}/GAMMA:${TintPy_HOME}/GAMMA/Sentinel-1:${TintPy_HOME}/GAMMA/Phase-stacking:${TintPy_HOME}/GAMMA/GACOS:${TintPy_HOME}/GAMMA/ALOS:${TintPy_HOME}/KMZ:${TintPy_HOME}/MintPy:${TintPy_HOME}/POEORB:${TintPy_HOME}/StaMPS:${TintPy_HOME}/StaMPS/GAMMA2StaMPS
export PYTHONPATH=${PYTHONPATH}:${TintPy_HOME}/CUT:${TintPy_HOME}/DEM:${TintPy_HOME}/GAMMA:${TintPy_HOME}/GAMMA/Sentinel-1:${TintPy_HOME}/GAMMA/Phase-stacking:${TintPy_HOME}/GAMMA/GACOS:${TintPy_HOME}/GAMMA/ALOS:${TintPy_HOME}/KMZ:${TintPy_HOME}/MintPy:${TintPy_HOME}/POEORB:${TintPy_HOME}/StaMPS:${TintPy_HOME}/StaMPS/GAMMA2StaMPS
export MATLABPATH=${TintPy_HOME}/GAMMA/GACOS:`echo $MATLABPATH`
# <<< TintPy <<<
```

Run the following in your terminal to download TintPy :

```Bash
git clone https://github.com/thorly/TintPy.git $TintPy_HOME
```
