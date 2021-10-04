from abc import ABC, abstractmethod
import sys
import yaml
import re
from pathlib import Path
import datetime
import pandas as pd
import time

import utilities
from github2pandas.utility import Utility


class RequestHandler(ABC):
    def __init__(self, github_token, parameters):
        self.repository_list = []
        self.time_slot_list = []
        self.github_token = github_token
        self.github_user = utilities.get_github_user(github_token)
        self.request = parameters

    @abstractmethod
    def get_repository_list(self):
        pass

    @abstractmethod
    def generate_repository_list(self):
        pass

    def __repr__(self):
        if len(self.repository_list) > 0:
            output = f"{len(self.repository_list)} repositories found: \n"
            for repo in self.repository_list:
                output += f"    {repo.full_name}\n"
        else:
            output = "No repositories found according to request!"
        return output


class RepositoriesByOrganization(RequestHandler):

    MANDATORY_PARAMETERS = ["organization_names"]

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

    MANDATORY_PARAMETERS = ["repos_names"]

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

    MANDATORY_PARAMETERS = ["repo_white_pattern", "repo_black_pattern"]

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
            blacklist_patterns=blacklist_patterns,
        )
        self.repository_list = relevant_repos


class RepositoriesByQuery(RequestHandler):

    MANDATORY_PARAMETERS = [
        "language", "start_date", "end_date", "star_filter"
    ]

    def __init__(self, github_token, request_params):
        super().__init__(github_token, request_params)
        self.generate_time_slot_list()
        self.generate_repository_list()

    def get_repository_list(self):
        return self.repository_list

    def get_time_slot_list(self):
        return self.time_slot_list

    def extract_language(self):
        """
        extract_language()
        Extract and validate the Programming language name provided by the
        user.It will be checked in the  Github known or supported programming
        Languages list. If it exists, it returns the language name otherwise
        it lets the user enter a valid language name.

        Returns
        -------
        str
            Name of Programming language

        Notes
        -----
        Search by language
        : https://docs.github.com/en/github/searching-for-information-on-github/searching-on-github/searching-code#search-by-language

        full list of supported languages in github/linguist repository
        : https://github.com/github/linguist/blob/master/lib/linguist/languages.yml.

        """
        with open("github_language_specification.yml", "r") as f:
            language_specification = yaml.load(f, Loader=yaml.FullLoader)

        github_languages_list = list(language_specification.keys())

        if self.request.parameters.language in github_languages_list:
            return self.request.parameters.language
        else:
            print(
                f"Requested programming language {self.request.parameters.language}"
            )
            print("not found! Please Enter a valid Programming Language")
            print("supported by Github.")
            return None

    def extract_star_filter(self):
        """
        extract_star_filter()

        Extract and validate the number of Stars and the comparison
        symbols(>,<,>=,<=) provided by the user.It accepts only
        a non-negative number or a non-negative number and one
        of these symbols >,<,>= or <=.

        Returns
        -------
        str
            number of Stars or comparision symbols(>,<,>=,<=) and number of
            Stars

        """

        match = re.fullmatch(r"(>|<|=|>=|<=)?\d+",
                             self.request.parameters.star_filter)

        if match is not None:
            return self.request.parameters.star_filter
        else:
            print("Please Enter valid comparison symbol (>,<,>=,<=) and")
            print("non-negative number.")
            return None

    def extract_dates(self):
        """
        extract_dates()

        Extract and validate the search start and end date.
        The start date should not be earlier than the start date of GitHub,
        i.e. 2008-04-10.
        The end date should not be later than the current date.

        Returns
        -------
        str
            Date object in string format

        """
        github_launched_date = datetime.date(2008, 4, 10)
        curr_date = datetime.datetime.today().date()

        start_date = self.request.parameters.start_date
        end_date = self.request.parameters.end_date
        ##Increment the end date to the next date to include it in the search
        #or to get the repositories created on that date
        end_date = end_date + datetime.timedelta(days=1)
        valid_date_configuration = True

        if not (isinstance(start_date, datetime.date)
                and isinstance(end_date, datetime.date)):
            print("The datetime formates are not correct! Please check again.")
            valid_date_configuration = False
        else:
            if (end_date - start_date).days < 1:
                print("Start time greater than end time!")
                valid_date_configuration = False

            if (start_date - github_launched_date).days < 0 or (
                    end_date - curr_date).days > 0:
                print(
                    f"Please enter valid date between {github_launched_date}")
                print(f"and {curr_date}")
                valid_date_configuration = False

        if valid_date_configuration:
            return start_date, end_date
        else:
            return None, None

    def generate_github_query(self, language, star_filter, start_date,
                              end_date):
        """
        generate_github_query(language, star_filter, start_date,end_date)

        generate a search query to  search for repositories on GitHub and 
        narrow the results using the provided parameters as search qualifiers.
        
        Parameters
        ----------
        language : str
            language of the code in the repositories
        star_filter : str
             number of stars the repositories have. Greater than, 
             less than, and range can be specified as extra search qualifiers.
        start_date : str
            search starting date to search repositories created form thise date 
        end_date : [type]
            search end date to search repositories created upto thise date

        Returns
        -------
        str
            search query based onn the provided parameters as search qualifiers
        """
        return ("language:" + language + " " + "created:" +
                start_date.strftime("%Y-%m-%dT%H:%M:%S") + ".." +
                end_date.strftime("%Y-%m-%dT%H:%M:%S") + " " + "stars:" +
                star_filter)

    def generate_short_time_slot(self, date_interval):
        """
        generate_short_time_slot(date_interval)

        Divide the two-day interval into small time segments, such as one day,
        half a day, six, three, or one hour, to further narrow the search 
        period

        Parameters
        ----------
        date_interval :  IntervalIndex
            a time/date interval index from the pandas interval range 
        """

        language = self.extract_language()
        star_filter = self.extract_star_filter()
        github_user = utilities.get_github_user(self.github_token)
        #to hold the small time interval until the suitable time interval is found.
        # Then, when a suitable time slot is found,
        # the time slots are appended to the main time list
        temp_time_slot = []
        periods = [
            2,  # one day interval slots
            4,  # 12 hours interval slots
            8,  # six hours interval slots
            16,  # three hours interval slots
            24,  # one hour interval slots
        ]

        for period in periods:
            print(f"Further dividing interval in {period} intervals.")
            short_time_intervals = pd.interval_range(
                start=pd.Timestamp(date_interval.left),
                end=pd.Timestamp(date_interval.right),
                periods=period)
            #Notification
            print(f" Further Interval -> {short_time_intervals}")
            for short_time_interval in short_time_intervals:

                query = self.generate_github_query(language, star_filter,
                                                   short_time_interval.left,
                                                   short_time_interval.right)

                repositories = github_user.search_repositories(query=query)

                rate_limits = repositories[0]._requester.rate_limiting
                if rate_limits[0] < 10:
                    print(
                        "Running low on search rate ... waiting for one minute to refresh"
                    )
                    time.sleep(60)  # Delay for 1 minute (60 seconds).
                if repositories.totalCount < 1000:
                    temp_time_slot.append(short_time_interval)

                else:
                    print(
                        "found more than 1000 repositories, starting temporal segmentation"
                    )
                    temp_time_slot = []

                    break
            if temp_time_slot:

                for time_slot in temp_time_slot:
                    self.time_slot_list.append(time_slot)
                break

    def generate_time_slot_list(self):
        """
        generate_time_slot_list()

        generates a suitable time slot for the specified search period. 
        The GitHub API allows authenticated users 1,000 requests per hour per
        repository. Therefore, it is necessary to narrow down the search period
        """
        language = self.extract_language()
        star_filter = self.extract_star_filter()
        start_date, end_date = self.extract_dates()
        #Increment the end date to the next date to include it in the search
        #end_date = end_date + datetime.timedelta(days=1)
        if language and star_filter and start_date and end_date:
            github_user = utilities.get_github_user(self.github_token)
            date_interval = pd.interval_range(start=pd.Timestamp(start_date),
                                              end=pd.Timestamp(end_date),
                                              periods=1)

            query = self.generate_github_query(language, star_filter,
                                               date_interval[0].left,
                                               date_interval[0].right)
            repositories = github_user.search_repositories(query=query)
            #Notification
            print(f" First Interval -> {date_interval}")
            if repositories.totalCount < 1000:
                print(
                    "Repositories are less than 1000 for the original search period!"
                )
                # add the star and end date as interval to the time slot list
                self.time_slot_list.append(date_interval[0])

            else:

                #creating two days interval
                two_days_slot = (end_date - start_date).days / 2
                print(f"dividing interval in {two_days_slot} intervals")

                date_intervals = pd.interval_range(
                    start=pd.Timestamp(start_date),
                    end=pd.Timestamp(end_date),
                    periods=two_days_slot)
                #Notification
                print(f" Further Interval -> {date_intervals}")
                for date_interval in date_intervals:

                    query = self.generate_github_query(language, star_filter,
                                                       date_interval.left,
                                                       date_interval.right)
                    repositories = self.github_user.search_repositories(
                        query=query)

                    rate_limits = repositories[0]._requester.rate_limiting
                    if rate_limits[0] < 10:
                        print(
                            "Running low on search rate ... waiting for one minute to refresh"
                        )
                        time.sleep(60)  # Delay for 1 minute (60 seconds).

                    if repositories.totalCount < 1000:

                        self.time_slot_list.append(date_interval)

                    else:
                        print("Repositories are again more than 1000. "
                              "Segmenting the two-day interval further.")
                        # create futher small time slots of the two days interval
                        self.generate_short_time_slot(date_interval)
        else:
            print("error while reading query parameters!")
            print(("Please check the parameters in the config file!"))
            sys.exit()

    def generate_repository_list(self):
        """
        generate_repository_list(self)

        create a list of repositories created in the specified search period.
        

        Returns
        -------
         list
             List of the found repositories
        """
        language = self.extract_language()
        star_filter = self.extract_star_filter()
        start_date, end_date = self.extract_dates()
        time_slot_list = self.time_slot_list
        #Increment the end date to the next date to include it in the search
        #end_date = end_date + datetime.timedelta(days=1)
        if language and star_filter and start_date and end_date:
            github_user = utilities.get_github_user(self.github_token)
            #Notification
            print("Now getting the repositories ....")
            for date_interval in time_slot_list:
                query = self.generate_github_query(language, star_filter,
                                                   date_interval.left,
                                                   date_interval.right)

                repositories = github_user.search_repositories(query=query)

                rate_limits = repositories[0]._requester.rate_limiting
                if rate_limits[0] < 10:
                    print(
                        "Running low on search rate ... waiting for one minute to refresh"
                    )
                    # Delay for 1 minute (60 seconds).
                    time.sleep(60)

                self.repository_list += list(repositories)

                print("{} <-> {}- {} Repositories found ({})".format(
                    date_interval.left.strftime("%Y-%m-%d %H:%M"),
                    date_interval.right.strftime("%Y-%m-%d %H:%M"),
                    len(list(repositories)),
                    repositories[0]._requester.rate_limiting[0],
                ))

        else:
            print("error while reading query parameters!")
            print(("Please check the parameters in the config file!"))
            sys.exit()


class RequestHandlerFactory:
    @staticmethod
    def get_request_handler(github_token, request_params):

        all_handlers = utilities.get_all_subclasses(RequestHandler)

        valid_repo_type = None
        for repo_type in all_handlers:
            if utilities.check_attributes_in_dict(
                    repo_type.MANDATORY_PARAMETERS,
                    request_params.parameters.__dict__,
                    stop_if_fails=False,
            ):
                valid_repo_type = repo_type

        if valid_repo_type:
            return valid_repo_type(github_token, request_params)
        else:
            print("No matching repository handler found! Please check")
            print("spelling!")
            sys.exit()
