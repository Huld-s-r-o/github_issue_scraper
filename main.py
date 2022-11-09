from base64 import encode
from datetime import datetime
from datetime import timedelta
from os import path


import urllib.request
import urllib.parse
import json
import csv

def date_fnc(hours_shift):
    '''
    Date function return date object shifted about
    hours_shift param
    '''
    now_t = datetime.now()
    delta_h = timedelta(hours=hours_shift)
    new_time = now_t + delta_h
    return new_time


def t_printer(dt_obj):
    print(f"Current time is: {dt_obj}")


class GithubRepo():
    '''
    Class representing Github repository and wrappers
    on basic Github API.
    '''
    api_repo_url = "https://api.github.com/repos/"

    def __init__(self, owner, repo):
        self.owner = owner
        self.repo_name = repo

    def get_repo_url(self):
        return f"{self.api_repo_url}{self.owner}/{self.repo_name}"

    def get_access_token(self):
        token = ""
        with open("access_token.priv",'r') as f:
            token = f.read().strip()
        return token

    def __str__(self):
        return f"Github repository of OWNER: {self.owner}, REPO_NAME:{self.repo_name}"

    def download_issues_all(self):
        
        last_page = 1
        url_query = [('per_page',50)]
        encoded_query = urllib.parse.urlencode(url_query)
        url = f"{self.get_repo_url()}/issues?"
        access_token = self.get_access_token()
        request_obj = urllib.request.Request(url=url+encoded_query,headers={'Authorization' : f'token {access_token}'})

        with urllib.request.urlopen(request_obj) as w:
             print(f"{w.url} => response status: {w.status}, {w.reason} ")
             print(f"{w.getheaders()}")
             link_header = w.getheader('Link').split(',')
             last_only = [ item for item in link_header if item.find('rel="last"') > 0]
             clean_url_last=last_only[0].split(';')[0].strip().replace('<','').replace('>','')
             parsed_url = urllib.parse.urlparse(clean_url_last)
             dict_qp = urllib.parse.parse_qs(parsed_url.query)
             last_page = int(dict_qp.get('page',1)[0])
             print(f"Last page: {last_page}")
        
        resp_data = []
        for pp in range(1,last_page + 1):            
            encoded_query = urllib.parse.urlencode([*url_query,('page',pp)])
            request_obj = urllib.request.Request(url=url+encoded_query,headers={'Authorization' : f'token {access_token}'})
            print(f"Querying page:{pp}, {request_obj.full_url} ")

            with urllib.request.urlopen(request_obj) as w:
                json_response = json.loads(w.read().decode('utf-8'))
                resp_data.extend(json_response)
        self.issues_all = resp_data

    def get_issues_only(self):
        if not(hasattr(self,'issues_all')):
            self.download_issues_all()    
        
        return list(filter(lambda x: not( 'pull_request' in x),self.issues_all))
    
   
    def get_transformed_issues(self,trans_fnc):
        transformed = list(map( trans_fnc, self.get_issues_only()))
        
        return transformed

def make_path(filename):
    out_dir="outputs"
    return path.join(out_dir,filename)


def save_csv(filename, data_dict):
    
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
    with open(make_path(filename),'w',encoding='utf-8') as f:
        json.dump(data_dict, f)
    print(f"Saved {len(data_dict)} issues into: {filename}")

def transformation_v1(element):
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
    to = date_fnc(0)
    date_frmt = to.strftime("%Y%m%d%H%M%S")
    t_printer(date_frmt)
    repo_amcr = GithubRepo("ARUP-CAS","aiscr-webamcr")
    data = repo_amcr.get_transformed_issues(transformation_v1)
    print(f"Received {len(data)} issues")
    
    save_csv(f"data_{date_frmt}.csv",data)
    save_json(f"data_{date_frmt}.json",data)
    save_json(f"issues-full_{date_frmt}.json",repo_amcr.get_issues_only())

