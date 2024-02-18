import argparse
import logging
import os
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

    init_db(db_name=args.db_name)

    dash_app = DashApp(db_name=args.db_name)
    dash_thread = threading.Thread(target=run_dash_app, args=(dash_app,), daemon=False)
    dash_thread.start()

    LinkExtractor(args.directory, args.db_name, args.model_name).extract_links()


if __name__ == "__main__":
    main()
