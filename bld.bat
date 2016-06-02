set CONDA_HOME=C:\Users\"%USERNAME%"\Anaconda3
xcopy "%CONDA_HOME%"\Lib\site-packages\blpapi "%CONDA_HOME%"\envs\_build\Lib\site-packages\blpapi /i
if errorlevel 1 exit 1

nosetests --verbose
if errorlevel 1 exit 1

"%PYTHON%" setup.py install
if errorlevel 1 exit 1

:: Add more build steps here, if they are necessary.

:: See
:: http://docs.continuum.io/conda/build.html
:: for a list of environment variables that are set during the build process.
