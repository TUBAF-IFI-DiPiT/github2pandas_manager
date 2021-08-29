from pathlib import Path
import time

from github2pandas.issues import Issues
from github2pandas.pull_requests import PullRequests
from github2pandas.version import Version
from github2pandas.workflows import Workflows
from github2pandas.repository import Repository
from github2pandas.git_releases import GitReleases

import utilities


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
        pass

    def aggWorkflows(repo, repo_base_folder, github_token=None):
        pass

    def aggGitReleases(repo, repo_base_folder, github_token=None):
        pass

    def check_remaining_github_requests(github_token, min_num=100):
        github_user = utilities.get_github_user(github_token)
        requests_remaning, requests_limit = github_user.rate_limiting
        if ((requests_limit == 5000) & (requests_remaning < min_num)):
            print("Waiting for request limit refresh ...")
            reset_timestamp = github_user.rate_limiting_resettime
            seconds_until_reset = reset_timestamp - time.time()
            sleep_step_width = 1
            sleeping_range = range(int(seconds_until_reset / sleep_step_width))
            for i in utilities.progressbar(sleeping_range, "Sleeping : ", 60):
                time.sleep(sleep_step_width)
            requests_remaning, requests_limit = github_user.rate_limiting
            print("Remaining request limit {0:5d} / {1:5d}".format(
                                                     requests_remaning,
                                                     requests_limit))
        return requests_remaning

    CLASSES = {
        "Repository": aggRepository,
        "Issues": aggIssues,
        "Version": aggVersion,
        "PullRequests": aggPullRequests,
        "Workflows": aggWorkflows,
        "GitReleases": aggGitReleases
    }

    @staticmethod
    def start(github_token, request_handler):
        for content_element in request_handler.request.parameters.content:
            if content_element in Github_data_extractor.CLASSES:
                number_of_repos = len(request_handler.repository_list)
                for index, repo in enumerate(request_handler.repository_list):
                    requests_remaning = Github_data_extractor.check_remaining_github_requests(github_token)
                    print("{0:10} - {1:3} / {2:3} - {3} ({4:4d})".format(
                            content_element,
                            index, number_of_repos, repo.full_name,
                            requests_remaning)
                         )
                    repo_base_folder = Path(
                        request_handler.request.parameters.project_folder,
                        repo.name
                    )
                    repo_base_folder.mkdir(parents=True, exist_ok=True)
                    Github_data_extractor.CLASSES[content_element](repo, repo_base_folder, github_token)
            else:
                print(f"{content_element} not known in github2pandas toolchain!")
                print("Please check spelling")
        return True
