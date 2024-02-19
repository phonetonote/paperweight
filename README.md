# paperweight

paperweight backs up and extracts info from the pdfs in a folder of markdown files

## features
- searches folders of markdown files for links to pdfs
- backup the pdf's in a sqlite database
- full pdf saved in a blob
- text extraction via https://github.com/pymupdf/PyMuPDF
- text embeddings from openai stored as [encoded JSON](https://datasette.io/plugins/datasette-faiss#user-content-configuration)
- metadata via gpt-3.5 turbo functions
- 3d viz of embeddings via dash and plotly
- cloud backup via [cloudflare r2](https://developers.cloudflare.com/r2/examples/aws/boto3/) or amazon s3

## limitations

embeddings are currently limited to the first 8191 characters of the pdf.  this is the max input size of `text-embedding-3-small`. chunking the text and sending it in parts to support full embeddings is a future feature.

(2/15/24 update) - perhaps huge context windows are around the corner anyways

full text is currently limited to 10mb per row. this is arbitrary and will be configurable in the future.

## Usage

### CLI Args
--directory: Path to the directory containing markdown files. Defaults to the value of the DIRECTORY_NAME environment variable or the current directory if not set.

--db-name: The name for the database. Defaults to the value of the DB_NAME environment variable or "papers.db" if not specified.

--model-name: Specifies the OpenAI model name to be used. Defaults to the value of the MODEL_NAME environment variable or "gpt-3.5-turbo-0125" if not provided.

--verbose: Enables verbose mode, providing detailed logging. This defaults to the boolean value of the VERBOSE environment variable or False if not set.

--remain-open: Keeps the application running even after processing is complete, useful for continuous operation or debugging. This defaults to the boolean value of the REMAIN_OPEN environment variable or False if not specified.

### Environment Variables
To enhance security and flexibility, certain configurations are managed through environment variables:

OPENAI_API_KEY: Your OpenAI API key, required for using the GPT-3.5 Turbo model. This is not explicitly called for anywhere in the application code, but is rather automagically used by the openai library.

S3_BUCKET_NAME: Specifies the S3 bucket name where backups are stored. Required for the backup functionality.

S3_ENDPOINT_URL: The endpoint URL for S3 services, necessary for accessing the S3 bucket.

AWS_ACCESS_KEY_ID: Your AWS access key ID, essential for authentication with AWS services.

AWS_SECRET_ACCESS_KEY: Your AWS secret access key, used alongside the access key ID for secure access to AWS services.

S3_REGION_NAME: Defines the AWS region for the S3 service. Defaults to "auto" if not explicitly set, allowing automatic determination based on the endpoint URL.

DIRECTORY_NAME: (Optional) Can be set to define a default directory for --directory, overriding the default current directory.

DB_NAME: (Optional) Sets a default database name for --db-name, overriding the default "papers.db".

MODEL_NAME: (Optional) Determines the default model name for --model-name, if not specified via CLI, defaulting to "gpt-3.5-turbo-0125".

VERBOSE: (Optional) Can be set to "true" to enable verbose mode by default, overriding the CLI --verbose flag.

REMAIN_OPEN: (Optional) When set to "true", the application remains open after processing, overriding the --remain-open CLI flag. This is used to continue looking at the dash app after processing is complete.

#### .env Example
To configure your script with environment variables, you can use a `.env` file. Here's an example that you can customize:

```
# AWS S3 Configuration
S3_BUCKET_NAME=your_bucket_name
S3_ENDPOINT_URL=https://s3.your-region.amazonaws.com
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
S3_REGION_NAME=your_region_name

# Application Configuration
DIRECTORY_NAME=./path/to/markdowns
DB_NAME=papers.db
MODEL_NAME=gpt-3.5-turbo-0125
VERBOSE=true
REMAIN_OPEN=false
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
- backing up full text and embeddings
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
