from setuptools import setup, Extension
import sys
import os
import platform

# Get Python include directory
python_include = sys.executable.replace('python.exe', 'include') if platform.system() == "Windows" else None

# Windows SDK paths
if platform.system() == "Windows":
    sdk_include = r"C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0"
    sdk_lib = r"C:\Program Files (x86)\Windows Kits\10\Lib\10.0.22621.0\um\x64"
    
    # Visual Studio paths
    vs_include = r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.43.34808\include"
    vs_lib = r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.43.34808\lib\x64"

ch341_module = Extension('ch341',
    sources=['hardware/ch341.c'],
    include_dirs=[
        python_include,
        vs_include,
        os.path.join(sdk_include, 'um'),
        os.path.join(sdk_include, 'shared'),
    ] if platform.system() == "Windows" else [],
    library_dirs=[
        sdk_lib,
        vs_lib,
    ] if platform.system() == "Windows" else [],
    libraries=['setupapi', 'hid'],
    define_macros=[('WIN32', '1')] if platform.system() == "Windows" else [],
    extra_compile_args=['-Wall'],
)

setup(
    name='ch341',
    version='1.0',
    description='CH341 USB-to-I2C driver',
    ext_modules=[ch341_module]
)