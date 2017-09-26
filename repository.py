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
        self.message_repo = ""

    # Create repository
    def createRepo(self, data, channel, slack_requestor, slack_approver):

        # get secure configuration from definition script
        data.update(self.getRepoCustomParam())

        self.githubPostRequest("orgs/{}/repos".format(config.GITHUB_ORGANISATION),data,"repository")
        self.getComonInfoRepo(data["name"])

        if self.status_message["http_status"] in [200,201]:
            self.status_message["uid_repo"] = uuid.uuid4()
        self.status_message["slack_requestor"] = slack_requestor
        self.status_message["slack_approver"] = slack_approver
        self.status_message["slack_channel"] = channel
        self.message_repo = self.status_message["message"]
        # information to send to slack
        self.slack_info = self.status_message
        self.logging()


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

    # Return information for slack user
    def sendSlackInfo(self):
        str_slack_info = "Action: Repository creation\nRepository Name: {}\nStatus: {}\nRequestor: {} \nApprover: {} \n"\
            .format(self.status_message["repo_name"],self.message_repo,self.status_message["slack_requestor"],self.status_message["slack_approver"],self.status_message["slack_approver"])

        return str_slack_info