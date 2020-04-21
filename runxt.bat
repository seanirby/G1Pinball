rem command when experimenting with python profiling, assumes that you've got args hardcoded into mpf package (checkout branch 'profilingPerformance')
rem start cmd /k ".\venv\mpf-devo\Scripts\activate.bat && mpf build production_bundle && cd C:\Users\THINKPAD\dev\mpf && python -m cProfile -o profile_output.cprof mpf\__main__.py"


rem start cmd /k ".\venv\mpf-devo\Scripts\activate.bat && python -m mpf"

rem start cmd /k ".\venv\mpf-devo\Scripts\activate.bat && mpf both -xtV"

start cmd /k ".\venv\mpf-devo\Scripts\activate.bat && mpf build production_bundle && mpf both -xP"
