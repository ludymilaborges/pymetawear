from distutils.command.clean import clean
from distutils.dir_util import copy_tree
from multiprocessing import cpu_count
from shutil import move 
from subprocess import call, STDOUT
from setuptools import setup
from setuptools.command.build_py import build_py

import os
import platform
import sys

machine = "arm" if "arm" in platform.machine() else ("x64" if sys.maxsize > 2**32 else "x86")
root = os.path.dirname(os.path.abspath(__file__))
warble = os.path.join(root, 'clibs', 'warble')
dest = os.path.join("mbientlab", "warble")

class WarbleClean(clean):
    def run(self):
        if (platform.system() == 'Windows'):
            dll = os.path.join(dest, "warble.dll")
            if os.path.isfile(dll):
                os.remove(dll)
        elif (platform.system() == 'Linux'):
            for f in os.listdir(dest):
                if (f.startswith("libwarble")):
                    os.remove(os.path.join(dest, f))

class WarbleBuild(build_py):
    @staticmethod
    def _move(src, dest, basename):
        for f in os.listdir(src):
            if (f.startswith(basename)):
                move(os.path.join(src, f), dest)

    def run(self):
        version_mk = os.path.join(warble, "version.mk")

        if os.path.exists(os.path.join(root, '.git')):
            if (call(["git", "submodule", "update", "--init", "--recursive"], cwd=root, stderr=STDOUT) != 0):
                raise RuntimeError("Could not init git submodule")

        if (platform.system() == 'Windows'):
            args = ["MSBuild.exe", "warble.vcxproj", "/p:Platform=%s" % machine, "/p:Configuration=Release"]
            if (os.path.exists(version_mk)):
                args.append("/p:SkipVersion=1")

            vs2017 = os.path.join(warble, 'vs2017')
            if (call(args, cwd=vs2017, stderr=STDOUT) != 0):
                raise RuntimeError("Failed to compile warble.dll")

            dll = os.path.join(vs2017, "" if machine == "x86" else machine, "Release", "warble.dll")
            move(dll, dest)
        elif (platform.system() == 'Linux'):
            args = ["make", "-C", warble, "-j%d" % (cpu_count())]
            if (os.path.exists(version_mk)):
                args.append("SKIP_VERSION=1")

            if (call(args, cwd=root, stderr=STDOUT) != 0):
                raise RuntimeError("Failed to compile libwarble.so")

            so = os.path.join(warble, 'dist', 'release', 'lib', machine)
            WarbleBuild._move(so, dest, 'libwarble.so')
        else:
            raise RuntimeError("pywarble is not supported for the '%s' platform" % platform.system())

        build_py.run(self)

so_pkg_data = ['libwarble.so*'] if platform.system() == 'Linux' else ['warble.dll']
setup(
    name='warble',
    packages=['mbientlab', 'mbientlab.warble'],
    version='1.1.0',
    description='Python bindings for MbientLab\'s Warble library',
    long_description=open(os.path.join(os.path.dirname(__file__), "README.rst")).read(),
    package_data={'mbientlab.warble': so_pkg_data},
    include_package_data=True,
    url='https://github.com/mbientlab/PyWarble',
    author='MbientLab',
    author_email="hello@mbientlab.com",
    cmdclass={
        'build_py': WarbleBuild,
        'clean': WarbleClean
    },
    keywords = ['mbientlab', 'bluetooth le', 'native'],
    python_requires='>=2.7',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ]
)
