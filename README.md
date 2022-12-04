# Scraper of GitHub issues via API

It stores given Github repository into .csv and .json files with transformation, i.e selecting only some details about issue into repository.
Original purpose is to make transition from GitHub into Jira issue easy. However by adding some other transformation functions, the purpose of this scrapper can easily extended.


RUN as 
'''
GITHUB_ADDRESS="https://github.com/<repo_owner>/<repo_name>" docker-compose up --build
'''

or

'''
GITHUB_ADDRESS="https://github.com/<repo_owner>/<repo_name>" docker-compose run api_issues
'''