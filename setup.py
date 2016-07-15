from setuptools import setup, find_packages


requires = [
    # list required third-party packages here
    'pycldf>=0.6.0',
    'openpyxl',
    'beautifulsoup4>=4.4.1',
    'requests',
    'clldutils>=1.0.1',
    'nameparser',
    'purl',
    'pyglottolog',
    'pyconcepticon',
]

setup(
    name='pylexibank',
    version='0.0',
    description='python package for the lexibank project',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ],
    author='Robert Forkel',
    author_email='forkel@shh.mpg.de',
    url='',
    keywords='data linguistics',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points={
        'console_scripts': ['lexibank=pylexibank.cli:main'],
    },
    tests_require=[],
    test_suite="pylexibank")
