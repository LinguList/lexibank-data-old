# Lexibank

Lexibank is a public database and repository for lexical data from the languages of the world. The database will be used to refine cognate judgments, infer language relationships, construct language phylogenies, test hypotheses about deep language history, investigate factors that affect the mode and tempo of language evolution, model sound change, and facilitate quantitative comparisons with other types of linguistic data. 

The initial focus of Lexibank will be on compiling basic or core vocabulary, but ultimately the database will be expanded to include a full range of lexicon from all the world’s languages. For more information on Lexibank and how to use or submit data please see the project website

Please contact us for more information.

# lexibank-data

lexibank-data is the main data repository for the lexibank project. The lexibank webapp is [here](https://github.com/glottobank/lexibank).

It aims at providing unified access to data published in various places and ways via
- a unified dataset manipulation workflow,
- a common data format based on [CLDF](cldf.md),
- a set of data quality metrics, assessing the interoperability of datasets.


## Interoperable lexical data

On the surface, lexical data of the wordlist kind seems to be as simple as it gets: It's just triples of (language, concept, word). Of course such triples are only interoperable/comparable, if language and concept are identified in
a way that allows comparison - in the simplest case this means just telling whether two languages or concepts are the same.
Since `lexibank` aims at making all its datasets interoperable with each other, [hubs](https://en.wikipedia.org/wiki/Hub_(network_science_concept)) for the identification of languages and concepts seem to be the most appropriate approach (rather than trying to map languages and concepts between each two datasets).
Thus, we use [Concepticon](http://concepticon.clld.org) as our hub for concepts and [Glottolog](http://glottolog.org) as hub for language identification (see also [Glottolog and Concepticon [PDF]](https://cloudstor.aarnet.edu.au/plus/index.php/s/HlFdQxJ5sdS30PZ)).


## Glossary:

- **`lexibank` dataset:** A `lexibank` dataset is collection of lexical data (or data derived from lexical data such as cognate judgements) sharing the same provider. Dataset providers can be lexical databases like ABVD or [IDS](http://ids.clld.org) or supplemental material for publications. If the provided dataset is an aggregation of data from various sources, this can be indicated by splitting one `lexibank` dataset into multiple CLDF datasets, one for each source.
- **data provider:** An access point to harvest lexical data, e.g. a lexical database like ABVD or [IDS](http://ids.clld.org), supplemental material for a publication or a dataset archived with [ZENODO](https://zenodo.org).
- **`lexibank` CLDF:** `lexibank` uses [CLDF](cldf.md) - the **C**ross-**L**inguistic **D**ata **F**ormat as storage format for datasets.
- **Concepticon:** To make datasets comparable we need a mapping (aka [schema crosswalk](https://en.wik  osswalk)) between the concept lists (aka [Swadesh lists](https://en.wikipedia.org/wiki/Swadesh_list)) used in each dataset. Fortunately, this has already been done for many concept lists by the [CLLD Concepticon](http://concepticon.clld.org). `lexibank` uses Concepticon [concept sets](http://concepticon.clld.org/parameters) to identify concepts across datasets.
- **Glottolog:** [Glottolog](http://glottolog.org) is a comprehensive catalog of the world's languages and dialects. In addition to language identification, it also provides a genealogical classification and additional metadata like geographic coordinates, alternative names, etc. for each language.
- **CLPA:** The cross-linguistic phonetic alphabet is an initial attempt to provide a cross-linguistic dialect of the international phonetic alphabet (IPA) that can be used as an authoritative standard of what could be called the "least of what most people would agree with". While IPA is described, it is not necessarily standardized to allow for transcriptions that are easily readable by a machine. CLPA tries to fill this gap by 
  - referring to IPA definitions for all phonetic segments we encounter in datasets that provide phonetic transcriptions in segmented form (segmentation is needed, since non-segmented transcriptions tend to be ambiguous in IPA)
  - linking to further resources on phonetic inventories and the like, like, e.g., [phoible](http://phoible.org) or [pbase](http://pbase.phon.chass.ncsu.edu/)
  - adding transcription conventions on the sequence level, including secondary segmentation on the morpheme and the word level
  - providing a software API that allows users to check to which degree their data conforms to CLPA standards, and how well a given dataset could be converted to account for it
  
  The current state of clpa can be found at https://github.com/glottobank/clpa. CLPA is used to check those datasets that provide IPA transcriptions in segmented form (or from which these are automatically derived) for their degree to which they conform to CLPA, and also to calculate additional statistics, like the average phoneme inventory size of a dataset.
- **`lexibank` workflow:**
- **`lexibank` app:**
