from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='nextbike',
    version='1.2',
    author='Simon Dorer',
    description='nextbike api',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/sIDsID11/nextbike',
    project_urls={
        "Bug Tracker": "https://github.com/sIDsID11/nextbike/Issues"
    },
    license='MIT',
    packages=['nextbike'],
    install_requires=['requests'],
)