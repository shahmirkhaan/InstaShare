from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
# When using flask-sqlalchemy add sqlite3.dll to include_files
buildOptions = dict(
    packages = [],
    excludes = [],
    #include_files=[r'"C:Anaconda2\\Library\\plugins"']
)

import sys
base = 'Win32GUI' if sys.platform=='win32' else None
# base = 'Console'

executables = [
    Executable('set_up.py', base=base)
]

setup(name='Test',
      version = '1.0',
      description = '',
      options = dict(build_exe = buildOptions),
      executables = executables)