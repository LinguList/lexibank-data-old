# lexibank-data

lexibank-data is a repository intended to bring together (wordlist-like) data and tools in the field of Historical Linguistics.
It aims at providing unified access to data published in various places and ways via
- a unified dataset manipulation workflow,
- a common data format based on [CLDF](http://cldf.clld.org),
- a set of data quality metrics, assessing the interoperability of datasets.


## Interoperable lexical data

On the surface, lexical data of the wordlist kind seems to be as simple as it gets: It's just triples of (language, concept, word). Of course such triples are only interoperable/comparable, if language and concept are identified in
a way that allows comparison - in the simplest case this means just telling whether two languages or concepts are the same.
Since `lexibank` aims at making all its datasets interoperable with each other, [hubs](https://en.wikipedia.org/wiki/Hub_(network_science_concept)) for the identification of languages and concepts seem to be the most appropriate approach (rather than trying to map languages and concepts between each two datasets).
Thus, we use [Concepticon](http://concepticon.clld.org) as our hub for concepts and [Glottolog](http://glottolog.org) as hub for language identification (see also [Glottolog and Concepticon [PDF]](https://cloudstor.aarnet.edu.au/plus/index.php/s/HlFdQxJ5sdS30PZ)).


## Glossary:

- **`lexibank` dataset:** A `lexibank` dataset is collection of lexical data (or data derived from lexical data such as cognate judgements) sharing the same provider. Dataset providers can be lexical databases like ABVD or [IDS](http://ids.clld.org) or supplemental material for publications. If the provided dataset is an aggregation of data from various sources, this can be indicated by splitting one `lexibank` dataset into multiple CLDF datasets, one for each source.
- **data provider:** An access point to harvest lexical data, e.g. a lexical database like ABVD or [IDS](http://ids.clld.org), supplemental material for a publication or a dataset archived with [ZENODO](https://zenodo.org).
- **`lexibank` CLDF:** `lexibank` uses [CLDF](http://cldf.clld.org) as storage format for datasets. Since interoperability of datasets is our main goal, we restrict the valid values for `Language_ID` and `Parameter_ID` in [CLDF data files](https://github.com/glottobank/cldf#the-data-file) as follows:
  - `Language_ID` must be a valid Glottolog language identifier (aka glottocode) of the form `abcd1234` or empty.
  - `Parameter_ID` must be a valid Concepticon concept set ID of the form `1234` or empty.
  Incomplete mapping to Concepticon or Glottolog is then indicated by `""` values, and local identifiers can be supplied in additional fields of the data files.
- **Concepticon:** To make datasets comparable we need a mapping (aka [schema crosswalk](https://en.wik  osswalk)) between the concept lists (aka [Swadesh lists](https://en.wikipedia.org/wiki/Swadesh_list)) used in each dataset. Fortunately, this has already been done for many concept lists by the [CLLD Concepticon](http://concepticon.clld.org). `lexibank` uses Concepticon [concept sets](http://concepticon.clld.org/parameters) to identify concepts across datasets.
- **Glottolog:** [Glottolog](http://glottolog.org) is a comprehensive catalog of the world's languages and dialects. In addition to language identification, it also provides a genealogical classification and additional metadata like geographic coordinates, alternative names, etc. for each language.
- **CLPA:**
- **`lexibank` workflow:**
- **`lexibank` app:**
