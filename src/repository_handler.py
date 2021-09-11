from abc import ABC, abstractmethod
import sys
import yaml
import re
from pathlib import Path
import datetime

import utilities
from github2pandas.utility import Utility


class RequestHandler(ABC):
    def __init__(self, github_token, parameters):
        self.repository_list = []
        self.github_token = github_token
        self.github_user = utilities.get_github_user(github_token)
        self.request = parameters

    @abstractmethod
    def get_repository_list(self): pass

    @abstractmethod
    def generate_repository_list(self): pass

    def __repr__(self):
        if len(self.repository_list) > 0:
            output = f"{len(self.repository_list)} repositories found: \n"
            for repo in self.repository_list:
                output += f"    {repo.full_name}\n"
        else:
            output = "No repositories found according to request!"
        return output
    

class RepositoriesByOrganization(RequestHandler):

    MANDATORY_PARAMETERS = [
        "organization_names"
    ]

    def __init__(self, github_token, request_params):
        super().__init__(github_token, request_params)
        self.generate_repository_list()

    def get_repository_list(self):
        return self.repository_list

    def generate_repository_list(self):
        relevant_repos = []
        github_user = utilities.get_github_user(self.github_token)
        for org_name in self.request.parameters.organization_names:
            org = github_user.get_organization(org_name)
            for repo in org.get_repos():
                relevant_repos.append(repo)
        self.repository_list = relevant_repos


class RepositoriesByRepoNames(RequestHandler):

    MANDATORY_PARAMETERS = [
        "repos_names"
    ]

    def __init__(self, github_token, request_params):
        super().__init__(github_token, request_params)
        self.generate_repository_list()

    def get_repository_list(self):
        return self.repository_list

    def generate_repository_list(self):
        relevant_repos = []
        repo_name_list = self.request.parameters.repos_names
        github_user = utilities.get_github_user(self.github_token)
        for repo_name in repo_name_list:
            try:
                repo = github_user.get_repo(repo_name)
                relevant_repos.append(repo)
            except:
                print(f"No repo found related to {repo_name}!")
        self.repository_list = relevant_repos


class RepositoriesByRepoNamePattern(RequestHandler):

    MANDATORY_PARAMETERS = [
        "repo_white_pattern",
        "repo_black_pattern"
    ]

    def __init__(self, github_token, request_params):
        super().__init__(github_token, request_params)
        self.generate_repository_list()

    def get_repository_list(self):
        return self.repository_list

    def generate_repository_list(self):
        whitelist_patterns = self.request.parameters.repo_white_pattern
        blacklist_patterns = self.request.parameters.repo_black_pattern
        relevant_repos = Utility.get_repos(
                              token=self.github_token,
                              data_root_dir=self.request.parameters.project_folder,
                              whitelist_patterns=whitelist_patterns,
                              blacklist_patterns=blacklist_patterns)
        self.repository_list = relevant_repos


class RepositoriesByQuery(RequestHandler):

    MANDATORY_PARAMETERS = [
        "language",
        "start_date",
        "end_date",
        "star_filter"
    ]

    def __init__(self, github_token, request_params):
        super().__init__(github_token, request_params)
        self.generate_repository_list()

    def get_repository_list(self):
        return self.repository_list

    def extract_language(self):
        with open("github_language_specification.yml", "r") as f:
            language_specification = yaml.load(f, Loader=yaml.FullLoader)

        github_languages_list = list(language_specification.keys())

        if self.request.parameters.language in github_languages_list:
            return self.request.parameters.language
        else:
            print(f"Requested programming language {self.request.parameters.language}")
            print("not found! Please Enter a valid Programming Language")
            print("supported by Github.")
            return None

    def extract_star_filter(self):
        match = re.fullmatch(r'(>|<|=|>=|<=)?\d+',
                             self.request.parameters.star_filter)

        if match is not None:
            return self.request.parameters.star_filter
        else:
            print("Please Enter valid comparison symbol (>,<,>=,<=) and")
            print("non-negative number.")
            return None

    def extract_dates(self):
        github_launched_date = datetime.date(2008, 4, 10)
        curr_date = datetime.datetime.today().date()

        start_date = self.request.parameters.start_date
        end_date = self.request.parameters.end_date
        valid_date_configuration = True

        if not (isinstance(start_date, datetime.date) and
                isinstance(end_date, datetime.date)):
            print("The datetime formates are not correct! Please check again.")
            valid_date_configuration = False
        else:
            if (end_date - start_date).days < 1:
                print("Start time greater than end time!")
                valid_date_configuration = False

            if ((start_date - github_launched_date).days < 0 or
               (end_date - curr_date).days > 0):
                print(f"Please enter valid date between {github_launched_date}")
                print(f"and {curr_date}")
                valid_date_configuration = False

        if valid_date_configuration:
            return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        else:
            return None, None

    def generate_github_query(self, language, star_filter, start_date,
                              end_date):
        return "language:" + language + " " + \
                "created:" + start_date + ".." + end_date + " " + \
                "stars:" + star_filter

    def generate_large_repository_list(self):
        pass

    def generate_repository_list(self):
        language = self.extract_language()
        star_filter = self.extract_star_filter()
        start_date, end_date = self.extract_dates()

        if language and star_filter and start_date and end_date:
            query = self.generate_github_query(language, star_filter,
                                               start_date, end_date)
            github_user = utilities.get_github_user(self.github_token)
            repositories = github_user.search_repositories(query=query)
            if repositories.totalCount > 1000:
                self.generate_large_repository_list()
            self.repository_list = list(repositories)
        else:
            print("Error while reading query parameters!")


class RequestHandlerFactory():

    @staticmethod
    def get_request_handler(github_token, request_params):

        all_handlers = utilities.get_all_subclasses(RequestHandler)

        valid_repo_type = None
        for repo_type in all_handlers:
            if utilities.check_attributes_in_dict(
                     repo_type.MANDATORY_PARAMETERS,
                     request_params.parameters.__dict__,
                     stop_if_fails=False):
                valid_repo_type = repo_type

        if valid_repo_type:
            return valid_repo_type(github_token, request_params)
        else:
            print("No matching repository handler found! Please check")
            print("spelling!")
            sys.exit()
