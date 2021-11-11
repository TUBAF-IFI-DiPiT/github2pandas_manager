from pathlib import Path
import time
import pandas as pd
import numpy as np

from github2pandas.issues import Issues
from github2pandas.pull_requests import PullRequests
from github2pandas.version import Version
from github2pandas.workflows import Workflows
from github2pandas.repository import Repository
from github2pandas.git_releases import GitReleases

from github2pandas_manager import utilities


class Github_data_extractor():

    def aggRepository(repo, repo_base_folder, github_token=None):
        Repository.generate_repository_pandas_table(
            repo=repo,
            data_root_dir=repo_base_folder,
            contributor_companies_included=False
        )

    def aggIssues(repo, repo_base_folder, github_token=None):
        Issues.generate_issue_pandas_tables(
            repo=repo,
            data_root_dir=repo_base_folder,
        )

    def aggVersion(repo, repo_base_folder, github_token=None):
        Version.clone_repository(
            repo=repo,
            data_root_dir=repo_base_folder,
            github_token=github_token
        )
        Version.no_of_proceses = 4
        Version.generate_version_pandas_tables(
            repo=repo,
            data_root_dir=repo_base_folder
        )

    def aggPullRequests(repo, repo_base_folder, github_token=None):
        PullRequests.generate_pull_request_pandas_tables(
            repo=repo,
            data_root_dir=repo_base_folder
        )
        #pass

    def aggWorkflows(repo, repo_base_folder, github_token=None):
        Workflows.generate_workflow_pandas_tables(
            repo=repo,
            data_root_dir=repo_base_folder
        )
        #pass

    def aggGitReleases(repo, repo_base_folder, github_token=None):
        GitReleases.generate_git_releases_pandas_tables(
            repo=repo,
            data_root_dir=repo_base_folder           
        )
        #pass

    def aggUsers(repo, repo_base_folder, github_token=None):
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
        status = pd.DataFrame()
        repo_content = dict.fromkeys(request_handler.request.parameters.content, np.nan)
        for index, repo in enumerate(request_handler.repository_list):
            repo_content['repo_name'] = repo.full_name
            status = status.append(repo_content, ignore_index=True)
        status.set_index("repo_name", inplace=True)

        for content_element in request_handler.request.parameters.content:
            if content_element in Github_data_extractor.CLASSES:
                number_of_repos = len(request_handler.repository_list)
                for index, repo in enumerate(request_handler.repository_list):
                    requests_remaning = utilities.check_remaining_github_requests(github_token)
                    print("{0:10} - {1:3} / {2:3} - {3} ({4:4d})".format(
                            content_element,
                            index, number_of_repos, repo.full_name,
                            requests_remaning)
                         )
                    repo_base_folder = Path(
                        request_handler.request.parameters.project_folder,
                        repo.full_name.split('/')[0],
                        repo.full_name.split('/')[1],
                    )
                    repo_base_folder.mkdir(parents=True, exist_ok=True)
                    Github_data_extractor.CLASSES[content_element](repo, repo_base_folder, github_token)
                    status.loc[repo.full_name, content_element] = pd.Timestamp.now()
            else:
                print(f"{content_element} not known in github2pandas toolchain!")
                print("Please check spelling")
                
        output_path = Path(request_handler.request.parameters.project_folder, output_file_name)
        file = open(output_path, 'w+', newline='')
        status.to_csv(file)
        return True