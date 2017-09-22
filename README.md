# github-autocreate

Python script which creates github repo for security automation.

### REQUIREMENTS

* Be part of New Wave Organisation
* To have slack and a Github

### USAGE

###### Slack Parameters

* repo_name: mandatory should start by "nw-"
* description: mandatory
* repo_team_name: mandatory
* repo_team_read: optional
* repo_team_write: optional
* ssh_key_title: optional
* ssh_key: optional

At least 6 parameters are required. Maximum 8 parameters.

1) Here is the configuration of the slackbot for auto repository creation

    ```/creategitrepo [repo_name] [description] [repo_team_name]```


2) Here is the exemple for approving a creation of repository

    ```/gitapprove [message_id] [repo_team_read] [repo_team_write] [ssh_key_title] [ssh_key]```
