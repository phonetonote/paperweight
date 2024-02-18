# paper weight

## features
- searches folders of markdown files for links to pdfs
- backup the pdf's in a sqlite database
- full pdf saved in a blob
- text extraction via https://github.com/pymupdf/PyMuPDF
- text embeddings from openai stored as [encoded JSON](https://datasette.io/plugins/datasette-faiss#user-content-configuration)
- metadata via gpt-3.5 turbo functions
- 3d viz of embeddings via dash and plotly

## limitations

embeddings are currently limited to the first 8191 characters of the pdf.  this is the max input size of `text-embedding-3-small`. chunking the text and sending it in parts to support full embeddings is a future feature.

(2/15/24 update) - perhaps huge context windows are around the corner anyways

full text is currently limited to 10mb per row. this is arbitrary and will be configurable in the future.


## usage

(coming soon)

requirements:
- openai api key
- python 3.11.1
   - probably works with 3.12, but has not been tested

## cloud backup

you can optionally setup a cloud backup of the sqlite database.

this is using cloudflare r2 storage. I evaluated using turso embedded replicas for this, but turso does not seem to support BLOB storage, so I did not think it would be a good fit. The primary purpose of these backups is so your PDFs do not dissapear to link rot.

TODO detailed instructions

If you want to turn the non-blob columns into a ~webscale~ db, turso db would probably work well with this project.


### WAL?

I did not run into any issues serving the dash app locally which pulls from the sqlite database file, as I am inserting into the database in a separate thread.

If I were to run into issues, [turning on WAL mode](https://til.simonwillison.net/sqlite/enabling-wal-mode) would probably be the first thing I would try.

If you are running into issues, or want to pull from the database more intensely, you might want to consider turning on WAL mode. The main downside seems to be the creation of two more files.

## coming soon (?)

-------
- n-shot training to extract data better
- turbo mode with many [modal](https://modal.com/) containers
- support more link types
   - arxiv
   - wikipedia
- backing up full text and embeddings
- datasette plugin
- gptstore plugin (?)
- service to run in the cloud on different data sources



## thank you
inspired by and hopefully mostly compatible with
- https://datasette.io/plugins/datasette-llm-embed
- https://datasette.io/plugins/datasette-faiss

inpired by [varepsilon](https://twitter.com/var_epsilon)'s [rsrch.space](https://github.com/ishan0102/rsrch.space)

inspired to work with files over apps by [kepano](https://twitter.com/kepano/status/1675626836821409792)
