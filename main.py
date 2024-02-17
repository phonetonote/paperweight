import argparse
import os
from db import init_db
from link_extractor import LinkExtractor
from dotenv import load_dotenv


def parse_arguments():
    parser = argparse.ArgumentParser()
    dir_name = os.getenv("DIRECTORY_NAME") or "."
    parser.add_argument("directory", help="Path to directory of markdown files", default=dir_name)
    db_name = os.getenv("DB_NAME") or "papers.db"
    parser.add_argument("--db-name", help="Database name", default=db_name)
    model_name = os.getenv("MODEL_NAME") or "gpt-3.5-turbo-0125"
    parser.add_argument("--model-name", help="OpenAI model name", default=model_name)
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_arguments()

    init_db(db_name=args.db_name)
    LinkExtractor(args.directory, args.db_name, args.model_name).extract_links()


if __name__ == "__main__":
    main()
