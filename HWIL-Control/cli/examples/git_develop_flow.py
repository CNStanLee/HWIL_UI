#!/usr/bin/env python3
import vitis
import git
import os
import shutil
import getpass
from datetime import datetime
import platform as os_platform

# GIT Integration
# In run.sh set below variables
# Requires GIT_USERNAME and GIT_PASSWORD environment variables,
# export GIT_USERNAME=<user_name>
# export GIT_PASSWORD=<password_of_user_in_plan_text_format>
# If GIT_PASSWORD not set, then it asks the user to provide the password.
# update REMOTE_URL variable with your GIT repository URL

print ("\n-----------------------------------------------------")
print ("GIT - Development flow use case\n")

if(os_platform.system() == "Windows"):
    workspace = 'C:\\tmp\\workspace-git\\'
else:
    workspace = '/tmp/workspace-git/'
date = datetime.now().strftime("%m-%d-%Y_%I_%M_%S")

# Clean the workspace directory
if (os.path.isdir(workspace)):
    shutil.rmtree(workspace)
    print(f"Deleted Workspace {workspace}")

proj_name = "vadd-proj"
prjLocation = os.path.join(workspace, proj_name)

# Create VITIS NG client
client = vitis.create_client()

#Add platform repository and get required platform
platforms_dir = os.environ.get('PLATFORM_REPO_PATHS')
if (platforms_dir == None):
    print(f"Set 'PLATFORM_REPO_PATHS' environment variable to add Platform repository")
    exit(1)

os.system("git config --global credential.helper store")

# GET GIT USERNAME
username = os.environ.get('GIT_USERNAME')
if (username == None):
    username = getpass.getuser()

# GET GIT Passoword
token = os.environ.get("GIT_PASSWORD")
if (token == None):
    print(f"GIT_PASSWORD' environment variable not set.")
    #Read password from user.
    print(f"Enter GIT Password for user '{username}'")
    token = getpass.getpass()

# Users can modify REMOTE_URL to their repository URL
REMOTE_URL = f"https://{username}@gitenterprise.xilinx.com/vitiside/test_git_repo.git"

# Clone the GIT repository
repo = git.Repo.clone_from(REMOTE_URL, workspace)
print(f"Cloned the GIT repository to '{workspace}' location")
new_branch_name = f'pl_kernel_upd_{date}'
new_branch = repo.create_head(new_branch_name)
new_branch.checkout()
print(f"New branch '{new_branch_name}' created")

# Do modification to project files
kernel_src = os.path.join(workspace, "vadd-app_krnl_vadd/src/krnl_vadd.cpp")
with open(kernel_src, "a") as src_file:
    msg = f"\n// Added a comment to check GIT update - {date}"
    src_file.write(msg)
    print(f"Kernel Source modified")

# set workspace
client.set_workspace(path=workspace)
print("Workspace set to : " + workspace)

# Add platform repository
client.add_platform_repos(platforms_dir)

# Get Application from workspace
proj = client.get_sys_project(proj_name)

#Build project - PL Kernel component build
proj.build(target = 'sw_emu')

# Track changes and submit them to branch
repo.git.add(kernel_src)
commit_message = f"GIT repository development flow commit {date}"
repo.git.commit(m=commit_message)
repo.git.push('--set-upstream', 'origin', new_branch)
print(f"Changes pushed to the branch '{new_branch_name}'")

# Merge cahnges from branch to main
main = repo.heads.main
main.checkout()
print(f"Checkout 'main' branch")
# To get new branch references to local.
repo.git.fetch("--all")
repo.git.merge("--no-ff", new_branch)
repo.git.push('--set-upstream', 'origin', main)
print(f"Changes merged from the branch '{new_branch_name}' to 'main' branch.")

# Delete the branch
del_new_branch = f":{new_branch_name}"
# Deletes the branch remotely in GIThub
repo.git.push("--set-upstream", "origin", del_new_branch)
# Deletes the branch locally
repo.git.branch("-D", new_branch_name)
print(f"Delete brach '{new_branch_name}'")

#Close client and terminate the vitis server
vitis.dispose()