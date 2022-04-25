import requests
import os
import xlsxwriter

""" 
    This script will print out a list of users that have access to a Projects under a top level group.

    Requirements:
    - Gitlab API Key/Personal Access Token. This can be set via GITLAB_API_KEY environment variable or you will be prompted for it.
    - top level group ID. This can be set via GITLAB_GROUP_ID environment variable or you will be prompted for it.

    Usage:

    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt
    $ GITLAB_API_KEY=<your_api_key> GITLAB_GROUP_ID=<your_group_id> python3 audit.py

    This will create or overwrite a file called "audit.xlsx" in the current directory with a list of users, what projects and groups they are assigned to.

"""

# Vars
if 'GITLAB_GROUP_ID' in os.environ:
    topGroup = str(os.environ['GITLAB_GROUP_ID'])
else:
    topGroup = input("Enter the top level group ID: ")

# Get API Key
if 'GITLAB_API_KEY' in os.environ:
    gitlabAPIKey = os.environ['GITLAB_API_KEY']
else:
    gitlabAPIKey = input("Enter your Gitlab API Key: ")

authHeaders = {"Authorization": "Bearer " + gitlabAPIKey}

# Get All Groups
groupsResp = requests.get("https://gitlab.com/api/v4/groups/" + topGroup + "/descendant_groups", headers=authHeaders)
groups = groupsResp.json()
groupIds = [{"id": topGroup, "name": "Infinite Blue"}]

# Get All Projects from the groups
for group in groups:
    groupIds.append({"id": str(group["id"]), "name": str(group["name"])})

projectIds = []
for groupObj in groupIds:
    group = groupObj["id"]
    projectsResp = requests.get("https://gitlab.com/api/v4/groups/" + str(group) + "/projects", headers=authHeaders)
    projects = projectsResp.json()
    for project in projects:
        projectIds.append({"id": str(project["id"]), "name": str(project["name"])})

members = []

# Get All members of all Groups
for groupObj in groupIds:
    group = groupObj["id"]
    membersResp = requests.get("https://gitlab.com/api/v4/groups/" + str(group) + "/members", headers=authHeaders)
    membersRaw = membersResp.json()
    for member in membersRaw:
        # check if member in members list
        if member["id"] not in list(map(lambda x: x["id"], members)):
            members.append({"id": member["id"], "username": member["username"], "groups": [groupObj]})
        else:
            # add group to member
            for searchmember in members:
                if member["id"] == searchmember["id"]:
                    searchmember["groups"].append(groupObj)

# Get All members of all Projects
for projectObj in projectIds:
    project = projectObj["id"]
    membersResp = requests.get("https://gitlab.com/api/v4/projects/" + str(project) + "/members", headers=authHeaders)
    membersRaw = membersResp.json()
    for member in membersRaw:
        # check if member in members list
        if member["id"] not in list(map(lambda x: x["id"], members)):
            members.append({"id": member["id"], "username": member["username"], "projects": [projectObj]})
        else:
            # add project to member
            for searchmember in members:
                if member["id"] == searchmember["id"]:
                    try:
                        searchmember["projects"]
                    except KeyError:
                        searchmember["projects"] = []
                    searchmember["projects"].append(projectObj)

# Get member details
xlsxData = [["Username", "Groups", "Projects"]]
for member in members:
    memberDetailsResp = requests.get("https://gitlab.com/api/v4/users/" + str(member["id"]), headers=authHeaders)
    # Print out names, projects and groups
    user = memberDetailsResp.json()["name"] + " (" + memberDetailsResp.json()["username"] + ")"
    try:
        groups = str(member["groups"])
    except KeyError:
        groups = "None"
    try:
        projects = str(member["projects"])
    except KeyError:
        projects = "None"

    xlsxData.append([user, groups, projects])

workbook = xlsxwriter.Workbook("audit.xlsx")
worksheet = workbook.add_worksheet("Audit")

for row_num, row_data in enumerate(xlsxData):
    for col_num, data in enumerate(row_data):
        worksheet.write(row_num, col_num, data)

max_col_sizes = [ max([len(str(xlsxData[row][col])) for row in range(len(xlsxData))]) for col in range(len(xlsxData[0])) ]
col = 0
for max_col_size in max_col_sizes:
    worksheet.set_column(col, col, max_col_size * 1.2)
    col += 1

workbook.close()