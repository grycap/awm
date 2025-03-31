# coding: utf-8

from setuptools import setup, find_packages
from awm import __version__

NAME = "awm"
VERSION = __version__
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "connexion",
    "swagger-ui-bundle>=0.0.2"
]

setup(
    name=NAME,
    version=VERSION,
    description="EOSC Application Workflow Management API",
    author_email="",
    url="",
    keywords=["Swagger", "EOSC Application Workflow Management API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['awm=awm.__main__:main']},
    long_description="""\
    Deployment service for European Open Science Cloud nodes
    """
)
