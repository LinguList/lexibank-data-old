# `pylexibank`

## Install

Since `pylexibank` has quite a few dependencies, installing it will result in installing
many other python packages along with it. To avoid any side effects for your default
python installation, we recommend installation in a 
[virtual environment](https://virtualenv.pypa.io/en/stable/).

Some code of `pylexibank` relies on LingPy functionality which is not yet released, thus,
LingPy should be installed from the source repository, running
```
$ git clone https://github.com/lingpy/lingpy/
$ cd lingpy
$ python setup.py install
```

Since `pylexibank` is used to manage data in the `lexibank-data` repository, we recommended
installing it from the source code available in each clone of this repository. If you cloned
the repository into a directory `lexibank-data`, change into this directory and run
```
pip install -e
```

This will install `pylexibank` and all dependencies in such a way that
- the code for the installed package is 
  [editable](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs), 
  i.e. you can use your repository clone also to contribute to `pylexibank`,
- the python package will be able to infer the location of the data repository.

Some functionality in `pylexibank` (in particular the `cldf` command), require access to
[Glottolog](http://glottolog.org) or [Concepticon](http://concepticon.clld.org) data.
Since the data of both these applications is curated in git repositories as well, the easiest
way to achieve this is by cloning [clld/glottolog](https://github.com/clld/glottolog) and
[clld/concepticon-data](https://github.com/clld/concepticon). But you could also download
(and unpack) a released version of these repositories.


## Usage

`pylexibank` can be used in two ways:
- The command line interface provides mainly access to the functionality for the `lexibank`
  [curation workflow](../workflow.md).
- The `pylexibank` package can also used like any other python package in your own python
  code to access `lexibank-data` in a programmatic (and consistent) way.