from abc import ABC, abstractmethod
import yaml

import utilities


class RequestDefinition(ABC):

    MANDATORY_PARAMETER = [
        "project_folder",
        "project_name",
        "content"
    ]

    def __init__(self, filename):
        self.parameters = {}
        self.filename = filename

    def check_mandatory_attributes(self, mandatory_list, parameter_dict):
        return utilities.check_attributes_in_dict(mandatory_list,
                                                  parameter_dict)

    @abstractmethod
    def parse_config_file(self):
        pass


class YAML_RequestDefinition(RequestDefinition):
    def __init__(self, yml_filename):
        super().__init__(yml_filename)
        self.parse_config_file()

    def parse_config_file(self):
        with open(self.filename, "r") as f:
            parameter = yaml.load(f, Loader=yaml.FullLoader)

        self.check_mandatory_attributes(RequestDefinition.MANDATORY_PARAMETER,
                                        parameter)

        # Append project name to folder
        # This structures the folder and avoids redundant inputs in yml config files
        parameter["project_folder"] = parameter["project_folder"] + parameter["project_name"]

        self.parameters = utilities.obj_to_dic(parameter, "Parameter")

    def __repr__(self):
        output = f"{self.filename} \n --------------------------\n"
        output += f"{self.parameters.project_name}"
        output += f"-> Store"
        output += f"{self.parameters.content} to {self.parameters.project_folder}"
        return output


class JSON_RequestDefinition(RequestDefinition):
    def __init__(self, json_filename):
        super().__init__(json_filename)
        self.parse_config_file(json_filename)

    def parse_config_file(self):
        pass
