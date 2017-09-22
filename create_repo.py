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
import uuid
import config

# return repository and team configurations
def getMandatoryParamerters(param):
    env_repo = env_team = {}
    env_repo = {"name": param[0],"description":param[1],"private":param[2],"team_id":param[3]}
    env_team = {"teams_read": param[4], "teams_write": param[5], "teams_admin":"devOps"}

    return env_repo, env_team

# Return ssh key parameters
def getOpionnalParamerters(param):
    env_key = {}
    env_key = {"ssh_title":param[6],"ssh_title":param[7]}

    return env_key

# Get the context of each repo
def createRepository(params, user, channel):
    ENV_KEY = ""
    message = {}
    ENV_REPO, ENV_TEAM = getMandatoryParamerters(params)

    if len(params) < 6:
        ENV_KEY = getOpionnalParamerters(params)


    myManageRepo = manageRepo()
    myProtectRepo = protectRepo()
    myManageBranch = manageBranch()
    myfunctionRepo = functionRepo()
    myManagePubkey = managePubkey()

    myfunctionRepo.slack_user = user
    myfunctionRepo.slack_channel = channel

    myManageBranch.devteams = ENV_TEAM["teams_write"]
    myManageBranch.adminteams = ENV_TEAM["teams_admin"]

    # get Team ID
    teamID = myfunctionRepo.getTeamID(ENV_REPO["team_id"])
    ENV_REPO["team_id"] = teamID

    # Create repository
    message = myManageRepo.createRepo(ENV_REPO,user,channel)

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

    return message