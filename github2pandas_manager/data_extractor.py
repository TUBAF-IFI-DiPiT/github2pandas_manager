from pathlib import Path
import time
import pandas as pd
import numpy as np
import logging

from github2pandas.github2pandas import GitHub2Pandas
from github2pandas.issues import Issues
from github2pandas.pull_requests import PullRequests
from github2pandas.version import Version
from github2pandas.workflows import Workflows
from github2pandas.repository import Repository
from github2pandas.git_releases import GitReleases
from github2pandas.core import Core

from github2pandas_manager import utilities

class Github_data_extractor():

    def aggRepository(repo, github2pandas):
        github2pandas.generate_repository_pandas_tables(repo)

    def aggIssues(repo, github2pandas):
        github2pandas.generate_issues_pandas_tables(repo) 

    def aggVersion(repo, github2pandas):
        no_of_proceses = 4
        github2pandas.generate_version_pandas_tables(repo, 
                                                     no_of_proceses)

    def aggPullRequests(repo, github2pandas):
        github2pandas.generate_pull_requests_pandas_tables(repo) 

    def aggWorkflows(repo, github2pandas):
        github2pandas.generate_workflows_pandas_tables(repo) 

    def aggGitReleases(repo, github2pandas):
        github2pandas.generate_git_releases_pandas_tables(repo)

    def aggUsers(repo, github2pandas):
        # Users are automatically extracted by github2pandas
        pass

    CLASSES = {
        "Repository": aggRepository,
        "Issues": aggIssues,
        "Version": aggVersion,
        "PullRequests": aggPullRequests,
        "Workflows": aggWorkflows,
        "GitReleases": aggGitReleases,
        "Users": aggUsers
    }
    
    AGG_HISTORY_FILE = "aggregation_history.csv"

    @staticmethod
    def start(github_token, request_handler,
              output_file_name = AGG_HISTORY_FILE):

        # Prepare data frame for providing aggregation history
        repo_list = []
        for index, repo in enumerate(request_handler.repository_list):
            repo_content = dict.fromkeys(request_handler.request.parameters.content, np.nan)
            repo_content['repo_name'] = repo.full_name
            repo_list.append(repo_content)
        status = pd.DataFrame(repo_list)

        # all classes of aggregation aims
        for content_element in request_handler.request.parameters.content:
            if content_element in Github_data_extractor.CLASSES:
                number_of_repos = len(request_handler.repository_list)
                # all relevant repositories
                for index, repo in enumerate(request_handler.repository_list):
                    requests_remaning = utilities.check_github_requests_limits(github_token)
                    print("{0:10} - {1:3} / {2:3} - {3} ({4:4d})".format(
                            content_element,
                            index, number_of_repos, repo.full_name,
                            requests_remaning)
                         )
                    git_repo_owner = repo.full_name.split('/')[0]
                    git_repo_name = repo.full_name.split('/')[1]
                    base_folder = Path(
                        request_handler.request.parameters.project_folder,
                    )
                    # Provide sub folders for individual organizations
                    repo_base_folder = Path(
                        request_handler.request.parameters.project_folder,
                        git_repo_owner, git_repo_name,
                    )
                    repo_base_folder.mkdir(parents=True, exist_ok=True)
                    # Run extraction
                    github2pandas = GitHub2Pandas(github_token, 
                                                  base_folder, 
                                                  log_level=logging.DEBUG)
                    repo_ = github2pandas.get_repo(git_repo_owner, git_repo_name)
                    Github_data_extractor.CLASSES[content_element](repo_, github2pandas)
                    # Note timestamp 
                    status.loc[status.repo_name == repo.full_name, content_element] = pd.Timestamp.now()
            else:
                print(f"{content_element} not known in github2pandas toolchain!")
                print("Please check spelling")
        
        output_path = Path(request_handler.request.parameters.project_folder, output_file_name)
        file = open(output_path, 'w+', newline='')
        status.to_csv(file)
        return True