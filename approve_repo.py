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
from boto3.dynamodb.conditions import Key


kms = boto3.client('kms')
resource = boto3.resource('dynamodb')
client   = boto3.client('dynamodb')
slack = Slacker(config.API_TOKEN)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

functionRepo()
myFunctionRepo = functionRepo()


# Manage Approval
class manageApprove:

    # define attribs for all functions
    def __init__(self):
        self.table_name = "githubCreateRepo"
        self.table = resource.Table(self.table_name)

    # check parameters
    def checkParam(self, param):
        message = {}
        test = 0

        try:
            data = param.split(" ")
        except KeyError:
            message["status"] = "Parameters have to be separated by space"
            test = 1

        if test == 0:
            if len(data) < 3:
                message["status"] = "At least 3 parameters are required: message id, teams read, teams write"
                test = 1

        if test == 0:
            if len(data[0]) != 15:
                message["status"] = "Wrong messaged_id provided"
                test = 1

        return message, test, data

    # Query dynamodb to get information from it
    def getItemFromDynamodb(self,data):
        message = ""

        # Using query With dynamoDB
        response = self.table.query(KeyConditionExpression=Key('message_id').eq(data[0]))
        if response:
            table_data = response['Items'][0]["data"]
        else:
            message["status"] = "This message does not match with the one in the DB"

        return table_data, message


def lambda_handler(event, context):
    status_code = 200
    body = message = event_body = dev_input = {}
    myManageApprove = manageApprove()
    message["status"] = ""
    status_code, message, event_body = myFunctionRepo.checkBody(event)
    command_text = event_body['text']

    # Check the parameters
    message, checkstatus, data = myManageApprove.checkParam(command_text)
    if checkstatus == 0:

        dev_input, message = myManageApprove.getItemFromDynamodb(data)


    return message["status"]


if __name__ == "__main__":
    event = context = {}
    lambda_handler(event,context)