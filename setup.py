from setuptools import setup, find_packages

setup(
    name='trello-to-deck',
    version='0.1',
    packages=find_packages(where='trello-to-deck'),
    url='https://github.com/maxammann/trello-to-deck',
    license='MIT',
    author='maxammann',
    author_email='max@maxammann.org',
    description='',
    install_requires=[
        'requests>=2.0.0'
    ],
    scripts=['scripts/trello-to-deck']
)
