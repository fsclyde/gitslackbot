# github-autocreate

Python script which creates github repo for security automation.

### REQUIREMENTS

* Be part of New Wave Organisation
* To have slack and a Github

This will send a message for approval to the Channel #githubot

This channel can be changed in the configurations files.

### USAGE

###### Slack Parameters

* repo_name: mandatory should start by "nw-"
* repo_team_name: mandatory

-----------------------------------

* repo_team_read: mandatory
* repo_team_write: mandatory
* ssh_key_title: optional
* ssh_key: optional

At least 6 parameters are required. Maximum 8 parameters.

1) Here is the configuration of the slackbot for auto repository creation

    `/creategitrepo [repo_name] [repo_team_name]`


2) Here is the exemple for approving a creation of repository

    `/gitapprove [message_id] [repo_team_read] [repo_team_write] [ssh_key_title] [ssh_key]`

### Diagram of gitslackbot

![gitslackbot Diagram](https://github.com/fsclyde/gitslackbot/blob/master/gitslackbot.png "Diagram")
