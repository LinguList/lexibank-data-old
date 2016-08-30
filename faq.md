# Frequently asked questions

## Can I add cognates to existing `lexibank` datasets?

Yes! You can do this by creating a derived dataset
should handle derived dataset as follows:

1. The fact that a dataset is derived from another dataset should be stated in the
   metadata of the dataset using
    - [dc:isVersionOf](http://dublincore.org/documents/dcmi-terms/#terms-isVersionOf) to link to source dataset
    - [dc:provenance](http://dublincore.org/documents/dcmi-terms/#terms-provenance) to describe how it was derived
2. The derived dataset comprises it's derived version of the original data, i.e. it should
    - either implement (or import) identical `download` functions, if all changes can be applied automatically
    - or download the raw data from a published version of the derived data
    - or provide the derived raw data in `glottobank/lexibank-data`.
3. The derived dataset must implement a `cldf` function - which may be similar to the one for the source dataset, but should only be imported if the maintainers of both datasets are identical.


## Can I publish a dataset through `lexibank`?

FIXME: Check eligibility for using [DOI service of MPDL](https://doi.mpdl.mpg.de/)