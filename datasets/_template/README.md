
A 'lexibank` dataset
====================

`lexibank` datasets package 
- the lexical data contributed by one data provider,
- code to create `lexibank` CLDF datasets from the raw data,
- lists of languages and concepts used in the data to allow control over the mapping to Concepticon and Glottolog.

This information is organized in a directory as follows:

```
datasets/<dataset-ID>/
├── raw/
├── cldf/
├── metadata.json
├── __init__.py
├── languages.csv
├── concepts.csv
└── README.md
```
