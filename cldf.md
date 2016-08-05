# `lexibank` CLDF

`glottobank/lexibank-data` stores interoperable wordlist data in the `cldf` subdirectories of each
dataset in a variant of the [CLDF](http://cldf.clld.org) format.


## Columns in the CLDF data file

Since interoperability of datasets is our main goal, we restrict the valid values for `Language_ID` and `Parameter_ID` 
in [CLDF data files](https://github.com/glottobank/cldf#the-data-file) as follows:
- `Language_ID` must be a valid Glottolog language identifier (aka glottocode) of the form `abcd1234` or empty.
- `Parameter_ID` must be a valid Concepticon concept set ID of the form `1234` or empty.

Incomplete mapping to Concepticon or Glottolog is then indicated by `""` values, and local identifiers can be supplied 
in additional fields of the data files as follows:

- `Language_name`: language name as given in source
- `Language_iso`: ISO-639-3 code as given in source
- `Language_local_ID`: identifier of language as given in source (preferably a URL)

These three additional fields should be enough to contain all necessary data to determine glottocodes at a later 
stage and to disambiguate rows within the dataset. The `Language_ID` field can then be used to compute the degree 
of glottolog mapping.

Concepts are handled in a similar way:

- `Parameter_name`: concept label as given in source
- `Parameter_local_ID`: identifier of concept as given in source (preferably a URL)


## Splitting `lexibank` datasets into multiple CLDF datasets

`lexibank` datasets may be partitioned into multiple CLDF datasets. This is recommended when subsets of the data
share the same metadata (e.g. source or other provenance information), distinct from other subsets.
If the data is split, the following conditions must be met:
- Each CLDF dataset must contain the same set and order of columns, i.e. it must be possible to get the complete
  data by concatenating the separate CLDF data files using tools like [csvstack](http://csvkit.readthedocs.io/en/0.9.1/scripts/csvstack.html).
- Each row of the dataset must be present in exactly one CLDF dataset.

These requirements make sure that we can run tools on all data of a dataset which only have to be configured once
per dataset; e.g. a transcription report may look for a column `Segments`, which should either be present in all
CLDF data files or in none.


## Example: Data from the ABVD

As an example, we look at a lexeme harvested from ABVD (the Austronesian Basic Vocabulary Database).

Based on the ISO 639-3 code [trv] specified for [Seediq L04 (Truku)](http://language.psy.auckland.ac.nz/austronesian/language.php?id=823)
the glottocode [taro1264 for Taroko](http://glottolog.org/resource/languoid/id/taro1264) is assigned as `Language_ID`.
But the variety name from ABVD "Seediq L04 (Truku)" is kept as `Language_name`, as well as the local ID `823`:

```
ID,Language_ID,Language_iso,Language_name,Language_local_ID,Parameter_ID,Parameter_name,Parameter_local_ID,Value,Context,Source,Cognate_Set,Comment,Loan
207953-1,taro1264,trv,Seediq L04 (Truku),823,1277,hand,1,baga,,li2004,51,,False
```

To make the local language ID more meaningful (e.g. to allow linking back to ABVD), the [CLDF metadata file]() specifies
a [`valueUrl` property](https://www.w3.org/TR/tabular-metadata/#cell-valueUrl) for the `Language_local_ID` column
```python
{
  "datatype": "string",
  "name": "Language_local_ID",
  "valueUrl": "http://language.psy.auckland.ac.nz/austronesian/language.php?id={Language_local_ID}"
},
```
which is a [URI template](https://tools.ietf.org/html/rfc6570) that can be expanded to yield a full URL pointing to
the language page in ABVD.
