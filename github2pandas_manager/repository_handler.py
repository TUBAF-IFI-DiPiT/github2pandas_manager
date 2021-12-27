from abc import ABC, abstractmethod
import sys
import yaml
import re
from pathlib import Path
import datetime
import pandas as pd
import time
import math

from github2pandas_manager import utilities
from github2pandas.utility import Utility


class RequestHandler(ABC):
    """Abstract Class to create a Request Hander.
    
    Methods
    -------
    get_repository_list():
        Abstract Method to get a List of repositories.
    generate_repository_list():
        Abstract Method to generate List of repositories.
    """
    
    
    def __init__(self, github_token, parameters):
        """Constractor of RequestHandler Class.

        Parameters
        ----------
        github_token : str
            GitHub API Access Authentication token.
        parameters : str
            Parameters requerd for the search the repositories.

        Attributes
        ----------
        github_token : str
            GitHub API Access Authentication token.
        request : str
           Parameters requerd to search for repositories.
        repository_list : List (str)
            List for the repositories
        time_slot_list : List (str)
            List for the timeslots
        github_user : GitHub User
            Authenticated GitHub User.

        """

        self.repository_list = []
        self.time_slot_list = []
        self.github_token = github_token
        self.github_user = utilities.get_github_user(github_token)
        self.request = parameters

    @abstractmethod
    def get_repository_list(self):
        """Abstract method that gets a list of all repositories."""

        pass

    @abstractmethod
    def generate_repository_list(self):
        """
        Abstract method that generates a list of all repositories found 
        from the search.
        """

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
    """Class to get repositories belonging to an organization.

    Parameters
    ----------
    RequestHandler : RequestHandler
        object of RequestHandler. 

    Attributes
    ----------
    MANDATORY_PARAMETERS : List
        List of organization's name.

    Methods
    -------
    get_repository_list():
        List of repositories belonging to an organization.
    generate_repository_list():
        Retrieve all repositories belonging to an organization.

    """

    MANDATORY_PARAMETERS = ["organization_names"]

    def __init__(self, github_token, request_params):
        """ Constractor of RepositoriesByOrganization Class.

        Parameters
        ----------
        github_token : str
            GitHub API Access Authentication token.
        request_params : str
            Parameters requerd for the search

        """

        super().__init__(github_token, request_params)
        self.generate_repository_list()

    def get_repository_list(self):
        """
        get_repository_list()

        Implements the Abstract Method of the base class to return a list of 
        all repositories belonging to an organization.

        Returns
        -------
        list :
            List of repositories.

        """

        return self.repository_list

    def generate_repository_list(self):
        """
        generate_repository_list()

        Implements the Abstract Method of the base class to Retrieve all 
        repositories belonging to an organization.

        """
        
        relevant_repos = []
        github_user = utilities.get_github_user(self.github_token)
        for org_name in self.request.parameters.organization_names:
            org = github_user.get_organization(org_name)
            for repo in org.get_repos():
                relevant_repos.append(repo)
        self.repository_list = relevant_repos


