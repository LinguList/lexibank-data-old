# Data curation for `lexibank`

Data in the `lexibank-data` repository is curated using functionality of a python package
[`pylexibank`](pylexibank), which is distributed with the repository. Thus, to work with
`lexibank-data`, you need to [install this package](pylexibank/README.md).


## The `lexibank` processing workflow

Processing of datasets (individually or all at once) in `lexibank` is slit
into multiple steps, making up a workflow. Individual steps are implemented
and can be executed as subcommands of the [`lexibank` command line interface](#cli)
using a syntax like
```bash
$ lexibank <subcommand> <dataset-ID-or-path>
```

### `download`

Can be run unconditionally thereby re-creating the raw data in a dataset's 
`raw` subdirectory.


### `cldf`

Can be run once `download` has completed. Recreates the dataset serialized in the
`lexibank` CLDF format.


### `report`

Can be run once `cldf` has completed. Creates a report on the transcriptions
used in a dataset and stores this report in `transcription.json`.

### `readme`

Can be run once `report` has completed. Create a dataset's landing page,
`README.md`.


## Editing `lexibank` data

`lexibank` supports three models of data editing:

1. Datasets curated outside of `lexibank`: Such datasets are simply pulled into `lexibank` by running their `download` command. It is the maintainers responsibility that the processing chain stays intact when data is updated.
2. Datasets curated in `raw` format in `lexibank`: Such datasets may have an established curation workflow tied to their original data format.
3. Datasets curated in `lexibank` CLDF format: These datasets implement "NOOP" `download` and `cldf` commands.

Any dataset specific comments (e.g. regarding language or concepticon mappings, of transcription decisions) should go into a file called `NOTES.md` in the dataset directory. This should be in markdown format, preferably as a set of bulletpoints (as it will be incorporated into the main `README.md` file.


## <a name="cli"> </a>The `lexibank` command line interface

Upon [installation of `pylexibank`](pylexibank/README.md), a command `lexibank` is installed,
which can be invoked from the command line:
```
$ lexibank --help
usage: lexibank [-h] [--verbosity VERBOSITY] [--lexibank-repos LEXIBANK_REPOS]
                [--glottolog-repos GLOTTOLOG_REPOS]
                [--concepticon-repos CONCEPTICON_REPOS]
                command ...

Main command line interface of the pylexibank package.

positional arguments:
  command               readme|download|cldf|ls|report|word_length|coverage
  args

optional arguments:
  -h, --help            show this help message and exit
  --verbosity VERBOSITY
                        increase output verbosity
  --lexibank-repos LEXIBANK_REPOS
                        path to lexibank data repository
  --glottolog-repos GLOTTOLOG_REPOS
                        path to glottolog data repository
  --concepticon-repos CONCEPTICON_REPOS
                        path to concepticon data repository

Use 'lexibank help <cmd>' to get help about individual commands.
```

If you don't want to specify the `--glottolog-repos` or `--concepticon-repos` options
for your system all the time, you may create an alias or `DOSKEY` providing access to
the `lexibank` command with prefilled options.


## The `lexibank` API

TODO