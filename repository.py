__author__ = "Clyde Fondop"
#!/usr/local/bin/python
#
# Creation for the repository
#
from functions import *
from definition import *
import uuid

# Manage creation of the repo
class manageRepo(functionRepo,protectRepo):

    # define attribs for all functions
    def __init__(self):
        functionRepo.__init__(self)
        protectRepo.__init__(self)

    # Create repository
    def createRepo(self, data, user, channel):

        # get secure configuration from definition script
        data.update(self.getRepoCustomParam())

        self.githubPostRequest("orgs/{}/repos".format(config.GITHUB_ORGANISATION),data,"repository")
        self.getComonInfoRepo(data["name"])

        if self.status_message["http_status"] in [200,201]:
            self.status_message["uid_repo"] = uuid.uuid4()
        self.status_message["slack_user"] = user
        self.status_message["slack_channel"] = channel
        self.logging()
        if self.status_message["http_status"] in [200,201]:
            del self.status_message["uid_repo"]

        return self.status_message

    # affect team to repository
    def affectTeam(self, repo, teams, permission):

        for data in teams.split(","):
            team_id = self.getTeamID(data)

            self.githubPutRequest("teams/{}/repos/{}/{}".format(team_id, config.GITHUB_ORGANISATION, repo), {"permission":permission}, "protect_repo")

        self.status_message["requested_permission"] = permission
        self.status_message["requested_team"] = teams
        self.status_message["team_id"] = team_id
        self.getComonInfoRepo(repo)

        self.logging()
        del self.status_message["team_id"]

    # Get common repository informations
    def getComonInfoRepo(self, repo):

        self.status_message["organisation_name"] = config.GITHUB_ORGANISATION
        self.status_message["repo_name"] = repo



