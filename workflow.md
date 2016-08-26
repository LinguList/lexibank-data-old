# The `lexibank` workflow

Processing of datasets (individually or all at once) in `lexibank` is slit
into multiple steps, making up a workflow. Individual steps are implemented
and can be executed as subcommands of the `lexibank` command line interface
using a syntax like
```bash
$ lexibank <subcommand> <dataset-ID-or-path>
```

## `download`

Can be run unconditionally thereby re-creating the raw data in a dataset's 
`raw` subdirectory.


## `cldf`

Can be run once `download` has completed. Recreates the dataset serialized in the
`lexibank` CLDF format.


## `report`

Can be run once `cldf` has completed. Creates a report on the transcriptions
used in a dataset and stores this report in `transcription.json`.

## `readme`

Can be run once `report` has completed. Create a dataset's landing page,
`README.md`.