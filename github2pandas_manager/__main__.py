import argparse
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import os

from github2pandas_manager.config_parser import YAML_RequestDefinition
from github2pandas_manager.repository_handler import RequestHandlerFactory
from github2pandas_manager.data_extractor import Github_data_extractor
from github2pandas_manager.data_merger import Github_data_merger
from github2pandas_manager import utilities

def main(request_params, github_token):
    project_folder = Path(request_params.parameters.project_folder)
    project_folder.mkdir(parents=True, exist_ok=True)

    request_handler = \
        RequestHandlerFactory.get_request_handler(
                github_token=github_token,
                request_params=request_params
            )

    print(f"{len(request_handler.repository_list)} machting repositories found.")

    data_extractor = Github_data_extractor.start(
             github_token=github_token,
             request_handler=request_handler
    )
    
    df = Github_data_merger.merge(
        request_handler=request_handler
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process command line arguments.')
    parser.add_argument('-path', dest='config_file',
                        type=utilities.check_file_path,
                        required=True,
                        help='paste path to .yml config file')

    arguments = parser.parse_args()
    request_params = YAML_RequestDefinition(arguments.config_file)

    load_dotenv(find_dotenv())
    github_token = os.getenv("GITHUB_API_TOKEN")

    main(request_params=request_params, github_token=github_token)
    print("Aus Maus")
