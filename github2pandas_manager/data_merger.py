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
from github2pandas.utility import Utility

import utilities


class Github_data_merger():

    def merge_pandas_tables(request_handler, project_base_folder, content):
        for merge_fct in Github_data_merger.CLASSES[content]:
            df = pd.DataFrame()
            for index, repo in enumerate(request_handler.repository_list):
                repo_base_folder = Path(
                    request_handler.request.parameters.project_folder,
                    repo.full_name.split('/')[0],
                    repo.full_name.split('/')[1],
                )
                repo_df = merge_fct(repo_base_folder, repo.name)
                #if df.empty:
                #    df = repo_df
                #else:
                df = pd.concat([df, repo_df], axis=0)
                    
            file_name = merge_fct.__name__.split('_')[1]
            csv_output_path = Path(project_base_folder, 
                                   file_name + '.csv')
            print(csv_output_path)
            # replace new lines in commit messages
            df = df.replace(r'\n',' ', regex=True) 
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

    def get_Users(repo_base_folder, repo_name):
        df = Utility.get_users(repo_base_folder)
        df['repo_name'] = repo_name
        return df

    def get_Branches(repo_base_folder, repo_name):
        pass

    def get_PullRequests(repo_base_folder, repo_name):
        #pass
        df = PullRequests.get_pull_requests(repo_base_folder)
        df['repo_name'] = repo_name
        return df

    def get_Workflows(repo_base_folder, repo_name):
        #pass
        df = Workflows.get_workflows(repo_base_folder)
        df['repo_name'] = repo_name
        return df

    def get_GitReleases(repo_base_folder, repo_name):
        #pass
        df = GitReleases.get_git_releases(repo_base_folder)
        df['repo_name'] = repo_name
        return df

    CLASSES = {
        "Repository": [get_Repositories],
        "Issues": [get_Issues],
        "Version": [get_Edits, get_Commits],
        "PullRequests": [get_PullRequests],
        "Workflows": [get_Workflows],
        "GitReleases": [get_GitReleases],
        "Users": [get_Users]
    }
    
    RAW_DATA_FOLDER = "."

    @staticmethod
    def merge(request_handler):
        for content_element in request_handler.request.parameters.content:
            if content_element in Github_data_merger.CLASSES:
                project_base_folder = Path(
                    request_handler.request.parameters.project_folder,
                    Github_data_merger.RAW_DATA_FOLDER,
                )
                project_base_folder.mkdir(parents=True, exist_ok=True)
                Github_data_merger.merge_pandas_tables(request_handler,
                                                       project_base_folder,
                                                       content_element)
