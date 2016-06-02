#blp

A Bloomberg API Wrapper that returns pandas DataFrame.

This service mimic the 3 Bloomberg Excel API functions:
1. BDP
2. BDS
3. BDH

All calls are blocking and return a (possibly empty) DataFrame object, a BLPRequestError is raised when invalid security/field is used.
