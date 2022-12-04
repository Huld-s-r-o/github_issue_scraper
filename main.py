from base64 import encode
from datetime import datetime
from datetime import timedelta
from os import path
from os import makedirs
from os import getenv

import re
import urllib.request
import urllib.parse
import json
import csv
import sys

def date_fnc(hours_shift):
    """Date function returning date object shifted about hours_shift arg

    Args:
        hours_shift (int): number of hours for shifting now date

    Returns:
        date: shifted date object
    """
    now_t = datetime.now()
    delta_h = timedelta(hours=hours_shift)
    new_time = now_t + delta_h
    return new_time


def t_printer(dt_obj):
    """Date obj printer

    Args:
        dt_obj (date): date for console print
    """
    print(f"Current time is: {dt_obj}")


class GithubRepo():
    """Class representing Github repo with set of wrappers for GitHub API

    Returns:
        _type_: GithubRepo instance
    """
    
    api_repo_url = "https://api.github.com/repos/"

    def __init__(self, owner, repo):
        """Instantiate Github repository class with owner and repo name

        Args:
            owner (_type_): owner of repository
            repo (_type_): repository name
        """
        self.owner = owner
        self.repo_name = repo

    def get_repo_url(self):
        return f"{self.api_repo_url}{self.owner}/{self.repo_name}"

    def get_access_token(self):
        """Returns access token from ENV variable GITHUB_TOKEN or from pre-defined file "access_token.priv"

        Returns:
            _type_: _description_
        """
        token = ""
        if getenv("GITHUB_TOKEN") is None:
            with open("access_token.priv",'r') as f:
                token = f.read().strip()
        else:
            token = getenv("GITHUB_TOKEN").strip()
        
        return token

    def __str__(self):
        """String representation of GithubRepo class

        Returns:
            _type_: string with owner and repository name for given instance.
        """
        return f"Github repository of OWNER: {self.owner}, REPO_NAME:{self.repo_name}"

    def download_issues_all(self):
        """Downloads all issues from Github and store them as list of dictionaries
        """
        last_page = 1
        url_query = [('per_page',50)]
        encoded_query = urllib.parse.urlencode(url_query)
        url = f"{self.get_repo_url()}/issues?"
        access_token = self.get_access_token()
        request_obj = urllib.request.Request(url=url+encoded_query,headers={'Authorization' : f'token {access_token}'})

        with urllib.request.urlopen(request_obj) as w:
            #Check whether there are multiple pages with issues
             print(f"{w.url} => response status: {w.status}, {w.reason} ")
             print(f"{w.getheaders()}")
             link_header_all = w.getheader('Link')
             last_page = 1
             if link_header_all is not None:
                link_header = link_header_all.split(',')
                last_only = [ item for item in link_header if item.find('rel="last"') > 0]
                clean_url_last=last_only[0].split(';')[0].strip().replace('<','').replace('>','')
                parsed_url = urllib.parse.urlparse(clean_url_last)
                dict_qp = urllib.parse.parse_qs(parsed_url.query)
                last_page = int(dict_qp.get('page',1)[0])
            
             print(f"Last page: {last_page}")
        
        resp_data = []
        for pp in range(1,last_page + 1):
            #Loop through pages with issues            
            encoded_query = urllib.parse.urlencode([*url_query,('page',pp)])
            request_obj = urllib.request.Request(url=url+encoded_query,headers={'Authorization' : f'token {access_token}'})
            print(f"Querying page:{pp}, {request_obj.full_url} ")

            with urllib.request.urlopen(request_obj) as w:
                json_response = json.loads(w.read().decode('utf-8'))
                resp_data.extend(json_response)
        self.issues_all = resp_data

    def get_issues_only(self):
        """Getter for issues from given Github repository ommitting pull requests (treated by Github also as an issue)

        Returns:
            list: list issues of in the repository
        """
        if not(hasattr(self,'issues_all')):
            self.download_issues_all()    
        
        return list(filter(lambda x: not( 'pull_request' in x),self.issues_all))
    
   
    def get_transformed_issues(self,trans_fnc):
        """Transformation of issue details according to provided function.

        Args:
            trans_fnc (fnc): function transforming issue details into desired output (i.e. stripping unwanted info and changing structure optimal for further processing)

        Returns:
            list: list of transformed issues 
        """
        transformed = list(map( trans_fnc, self.get_issues_only()))
        
        return transformed

