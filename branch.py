__author__ = "Clyde Fondop"
#!/usr/local/bin/python
#
# Create branch
#
from functions import *
from definition import *
import hashlib, json
import config


# Manage creation of the repo
class manageBranch(functionRepo,protectRepo):

    # define attribs for all functions
    def __init__(self):
        functionRepo.__init__(self)
        protectRepo.__init__(self)

    # Get Branch revision number
    def getRevisionNumber(self, branch_name, payload):
        number = 0
        res = self.githubGetRequest(payload)

        if res.status_code in [200,201]:
            json_res = json.loads(res.content)
            number = json_res["commit"]["sha"]

        return number

    # Branch creation
    def createBranch(self,repo, from_branch, to_branch_name):
        branch_full_name = "refs/heads/{}".format(to_branch_name)

        sha1 = self.getRevisionNumber(from_branch, 'repos/{}/{}/branches/{}'.format(config.GITHUB_ORGANISATION,repo,from_branch))

        self.githubPostRequest("repos/{}/{}/git/refs".format(config.GITHUB_ORGANISATION, repo),{"ref":branch_full_name,"sha":sha1}, "branch")
        self.getComonInfoRepo(repo, to_branch_name)
        self.logging()


    # Protect branch
    def protectBranch(self, repo, branch_name, protection):

        self.githubPutRequest("repos/{}/{}/branches/{}/protection".format(config.GITHUB_ORGANISATION, repo, branch_name),protection, "protectBranch")
        self.getComonInfoRepo(repo, branch_name)
        self.logging()


    def getComonInfoRepo(self, repo, branch_name):

        self.status_message["branch_name"] = branch_name
        self.status_message["repo_name"] = repo
        self.status_message["organisation_name"] = config.GITHUB_ORGANISATION

