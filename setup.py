import codecs
import os.path

from setuptools import find_packages, setup

with open("README.md") as fh:
    long_description = fh.read()


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        msg = "Unable to find version string."
        raise RuntimeError(msg)


setup(
    name="netbox-peering-manager",
    version=get_version("netbox_peering_manager/version.py"),
    description="BGP related stuff",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jsenecal/netbox-peering-manager",
    author="Jonathan Senecal",
    author_email="jonathan.senecal@metrooptic.com",
    install_requires=[
        "httpx",
        "tenacity",
        "netbox-routing @ git+https://github.com/DanSheps/netbox-routing.git@14318f1c",
    ],
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Framework :: Django",
        "Programming Language :: Python :: 3",
    ],
)