def make_path(filename):
    """wrapper for making output folder in the current dir and return the path appended by given filename

    Args:
        filename (string): filename to append to output path

    Returns:
        string: complete path of file on output
    """
    out_dir="outputs"
    makedirs(out_dir,exist_ok=True)
    return path.join(out_dir,filename)


def save_csv(filename, data_dict):
    """Save data into given file formatted as csv

    Args:
        filename (_type_): filename of output
        data_dict (_type_): data as dictionary
    """
    with open(make_path(filename),'w',encoding='utf-8', newline='') as f:
        wo = csv.writer(f, quoting=csv.QUOTE_ALL)
        count = 0
        for item in data_dict:
            if count == 0:
                header = item.keys()
                wo.writerow(header)
                count += 1
            wo.writerow(item.values())
    print(f"Saved {len(data_dict)} issues into: {filename}")


def save_json(filename, data_dict):
    """Save data into given file formatted as json

    Args:
        filename (_type_): filename of output
        data_dict (_type_): data as dictionary
    """
    with open(make_path(filename),'w',encoding='utf-8') as f:
        json.dump(data_dict, f)
    print(f"Saved {len(data_dict)} issues into: {filename}")

def transformation_v1(element):
    """Concrete transformation of issues into a structure where only:
       - number
       - title
       - n-comments
       - body of issues as text
       - updated
       - created
       - state 
       - labels
       - milestone title
       - html url of issue
       - url of issue
     are kept for output.



    Args:
        element (dict): single issue with all details as got from GitHub API

    Returns:
        dict: transformed issue
    """
    return {
        'number' : element ['number'], 
        'title' : element['title'],
         "n_comments": element['comments'],
        "body": element['body'],
        "updated_at": element['updated_at'],
        "created_at": element['created_at'],
        "state": element['state'],
        "labels": ','.join(map(lambda x: x['name'],element['labels'])),
        "milestone_title": element.get('milestone').get('title') if element.get('milestone',False) else "",
        "html_url": element['html_url'],
        "url": element['url']
        }


if __name__ == "__main__":
    args=sys.argv[1:]
    nargs=len(args)

    repo_owner=""
    repo_name=""

    if nargs >= 1:
        if nargs == 1:
            #Consider 1st command-line argument as github.com repo address, i.e https://github.com/owner/repo-name
            address=sys.argv[1]
            res = re.search('.*(github.com)(.*)', address)
            if res is None:
                #Error if github.com address not found
                print(f"The input argument {sys.argv[1]} isn't github.com address => fix to this format https://github.com/repo_owner/repo_name")
                sys.exit(1)
            repo_details=res.group(2).split("/")
            if len(repo_details) != 3 or repo_details[2] == '':
                #Error if github.com address doesn't contain repo_owner and repo_name separated by /
                print(f"Input address has to be in this format => https://github.com/repo_owner/repo_name")
                sys.exit(1)
            repo_owner=repo_details[1]
            repo_name=repo_details[2]
        else:
            #Consider 1st, 2nd command-line argument as owner and repository name on GitHub.com
            repo_owner=sys.argv[1]
            repo_name=sys.argv[2]

    print(f"Repo-owner: {repo_owner}, Repo-name: {repo_name}")
    if repo_owner == "" and repo_name == "":
        print(f"Repository details not obtained => Exiting")
        sys.exit(1)
    
    to = date_fnc(0)
    date_frmt = to.strftime("%Y%m%d%H%M%S")
    t_printer(date_frmt)
    repo_amcr = GithubRepo(repo_owner,repo_name)
    data = repo_amcr.get_transformed_issues(transformation_v1)
    print(f"Received {len(data)} issues")
    
    save_csv(f"data_{date_frmt}.csv",data)
    save_json(f"data_{date_frmt}.json",data)
    save_json(f"issues-full_{date_frmt}.json",repo_amcr.get_issues_only())

