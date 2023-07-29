import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name='nextbike',
    version='1.0',
    author='Simon Dorer',
    author_email='sdorer00@gmx.de',
    description='nextbike api',
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