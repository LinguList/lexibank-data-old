# `lexibank` cookbook

The `lexibank` cookbook is a collection of recipes showing how to manage, access and
analyze data in `lexibank`, thereby introducing
- the `lexibank` API
- tools like LingPy

The recipes are implemented as [Jupyter notebooks](http://jupyter.org/), i.e. as documented
python code which can be run and modified locally and interactively. But of course the recipes
can also be followed just by reading through code and documentation.

## The recipes

- [Creating CLDF data for datasets](creating_cldf.ipynb)
- [Loading CLDF data into LingPy](loading_cldf_into_lingpy.ipynb)


## Running the recipes

To run the recipes you must
- [clone `lexibank-data`](https://github.com/glottobank/lexibank-data)
- install the `lexibank` dependencies running
```
python setup.py develop
```
- [install Jupyter Notebook](https://jupyter.readthedocs.io/en/latest/install.html)
- change into the `cookbook` directory and
- [start the Notebook server](https://jupyter.readthedocs.io/en/latest/running.html) 
