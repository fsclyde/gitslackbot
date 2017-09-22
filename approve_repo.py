import boto3
import json
import logging
import os
from functions import *
from base64 import b64decode
from urlparse import parse_qs
import config, re, create_repo
from slacker import Slacker
import random

kms = boto3.client('kms')
sqs = boto3.resource('sqs')
slack = Slacker(config.API_TOKEN)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

functionRepo()
myFunctionRepo = functionRepo()


# Manage Approval
class manageApprove:

    # define attribs for all functions
    def __init__(self):
        self.message = ""
        self.sqs_queue = "githubCreateRepo.fifo"


def lambda_handler(event, context):
    status_code = 200
    body = message = event_body = {}
    myManageApprove = manageApprove()

    status_code, message, event_body = myFunctionRepo.checkbody(event)


if __name__ == "__main__":
    event = context = {}
    lambda_handler(event,context)