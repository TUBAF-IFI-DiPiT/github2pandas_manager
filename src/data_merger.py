from pathlib import Path
import pandas as pd
import numpy as np
import pickle

from github2pandas.issues import Issues
from github2pandas.pull_requests import PullRequests
from github2pandas.version import Version
from github2pandas.workflows import Workflows
from github2pandas.repository import Repository
from github2pandas.git_releases import GitReleases
import utilities


class Github_data_merger():

    def merge_pandas_tables(request_handler, project_base_folder, content):
        for merge_fct in Github_data_merger.CLASSES[content]:
            df = pd.DataFrame()
            for index, repo in enumerate(request_handler.repository_list):
                repo_base_folder = Path(
                    project_base_folder,
                    repo.full_name.replace('/', '-')
                )
                repo_df = merge_fct(repo_base_folder, repo.name)
                if df.empty:
                    df = repo_df
                else:
                    df = pd.concat([df, repo_df], axis=0)
            file_name = merge_fct.__name__.split('_')[1]
            csv_output_path = Path(project_base_folder, file_name + '.csv')
            # replace new lines in commit messages
            df = df.apply(lambda x : x.replace('\n', '\\n'))
            df.to_csv(csv_output_path, index=False)
            output_path = Path(project_base_folder, file_name + '.p')
            with open(output_path, "wb") as f:
                pickle.dump(df, f)

    def get_Repositories(repo_base_folder, repo_name):
        return Repository.get_repository_keyparameter(repo_base_folder)

    def get_Issues(repo_base_folder, repo_name):
        df = Issues.get_issues(repo_base_folder)
        df['repo_name'] = repo_name
        return df

    def get_Commits(repo_base_folder, repo_name):
        df = Version.get_version(repo_base_folder, filename=Version.VERSION_COMMITS)
        df['repo_name'] = repo_name
        return df

    def get_Edits(repo_base_folder, repo_name):
        df = Version.get_version(repo_base_folder, filename=Version.VERSION_EDITS)
        df['repo_name'] = repo_name
        return df

    def get_Branches(repo_base_folder, repo_name):
        pass

    def get_PullRequests(repo_base_folder):
        pass

    def get_Workflows(repo_base_folder):
        pass

    def get_GitReleases(repo_base_folder):
        pass

    CLASSES = {
        "Repository": [get_Repositories],
        "Issues": [get_Issues],
        "Version": [get_Edits, get_Commits],
        "PullRequests": [get_PullRequests],
        "Workflows": [get_Workflows],
        "GitReleases": [get_GitReleases]
    }
    
    RAW_DATA_FOLDER = "raw_data"

    @staticmethod
    def merge(request_handler):
        for content_element in request_handler.request.parameters.content:
            if content_element in Github_data_merger.CLASSES:
                project_base_folder = Path(
                    request_handler.request.parameters.project_folder,
                    Github_data_merger.RAW_DATA_FOLDER,
                )
                Github_data_merger.merge_pandas_tables(request_handler,
                                                       project_base_folder,
                                                       content_element)
