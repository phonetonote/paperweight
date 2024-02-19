# paperweight

paperweight backs up and extracts data from the pdf links in your markdown files

script running in CLI:

<img width="400" alt="cli screenshot" src="https://github.com/phonetonote/paperweight/assets/1139703/dc5f3caa-7277-4c91-bf3c-fd6f0ba6ed91">

dash showing embeddings in 3d space:

<img width="650" alt="dash screenshot" src="https://github.com/phonetonote/paperweight/assets/1139703/b1685280-652e-4f83-9179-db0f62f465f9">

sqlite db (shown in [Beekeper Studio Ultimate](https://www.beekeeperstudio.io/))

![image](https://github.com/phonetonote/paperweight/assets/1139703/f57ee402-f3ab-4fce-84e2-50dc3d4a803d)


## features
- finds links to pdfs in markdown files
- backup the pdf's in a sqlite database
- full pdf saved in a blob
- text extraction via https://github.com/pymupdf/PyMuPDF
- text embeddings from openai stored as [encoded JSON](https://datasette.io/plugins/datasette-faiss#user-content-configuration)
- metadata via gpt-3.5 turbo functions
  - title
  - keywords
  - authors
  - abstract
  - published_date
  - summary
  - institution
  - location
  - doi
- screenshot of first page saved as blob
- 3d viz of embeddings via dash and plotly
- cloud backup via [cloudflare r2](https://developers.cloudflare.com/r2/examples/aws/boto3/) or amazon s3

## limitations

embeddings are currently limited to the first 8191 tokens of the pdf.  this is the max input size of `text-embedding-3-small`. chunking the text and sending it in parts to support full embeddings is a future feature.

(2/15/24 update) - perhaps huge context windows are around the corner anyways

full text is currently limited to 10mb per row. this is arbitrary and will be configurable in the future.

## Usage

run via the command line with the following command
```
python main.py --directory ~/path/to/your/mds
```

the dash will be accessible on `http://127.0.0.1:8050/`. see the `REMAIN_OPEN` arg below for keeping the dash running when processing is complete.

### CLI Args
- `--directory` - path to the directory containing markdown files. defaults to the value of the `DIRECTORY_NAME` environment variable or the current directory if not set
- `--db-name` - the name for the database. defaults to the value of the `DB_NAME` environment variable or `papers.db` if not specified
- `--model-name` - specifies the OpenAI model name to be used. defaults to the value of the `MODEL_NAME` environment variable or `gpt-3.5-turbo-0125` if not provided
- `--verbose` - enables verbose mode, providing detailed logging. this defaults to the boolean value of the `VERBOSE` environment variable or `False` if not set
- `--remain-open` - keeps the application running even after processing is complete, useful for continuous operation or debugging. this defaults to the boolean value of the `REMAIN_OPEN` environment variable or `False` if not specified

### Environment Variables
To enhance security and flexibility, certain configurations are managed through environment variables:
- `OPENAI_API_KEY` - your OpenAI API key, required for generating embeddings and extracting data. this is not explicitly called for anywhere in the application code, but is rather automagically used by the openai library.
- `DIRECTORY_NAME` - (optional) can be set to define a default directory for `--directory`, overriding the default current directory
- `DB_NAME` - (optional) sets a default database name for `--db-name`, overriding the default `papers.db`
- `MODEL_NAME` - (optional) determines the default model name for `--model-name`, if not specified via CLI, defaulting to `gpt-3.5-turbo-0125`
- `VERBOSE` - (optional) can be set to `true` to enable verbose mode by default, overriding the CLI `--verbose` flag
- `REMAIN_OPEN` - (optional) when set to `true`, the application remains open after processing, overriding the `--remain-open` CLI flag. this is used to continue looking at the dash app after processing is complete.

#### more env vars for cloud backuop
the following environment variables are used for cloud backup functionality:
- `S3_BUCKET_NAME` - specifies the S3 bucket name where backups are stored
- `S3_ENDPOINT_URL` - the endpoint URL for S3 services
- `AWS_ACCESS_KEY_ID` - your AWS access key ID
- `AWS_SECRET_ACCESS_KEY` - your AWS secret access key
- `S3_REGION_NAME` - defines the AWS region for the S3 service. defaults to `auto` if not explicitly set, allowing automatic determination based on the endpoint URL


### .env example
To configure your script with environment variables, you can use a `.env` file. Here's an example that you can customize:

```
# Application Configuration
DIRECTORY_NAME=./path/to/markdowns
DB_NAME=papers.db
MODEL_NAME=gpt-3.5-turbo-0125
VERBOSE=true
REMAIN_OPEN=false

# AWS S3 Configuration
S3_BUCKET_NAME=your_bucket_name
S3_ENDPOINT_URL=https://s3.your-region.amazonaws.com
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
S3_REGION_NAME=your_region_name
```

replace the placeholder values with your actual configuration details. this file should be named `.env` and *should not* be committed to version control for security reasons (people can steal your openai key). this is why `.env` is in the `.gitignore` file.

## requirements
- openai api key
- python 3.11.1
   - probably works with 3.12, but has not been tested
- for cloud backup you will need the following. see https://developers.cloudflare.com/r2/examples/aws/boto3/ for more information on how to set up your keys and what the endpoint_url should be:
   - endpoint_url
   - access_key
   - secret_key

see `usage` above for how to configure these as environment variables.


## cloud backup

you can optionally setup a cloud backup of the sqlite database to aws s3/cloudflare r2.


see `usage` section for detailed instructions on how to set up the  backup.

I evaluated using turso embedded replicas for this, but turso [does not seem to support BLOB columns](https://github.com/tursodatabase/libsql-experimental-python/blob/29c6a23557ee028fbff415afc5486df13644c191/src/lib.rs#L370), so I did not think it would be a good fit. The primary purpose of these backups is so your PDFs do not dissapear to link rot, so the blob columns are important.


if you want to turn the non-blob columns into a distributed database, perhaps to create an API to serve your papers with a JS based frontend, you might want to consider using turso. I have not tried this, but it seems like it would be a good fit for that use case.

## WAL?

I did not run into any issues serving the dash app locally which pulls from the sqlite database file, as papers are inserted into the same database in a separate thread.

if I were to run into issues, [turning on WAL mode](https://til.simonwillison.net/sqlite/enabling-wal-mode) would probably be the first thing I would try.

if you are running into issues, or want to pull from the database more intensely, you might want to consider turning on WAL mode. The main downside seems to be the creation of two more files.

## prompt engineering

results can be improved by better prompt engineering `extractor` in `models.py`


## coming soon (?)
- n-shot training to extract data better
- turbo mode with many [modal](https://modal.com/) containers
- support more link types
   - arxiv
   - wikipedia
- support local pdf files
- backing up full text and embeddings
- make embeddings and NER optional
- modularize the existing functionality to reduce core dependencies
   - dash server is a separate service
   - cloud backup is a separate service
- test coverage
- datasette plugin
- gptstore plugin (?)
- service to run in the cloud on different data sources



## thank you
inspired by and hopefully mostly compatible with
- https://datasette.io/plugins/datasette-llm-embed
- https://datasette.io/plugins/datasette-faiss

inpired by [varepsilon](https://twitter.com/var_epsilon)'s [rsrch.space](https://github.com/ishan0102/rsrch.space)

inspired to work with files over apps by [kepano](https://twitter.com/kepano/status/1675626836821409792)
