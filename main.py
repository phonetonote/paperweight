import argparse
import logging
import os
from cloud_backup import backup_db
from db import init_db
from link_extractor import LinkExtractor
from dotenv import load_dotenv
from dash_app import DashApp
import threading


def parse_arguments():
    parser = argparse.ArgumentParser()

    dir_name = os.getenv("DIRECTORY_NAME") or "."
    parser.add_argument("--directory", help="Path to directory of markdown files", default=dir_name)

    db_name = os.getenv("DB_NAME") or "papers.db"
    parser.add_argument("--db-name", help="Database name", default=db_name)

    model_name = os.getenv("MODEL_NAME") or "gpt-3.5-turbo-0125"
    parser.add_argument("--model-name", help="OpenAI model name", default=model_name)

    verbose_env = os.getenv("VERBOSE", "False").lower() in ("true", "1", "t")
    parser.add_argument("--verbose", help="Verbose mode", action="store_true", default=verbose_env)

    remain_open_env = os.getenv("REMAIN_OPEN", "False").lower() in ("true", "1", "t")
    parser.add_argument(
        "--remain-open", help="Remain open mode", action="store_true", default=remain_open_env
    )

    return parser.parse_args()


def run_dash_app(dash_app):
    dash_app.run(debug=False)


def main():
    load_dotenv()
    args = parse_arguments()

    if args.verbose:
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        logging.info(f"Starting link extraction from {args.directory} in verbose mode")
    else:
        logging.basicConfig(level=logging.CRITICAL)

    init_db(db_name=args.db_name)

    dash_app = DashApp(db_name=args.db_name)
    dash_thread = threading.Thread(target=run_dash_app, args=(dash_app,), daemon=False)
    dash_thread.start()

    LinkExtractor(args.directory, args.db_name, args.model_name).extract_links()

    s3_bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_endpoint_url = os.getenv("S3_ENDPOINT_URL")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    s3_region_name = os.getenv("S3_REGION_NAME") or "auto"

    if not all(
        [s3_bucket_name, s3_endpoint_url, aws_access_key_id, aws_secret_access_key, args.db_name]
    ):
        print("skip backup, missing s3 info")
    else:
        backup_db(
            args.db_name,
            s3_bucket_name,
            s3_endpoint_url,
            aws_access_key_id,
            aws_secret_access_key,
            s3_region_name,
        )

    if not args.remain_open:
        print("shutting down dash app")
        # flask and by extension dash is designed for dev mode and to be killed abruptly
        os._exit(0)
    else:
        print("running in remain open mode, visit the dash app at http://127.0.0.1:8050/")


if __name__ == "__main__":
    main()
