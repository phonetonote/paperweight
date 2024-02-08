import argparse
from db import init_db
from link_extractor import LinkExtractor


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="path to directory containing markdown files")
    return parser.parse_args()


def main():
    args = parse_arguments()
    init_db()
    LinkExtractor(args.directory).extract_links()


if __name__ == "__main__":
    main()
