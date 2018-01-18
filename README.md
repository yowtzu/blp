#blp

## Introduction
A Bloomberg API Wrapper that returns pandas DataFrame.

This service mimic the 3 Bloomberg Excel API functions:

1. BDP
2. BDS
3. BDH

All calls are blocking and return a (possibly empty) DataFrame object, a BLPRequestError is raised when invalid security/field is used.

## Installation guide

1. Clone this package
```
git clone https://github.com/yowtzu/blp.git
```
(Optional). Make sure dependencies channel (mbonix) is included
```
conda config --add channels mbonix
```
it is hard_coded the %CONDA_HOME% to be C:\Users\%USERNAME%\Anaconda in the bld.bat file, change it to the corresponding path as necessary.

2. Navigate to the base directory (~/blp/.) and build the conda package
```
conda build . 
```
3. Install the build package locally
```
conda install blp --use-local
```

## Basic usage

```python
from blp import blp
bloomberg = blp.BLPService()
df = bloomberg.BDS(...)
```

For more details, refer the test_blp.py test class.

