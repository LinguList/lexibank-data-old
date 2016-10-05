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

Yes, you can. We offer a DOI service, that will give your dataset a digital object identifier. In this way, you can publish your data with `lexibank` and other people will be able to use and quote it as a regular citation.

## I compiled a dictionary, can I publish it with `lexibank`?

No. Dictionaries are not the target of `lexibank`, as we only assemble collections of data which are normalized for meanings. If your dictionary is fully linked to the [Concepticon](http:///concepticon.clld.org), you can publish it with `lexibank`, but if this is not the case, you should consider publishin with [Dictionaria](http://home.uni-leipzig.de/dictionaryjournal/) instead.

## I have compiled a word list for a so far unknown language. It is not on Glottolog. Can I still add it to `lexibank`?

Yes, you can. We are working in close interaction with Glottobank, and we report and discuss all problems of missing or erroneous Glottocodes. Ideally, you would also contact Glottolog to report the missing language variety, providing them with coordinates and suggestions for classification. 

**FIXME: fix procedure here: what are the minimal requirements? Can we add user-defined coordinates for language varieties? We have examples of that kind of data already.**

## I have tried to link my concepts to the Concepticon, but there are at least twenty concepts for which I could not identify a useful concept set, can I still add my data to `lexibank`?

Sure. If concepts are assigned no Concepticon ID, we leave them unlinked, and they may still be valuabe for us. If you have reason to assume that important comparison concepts are actually missing in the Concepticon, we would further ask you to file an issue at https://github.com/clld/concepticon-data, to make sure that your new suggestions will be included in later versions of the Concepticon.

## I have typed off a very interesting resource from the 1970ies which would be a very nice addon for `lexibank`. I don't have a licence, though. What should I do?

**FIXME: how do we deal with problematic licenses in general? Do we just publish the data and wait until people complain? Do we claim that 200 words are beyond licenses? We have already a couple of datasets where we don't really know what license they have...**

## I am a specialist in language family X. I realized that the dataset Y on this language family is showing a huge amount of errors. How can I fix them?

You cannot fix datasets which have been published, unless you can show that the errors were introduced by the `lexibank` curation process. Even if we fix a dataset according to your wishes, the originally published data will still have the errors. Instead we encourage you to correct the errors and publish them with `lexibank` as a new dataset which explicitly corrects the older version. Both versions, the old dataset, and your refinement, however, will remain in `lexibank` and allow people to compare how the knowledge about certain language families has developed.

## You have added my dataset to `lexibank`, linked the concepts and language varieties, and automatically evaluated the phonetic transcriptions. Your interpretation of my data, however, is wrong. Concept X is wrongly linked to the Concepticon, language variety Y has the wrong Glottocode, and sound Z has the wrong CLPA value. Can you correct the errors?

Sure we can, and we are glad for every help we can get from you in making `lexibank` more reliable. You can either commit your modifications as a pull request on GitHub, or you can contact the executive board by writing an email to lexibank@shh.mpg.de. In any case we will be very glad to improve on your data to make sure it is represented correctly.

## I have a very nice dataset for `lexibank` but it is written in Word format, and I hate computers. Can I still add it to `lexibank`?

Yes, you can, but depending on the general state of the data. If you have data and have problems in submitting it via GitHub, please contact our executive board at lexibank@shh.mpg.de.

