import argparse
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import os

import utilities
from config_parser import YAML_RequestDefinition
from repository_handler import RepositoryHandlerFactory


def main(request_params, github_token):
    project_folder = Path(request_params.parameters.project_folder)
    project_folder.mkdir(parents=True, exist_ok=True)

    repository_handler = \
        RepositoryHandlerFactory.get_repositories_handler(
                github_token=github_token,
                request_params=request_params
            )

    repository_handler.save_repositories_to_csv(project_folder=project_folder)
    print(repository_handler)


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
