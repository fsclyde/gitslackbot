__author__ = "Clyde Fondop"
#!/usr/local/bin/python
# title           : AWS Lambda Gihub Enterprise Create repository
# description     : Create automatically GIT repositoies, set branch, permission, groups etc.
#                   AWS Lambda Role Name:
#                   AWS Lambda Arn:
#
# author          : clyde
# date            :
# version         : 0.1
# usage           : python nw-repoautocreate.py
# notes           :
# python_version  : 2.7
# ==============================================================================
#
#
#
# Import the modules needed to run the script.
from repository import *
from branch import *
from definition import *
from functions import *
from deploy_pubkey import *
from slacker import Slacker
import boto3
from boto3.dynamodb.conditions import Key

import uuid
import config

resource = boto3.resource('dynamodb')
slack = Slacker(config.API_TOKEN)
myfunctionRepo = functionRepo()


# return repository and team configurations
def getMandatoryParamerters(param):
    env_repo = env_team = {}
    env_repo = {"name": param["repo_name"],"description":"Git Repository for {} ".format(param["repo_team"]),"private":True,"team_id":myfunctionRepo.getTeamID(param["repo_team"])}
    env_team = {"teams_read": param["repo_teams_read"], "teams_write": param["repo_teams_write"], "teams_admin":"devOps"}

    return env_repo, env_team

# Return ssh key parameters
def getOpionnalParamerters(param):
    env_key = {}
    env_key = {"ssh_title":param["ssh_title"],"ssh_key":param["ssh_key"]}

    return env_key

# Get the context of each repo
def createRepository(event,context):
    ENV_KEY = ""
    test = 0
    message = {}
    try:
        test_key  = event["repo_name"]
    except KeyError:
        message = "Error in the inputs parameters"
        test = 1

    if test == 0:
        params = event
        ENV_REPO, ENV_TEAM = getMandatoryParamerters(params)

        if "ssh_key" in params:
            ENV_KEY = getOpionnalParamerters(params)

        myManageRepo = manageRepo()
        myProtectRepo = protectRepo()
        myManageBranch = manageBranch()
        myManagePubkey = managePubkey()

        myfunctionRepo.slack_channel = params["channel"]
        myManageBranch.devteams = ENV_TEAM["teams_write"]
        myManageBranch.adminteams = ENV_TEAM["teams_admin"]

        # Create repository
        message = myManageRepo.createRepo(ENV_REPO,myfunctionRepo.slack_channel, params["approver"], params["requestor"])

        # Affect team to the repository
        myManageRepo.affectTeam(ENV_REPO["name"],ENV_TEAM["teams_read"], "pull") # READ
        myManageRepo.affectTeam(ENV_REPO["name"],ENV_TEAM["teams_write"], "push") # WRITE
        myManageRepo.affectTeam(ENV_REPO["name"],ENV_TEAM["teams_admin"], "admin") # ADMIN

        # Protect branch MASTER
        myManageBranch.protectBranch(ENV_REPO["name"], "master",myProtectRepo.getBranchCustomProtection(pusher=ENV_TEAM["teams_write"], reviewer=ENV_TEAM["teams_admin"]))

        # create Branch DEVELOP
        myManageBranch.createBranch(ENV_REPO["name"],"master","develop")

        # Protect branch DEVELOP
        myManageBranch.protectBranch(ENV_REPO["name"],"develop",myProtectRepo.getBranchCustomProtection(pusher=ENV_TEAM["teams_write"], reviewer=ENV_TEAM["teams_admin"]))

        if ENV_KEY:
            # deploy the ssh public key for the repository
            myManagePubkey.deployKey(ENV_KEY,ENV_REPO["name"])

        # Send information to Slack channel
        slack.chat.post_message(config.SLACK_CHANNEL, text=myManageRepo.sendSlackInfo(), username="slackbot")

        table = resource.Table(config.TABLE)
        table.delete_item(
            Key={
                'message_id':params["message_id"]
            }
        )

    return message


# if __name__ == "__main__":
#     event = context = {}
#     event = {
#             "repo_name":"nw-test",
#             "repo_description":"tototo",
#             "repo_team":"read-only",
#             "repo_teams_read":"devOps",
#             "repo_teams_write":"read-only",
#             "approver":"ok",
#             "requestor":"test",
#             "channel":"ok",
#             "ssh_title": "test",
#             "ssh_key": "test"
#         }
#
#     createRepository(event)