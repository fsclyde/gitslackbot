__author__ = "Clyde Fondop"
#!/usr/local/bin/python
#
# Add permission and access to repo and branch
#
from functions import *

# Manage creation of the repo
class protectRepo(functionRepo):

    # define attribs for all functions
    def __init__(self):
        self.message = ""
        functionRepo.__init__(self)

    # Repo creation custom parameters
    def getRepoCustomParam(self):
        param = {
            "has_issues":True,
            "has_projects":True,
            "has_wiki":True,
            "auto_init":False,
            "auto_init":True,
            "allow_merge_commit":True,
            "allow_squash_merge":True,
            "allow_rebase_merge":True
        }

        return param

    # Branch protection definition
    def getBranchCustomProtection(self, pusher, reviewer):

        param = {
          "required_status_checks": {
            "strict": False,
            "include_admins": True,
            "contexts": []
          },
          "required_pull_request_reviews": {
              "dismissal_restrictions": {
                "users": [
                "{}".format(config.GITHUB_ORGANISATION)
              ],
              "teams": [
                "{}".format(reviewer)
              ]
            },
            "dismiss_stale_reviews": False,
            "require_code_owner_reviews": True
          },
          "enforce_admins": True,
          "restrictions": {
            "users": [
              "{}".format(config.GITHUB_ORGANISATION)
            ],
            "teams": [
              "{}".format(pusher)
            ]
          }
        }

        return param

    # Deploy key parameters
    def sshKeyConfig(self):

        param = {
          "read_only": True
        }

        return param



