from pathlib import Path
from github import Github
import argparse
import os
import sys
import re
import datetime

def check_file_path(file_path_name):
    if os.path.isfile(file_path_name):
        return file_path_name
    else:
        raise argparse.ArgumentTypeError(f"{file_path_name} is not a valid file")

def get_github_user(github_token):
    git_user = Github(github_token, retry=10, timeout=10, per_page=1000)
    return git_user

def check_attributes_in_dict(mandatory_list, parameter_dict, stop_if_fails = True):
    mandatory = set(mandatory_list)
    existing = set(parameter_dict.keys())
    if not mandatory.issubset(existing):
        if stop_if_fails:
            print(f"Missing parameter {mandatory - existing} in config. Please check the spelling!")
            sys.exit()
        else:
            return False
    return True

def obj_to_dic(d, classname):
    obj = type(classname, (object,), d)
    seqs = tuple, list, set, frozenset
    for i, j in d.items():
        if isinstance(j, dict):
            setattr(obj, i, obj_to_dic(j))
        elif isinstance(j, seqs):
            setattr(obj, i, 
                type(j)(obj_to_dic(sj) if isinstance(sj, dict) else sj for sj in j))
        else:
            setattr(obj, i, j)
    return obj

def get_all_subclasses(python_class):
    python_class.__subclasses__()

    subclasses = set()
    check_these = [python_class]

    while check_these:
        parent = check_these.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                check_these.append(child)

    return sorted(subclasses, key=lambda x: x.__name__)

def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)
    def show(j):
        x = int(size*j/count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
        file.flush()        
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()