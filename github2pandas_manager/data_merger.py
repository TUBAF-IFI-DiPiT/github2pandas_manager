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
from github2pandas.core import Core

from github2pandas_manager import utilities

class Github_data_merger():

    def merge_pandas_tables(request_handler, project_base_folder, content):
        print(content, " - results stored in:")
        for merge_fct in Github_data_merger.CLASSES[content]:
            df = pd.DataFrame()
            for index, repo in enumerate(request_handler.repository_list):
                repo_base_folder = Path(
                    request_handler.request.parameters.project_folder,
                    repo.full_name.split('/')[0],
                    repo.full_name.split('/')[1],
                )
                repo_df = merge_fct(repo_base_folder, repo.name)
                df = pd.concat([df, repo_df], axis=0)
                    
            file_name = merge_fct.__name__.split('_')[1]
            csv_output_path = Path(project_base_folder, 
                                   file_name + '.csv')
            print("    " + str(csv_output_path))
            # replace new lines in commit messages
            df = df.replace(r'\n',' ', regex=True) 
            df.to_csv(csv_output_path, index=False)
            output_path = Path(project_base_folder, file_name + '.p')
            with open(output_path, "wb") as f:
                pickle.dump(df, f)

    def get_Repositories(repo_base_folder, repo_name):
        data_dir = Path(repo_base_folder, Repository.Files.DATA_DIR)
        df = Core.get_pandas_data_frame(data_dir, Repository.Files.REPOSITORY)
        return df

    def get_Issues(repo_base_folder, repo_name):
        data_dir = Path(repo_base_folder, Issues.Files.DATA_DIR)
        df = Core.get_pandas_data_frame(data_dir, Issues.Files.ISSUES)
        df['repo_name'] = repo_name
        return df

    def get_IssueComments(repo_base_folder, repo_name):
        data_dir = Path(repo_base_folder, Issues.Files.DATA_DIR)
        df = Core.get_pandas_data_frame(data_dir, Issues.Files.COMMENTS)
        df['repo_name'] = repo_name
        return df

    def get_IssueEvents(repo_base_folder, repo_name):
        data_dir = Path(repo_base_folder, Issues.Files.DATA_DIR)
        df = Core.get_pandas_data_frame(data_dir, Issues.Files.EVENTS)
        df['repo_name'] = repo_name
        return df

    def get_IssueReactions(repo_base_folder, repo_name):
        data_dir = Path(repo_base_folder, Issues.Files.DATA_DIR)
        df = Core.get_pandas_data_frame(data_dir, Issues.Files.ISSUES_REACTIONS)
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
        data_dir = Path(repo_base_folder, PullRequests.Files.DATA_DIR)
        df = Core.get_pandas_data_frame(data_dir, PullRequests.Files.PULL_REQUESTS)
        df['repo_name'] = repo_name
        return df

    def get_PullRequestReviews(repo_base_folder, repo_name):
        data_dir = Path(repo_base_folder, PullRequests.Files.DATA_DIR)
        df = Core.get_pandas_data_frame(data_dir, PullRequests.Files.REVIEWS)
        df['repo_name'] = repo_name
        return df

    def get_PullRequestReviewComments(repo_base_folder, repo_name):
        data_dir = Path(repo_base_folder, PullRequests.Files.DATA_DIR)
        df = Core.get_pandas_data_frame(data_dir, PullRequests.Files.REVIEWS_COMMENTS)
        df['repo_name'] = repo_name
        return df

    def get_PullRequestReactions(repo_base_folder, repo_name):
        data_dir = Path(repo_base_folder, PullRequests.Files.DATA_DIR)
        df = Core.get_pandas_data_frame(data_dir, PullRequests.Files.PULL_REQUESTS_REACTIONS)
        df['repo_name'] = repo_name
        return df

    def get_Workflows(repo_base_folder, repo_name):
        data_dir = Path(repo_base_folder, Workflows.Files.DATA_DIR)
        df = Core.get_pandas_data_frame(data_dir, Workflows.Files.WORKFLOWS)
        df['repo_name'] = repo_name
        return df

    def get_WorkflowRuns(repo_base_folder, repo_name):
        data_dir = Path(repo_base_folder, Workflows.Files.DATA_DIR)
        df = Core.get_pandas_data_frame(data_dir, Workflows.Files.RUNS)
        df['repo_name'] = repo_name
        return df

    def get_GitReleases(repo_base_folder, repo_name):
        data_dir = Path(repo_base_folder, GitReleases.Files.DATA_DIR)
        df = Core.get_pandas_data_frame(data_dir, GitReleases.Files.GIT_RELEASES)
        df['repo_name'] = repo_name
        return df

    CLASSES = {
        "Repository": [get_Repositories],
        "Issues": [get_Issues, get_IssueComments, get_IssueEvents, get_IssueReactions],
        "Version": [get_Edits, get_Commits],
        "PullRequests": [get_PullRequests, get_PullRequestReviews,
                         get_PullRequestReviewComments, get_PullRequestReactions],
        "Workflows": [get_Workflows, get_WorkflowRuns],
        "GitReleases": [get_GitReleases],
        "Users": [get_Users]
    }
    
    RAW_DATA_FOLDER = "."

    @staticmethod
    def merge(request_handler):
        for content_element in request_handler.request.parameters.content:
            print("\n\n")
            if content_element in Github_data_merger.CLASSES:
                project_base_folder = Path(
                    request_handler.request.parameters.project_folder,
                    Github_data_merger.RAW_DATA_FOLDER,
                )
                project_base_folder.mkdir(parents=True, exist_ok=True)
                Github_data_merger.merge_pandas_tables(request_handler,
                                                       project_base_folder,
                                                       content_element)
