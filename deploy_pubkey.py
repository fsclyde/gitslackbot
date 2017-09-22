__author__ = "Clyde Fondop"
#!/usr/local/bin/python
#
# Deploy public key for github
#
import datetime, json, string
from functions import *
from definition import *

# Manage the public key
class managePubkey(functionRepo,protectRepo):

    # define attribs for all functions
    def __init__(self):
        self.message = ""
        functionRepo.__init__(self)
        protectRepo.__init__(self)

    # deploy a new public key to github
    def deployKey(self, env_key, repo):

        env_key.update(self.sshKeyConfig())
        self.githubPostRequest("repos/{}/{}/keys".format(config.GITHUB_ORGANISATION,repo),env_key,"deploy_ssh_pubkey")

        self.logging()

