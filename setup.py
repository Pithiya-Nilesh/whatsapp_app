from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in whatsapp_app/__init__.py
from whatsapp_app import __version__ as version

setup(
	name="whatsapp_app",
	version=version,
	description="this app for whatsapp integration",
	author="Nilesh Pithiya",
	author_email="nilesh@sanskartechnolab.in",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
