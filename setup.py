from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

setup(
	name="garment_demo",
	version="0.0.1",
	description="Garment manufacturing & export operations on ERPNext",
	author="Nikunj",
	author_email="nikunj7943@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
)
