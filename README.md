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
..* git clone https://github.com/yowtzu/blp.git

2. Navigate to ~/bld/. and build the conda package
..* conda build . 

3. Install the build package locally
..* conda install blp --use-local

## To use the service

```python
from blp import blp
bloomberg = blp.BLPService()
bloomberg.BDS(...)
```

For more detail, refer the test_blp.py test class.

