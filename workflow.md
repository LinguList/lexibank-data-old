# Data curation in `lexibank`

## The `lexibank` processing workflow

Processing of datasets (individually or all at once) in `lexibank` is slit
into multiple steps, making up a workflow. Individual steps are implemented
and can be executed as subcommands of the `lexibank` command line interface
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
