from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='anidbsync',
    version='0.0.1',
    description='Synchronizes Watch Status from AniDB to Kodi',
    long_description=readme,
    author='Gabriel Nadler',
    author_email='nadler.gabriel@gmail.com',
    url='https://github.com/Tyderion/kodi-anidb-sync',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)