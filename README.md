# paper weight

## features
- searches folders of markdown files for links to pdfs
- backup the pdf's in a sqlite database
- full pdf saved in a blob
- text extraction via https://github.com/pymupdf/PyMuPDF
- text embeddings from openai stored as [encoded JSON](https://datasette.io/plugins/datasette-faiss#user-content-configuration)
- metadata via gpt-3.5 turbo functions

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

## coming soon (?)
- cloud backup
- dataviz via tensorboard
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