class RepositoriesByRepoNames(RequestHandler): 
    """Class to get repositories by Name.

    Parameters
    ----------
    RequestHandler : RequestHandler
        object of RequestHandler 

    Attributes
    ----------
    MANDATORY_PARAMETERS : List
        List of repositories's name.

    Methods
    -------
    get_repository_list():
        List of repositories based on repositories' name.
    generate_repository_list():
        Retrieves all repositories based on repositories' name.

    """

    MANDATORY_PARAMETERS = ["repos_names"]

    def __init__(self, github_token, request_params):
        """Constractor of RepositoriesByRepoNames Class.

        Parameters
        ----------
        github_token : str
            GitHub API Access Authentication token.
        request_params : str
            Parameters requerd for the search
        """

        super().__init__(github_token, request_params)
        self.generate_repository_list()

    def get_repository_list(self):
        """
        get_repository_list()

        Implements the Abstract Method of the base class to return a list 
        of all repositories according to the repositories' names.

        Returns
        -------
        list :
            List of repositories.

        """

        return self.repository_list

    def generate_repository_list(self):
        """
        generate_repository_list()

        Implements the Abstract Method of the base class to retrieve all 
        repositories according to the repositories' names.

        """
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
    """Class to get repositories by the Name pattern.

    Parameters
    ----------
    RequestHandler : RequestHandler
        object of RequestHandler. 

    Attributes
    ----------
    MANDATORY_PARAMETERS : List
        List of repository white and black pattern.

    Methods
    -------
    get_repository_list():
        Returns a List of repositories based on the white or black pattern  
        filters.
    generate_repository_list():
        Retrieve all repositories belonging based on the white or black pattern.

    """

    MANDATORY_PARAMETERS = ["repo_white_pattern", "repo_black_pattern"]

    def __init__(self, github_token, request_params):
        """ Constractor of RepositoriesByRepoNamePattern Class.

        Parameters
        ----------
        github_token : str
            GitHub API Access Authentication token.
        request_params : str
            Parameters requerd for the search.

        """
        
        super().__init__(github_token, request_params)
        self.generate_repository_list()

    def get_repository_list(self):
        """
        get_repository_list(self)

        Implements the Abstract Method of the base class to return a list of 
        all repositories based on the white or black pattern.

        Returns
        -------
        list :
            List of repositories.

        """

        return self.repository_list

    def generate_repository_list(self):
        """
        generate_repository_list()

        Implements the Abstract Method of the base class to retrieve all 
        repositories based on the white or black pattern.

        """
        print("###########################################################")
        print(self.github_token)
        print(len(self.github_token))
        print("###########################################################")
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
    """Class to get repositories by the Search query.

    Parameters
    ----------
    RequestHandler : RequestHandler
        object of RequestHandler 

    Attributes
    ----------
    MANDATORY_PARAMETERS : List
        List of search qualifiers and filters.

    Methods
    -------
    get_repository_list():
        Returns a List of repositories based on the search qualifies and 
        filters.
    generate_repository_list():
        Retrieve all repositories repositories based on the search qualifies and 
        filters.
    def get_time_slot_list():
        Returns a List of small timeslots of the search period. 
    extract_language():
        Extract and validate the repository's Programming language.
    extract_star_filter():
        Extracts and validates the number of stars and the comparison symbols.
    extract_dates():
        Extract and validate the search start and end date.
    generate_github_query(language, star_filter, start_date, end_date):
        generates a search query based on the qualifiers and filters.
    generate_short_time_slot(date_interval):
        Divide the Datetime interval into more small time segments.
    generate_time_slot_list():
        generates suitable small Datetime interval timeslots for the search by
        dividing the specified search period.
    generate_repository_list():
        generate a list of repositories for the specified search period.

    """

    MANDATORY_PARAMETERS = [
        "language", "start_date", "end_date", "star_filter"
    ]

    def __init__(self, github_token, request_params):
        """ Constractor of RepositoriesByQuery Class

        Parameters
        ----------
        github_token : str
            GitHub API Access Authentication token.
        request_params : str
            Parameters requerd for the search.

        """

        super().__init__(github_token, request_params)
        self.generate_time_slot_list()
        self.generate_repository_list()

    def get_repository_list(self):
        """
        get_repository_list(self)

        Implements the Abstract Method of the base class to return a list of 
        all repositories based on the search qualifiers and filters.

        Returns
        -------
        list : 
            List of repositories.

        """

        return self.repository_list

    def get_time_slot_list(self):
        """
        get_time_slot_list()

        Returns a list of Datetime interval slots of the specified search period.

        Returns
        -------
        list 
            a list of small Datetime interval timeslots.

        """

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
            Name of Programming language.

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

        Extracts and validates the number of stars and the comparison symbols
        (>,<,>=,<=) if they are specified as additional filters. Only a 
        non-negative number or a non-negative number and one of these 
        comparison symbols (>,<,>= or <= )are allowed.
        Example: star = 5 or =<5  or <=5 or >5 or >=5

        Returns
        -------
        str
            number of Stars with or without comparison symbols(>,<,>=,<=) and 
            number of Stars.

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

    def _generate_short_time_slot(self, date_interval):
        """
        _generate_short_time_slot(date_interval)

        Divide the Datetime interval further into small time segments, such as
        one day,half a day, six, three, or one hour, to further narrow the 
        search period

        Parameters
        ----------
        date_interval :  IntervalIndex
            a time/date interval index from the pandas interval range 

        """

        language = self.extract_language()
        star_filter = self.extract_star_filter()
        github_user = utilities.get_github_user(self.github_token)
        # To hold the short time interval until the suitable time
        # interval is found. Then, when a suitable time slot is found,
        # the time slots are appended to the main timeslots list.
        temp_time_slot = []
        periods = [
            2,  # one day interval slots
            4,  # 12 hours interval slots
            8,  # six hours interval slots
            16,  # three hours interval slots
            24,  # one hour interval slots
        ]

        for period in periods:
            short_time_intervals = pd.interval_range(
                start=pd.Timestamp(date_interval.left),
                end=pd.Timestamp(date_interval.right),
                periods=period)
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
                    # Emptying the temporary timeslot list to regenerate
                    # another suitable shorter time slot.
                    temp_time_slot = []
                    break
            if temp_time_slot:
                self.time_slot_list.extend(temp_time_slot)
                break

    def generate_time_slot_list(self):
        """
        generate_time_slot_list()

        creates suitable small timeslots by splitting the specified search 
        period. The GitHub API allows authenticated users 1,000 repositories 
        per hour and per request for the specified search period. To get all 
        repositories created in a given search period, the search period must 
        be split into small time slots. The number of repositories created in 
        each time slot must be less than 1000, and finally, all repositories 
        from each time slot are aggregated to get all repositories created in 
        the search period.

        """

        language = self.extract_language()
        star_filter = self.extract_star_filter()
        start_date, end_date = self.extract_dates()
        separator_line_count = 55
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
            print("-"*separator_line_count)
            print(f"Original search period: {date_interval[0]}")
            print("-"*separator_line_count)
            if repositories.totalCount < 1000:
                print(
                    "Repositories are less than 1000 for the original search"
                    "period!"
                )
                # add the star and end date as interval to the time slot list
                self.time_slot_list.append(date_interval[0])
                print("-"*separator_line_count)
            else:
                # Create intervals of one up to two-day timespan,
                # depending on the length of the search period.
                interval_count = math.ceil((end_date - start_date).days / 2)
                # Notification
                print("For the original search period, the number of\n"
                    "repositories is more than 1000. Segmenting of\n"
                    "Original search period into shorter search time\n"
                    "slots the is required. Then, this may take between\n"
                    "seconds and minutes depending on the span of the\n"
                    "original search period."

                    )
                print("-"*separator_line_count)
                date_intervals = pd.interval_range(
                    start=pd.Timestamp(start_date),
                    end=pd.Timestamp(end_date),
                    periods=interval_count)
                for index, date_interval in enumerate(date_intervals):
                    # To adjust the index number with the interval count
                    index += 1
                    # Simple progress bar for the interval generating.
                    sys.stdout.write("Please Wait : %s[%s%s] %i/%s\r" %
                                (" ", 
                                "#"*math.ceil((index/interval_count)*100),
                                "."*math.ceil((1-index/interval_count)*100),
                                math.ceil((index/interval_count)*100),"100%"))
                    sys.stdout.flush()
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
                        # If the repositories for the interval are still
                        # more than 1000, then further shorter interval
                        # segmentation of the interval is requerd.
                        self.time_slot_list.append(date_interval)
                    else:
                        self._generate_short_time_slot(date_interval)
                # Notification 
            print("\nDone! A list of suitable time slots has been generated.")
            print("-"*separator_line_count)
        else:
            print("error while reading query parameters!")
            print(("Please check the parameters in the config file!"))
            sys.exit()

    def generate_repository_list(self):
        """
        generate_repository_list(self)

        generates a list of repositories created in the specified search 
        period based on the search criteria and filters.
        
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
    """Class to check the mandatory parameters 

    get_request_handler(github_token, request_params):
        
    """

    @staticmethod
    def get_request_handler(github_token, request_params):
        """ Gets a RequestHandler to search repositories. 

        Parameters
        ----------
        github_token : str
            GitHub API Access Authentication token.
        request_params : str
            Parameters requerd for the search

        Returns
        -------
        RequestHandler: 
            Object of RequestHandler Class or its subclass.

        """

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
