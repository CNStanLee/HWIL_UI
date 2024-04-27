#!/usr/bin/env python3

# This example demonstrates the use of different example repository management APIs
import vitis
import os
import shutil
from datetime import datetime
import platform as os_platform

def is_dir_exists_repos(dir, repos):
    for repo in repos:
        if dir in repo:
            return True
    return False

print ("\n-------------------------------------------")
print ("  Example Repository Management Test \n")
print ("---------------------------------------------")

# Create a client object -
# It starts Vitis Server
# Create a client object
# Establishes a connection between the server and the client
client = vitis.create_client()

date = datetime.now().strftime("%Y%m%d%I%M%S")
if(os_platform.system() == "Windows"):
    workspace_path = 'C:\\tmp\\workspace_apprepo_'+date+'\\'
else:
    workspace_path = '/tmp/workspace_apprepo_'+date+'/'

# Delete the workspace if it already exists
if (os.path.isdir(workspace_path)):
    shutil.rmtree(workspace_path)
    print(f"Deleted Workspace {workspace_path}")

# Sets the workspace to given path
client.set_workspace(path=workspace_path)

# Reset all the user repositories
client.reset_example_repo('accl_app')

# list git example and library repositories configured by the tool
example_repo_list = client.list_example_repos()
# print("Tool configured example repositories")
# print(example_repo_list)

# Create a user repository, especially for library and example developers they have
# in developing examples and libraries, they use this for their testing and automation
# Adding platform directory to platform repository
git_repo_name    = "test_git_Repo"
repo_description = "Get Repo State example"
repo_local_path = f"/tmp/unittest-repo_{date}"

if (os.path.isdir(repo_local_path)):
    shutil.rmtree(repo_local_path)
    print(f"Deleted local repo path '{repo_local_path}'")

git_url_path     = "https://github.com/Xilinx/Vitis_Accel_Examples.git"
branch           = "master"
status = client.add_git_example_repo(name = git_repo_name, description = repo_description,
                                 local_directory = repo_local_path, git_url = git_url_path,
                                 git_branch = branch)

print(f"\nGit repo '{git_repo_name}' added")
if (os.path.isdir(repo_local_path)):
    shutil.rmtree(repo_local_path)
# Download the repository locally for testing
client.sync_git_example_repo(git_repo_name)
# Make sure that the repository state should be downloaded
getStateResponse = client.get_example_repo_state(git_repo_name)
print(f"Git app repo '{git_repo_name}' downloaded, status: {getStateResponse}")

# If the user has examples or library repositories locally on disk then he can use that path to create
# a repository and use it for his development
# Two cases where we need this
#  1. User is developing his examples/libraries and are there locally on disk and would to test before submitting to git
#  2. User is already cloned a repository from git to his local area
local_repo_name = 'test_local_repo'
local_repo_path = repo_local_path
local_repo_description = "Test local example repository"
os.makedirs(local_repo_path, exist_ok = True)

# Add the local path to the examples/library repository
status = client.add_local_example_repo(name=local_repo_name, description = local_repo_description,
                                   local_directory=local_repo_path)
print(f"Local repo '{local_repo_name}' added")

# Add platform repository and get required platform
platforms_dir = os.environ.get('PLATFORM_REPO_PATHS')
if (platforms_dir == None):
    print(f"Set 'PLATFORM_REPO_PATHS' environment variable to add Platform repository")
    exit()

# Users need to get an example path from the repository for creating an example project
# Here are the different ways to get an example
#  1.Get first example in case of multiple matches
example = client.get_template(name = 'copy buffer')
print(f"Got example template for 'copy buffer' - {example}")

#  2.Get first example supporting given platforms in case of multiple matches
example = client.get_template(name = 'copy buffer', platforms = ['u200', 'u280'])
print(f"Got example template for 'copy buffer' - {example} supporting platforms u200 and u280")

#  3.Get list of examples matching the given string
examples = client.get_templates(name = 'copy buffer')
print(f"Got example templates for 'copy buffer' - {examples}")

#  4.Get list of examples supporting given platforms matching the given string
examples = client.get_templates(name = 'copy buffer', platforms = ['u200', 'u280'])
print(f"Got example templates for 'copy buffer' - {examples} supporting platforms u200 and u280")

# Examples/Libraries repository details like description, name, local directory, git url,
# git branch and type
# Example repository can be updated using the following APIs

# Get an example repository object for local repository
local_repo_obj = client.get_example_repo(local_repo_name)
print('Got example repository')
print(local_repo_obj)
print('Got git example repository')

# Edit the fields
local_repo_obj.display_name = 'test_local_repo1'
local_repo_obj.description = "Test local example repository 1"
client.update_example_repo(local_repo_obj)

print("Updated local repository")
print(client.get_example_repo(local_repo_obj.name))

# Get an example repository object for git repository
test_git_repo_obj = client.get_example_repo(git_repo_name)
print('Got git example repository')

# Edit the fields
test_git_repo_obj.display_name = "test_git_Repo1"
test_git_repo_obj.description = 'Get Repo State example 1'
test_git_repo_obj.local_directory = '/tmp/unittest-repo1'
test_git_repo_obj.git_branch = '2021.2'
test_git_repo_obj.git_url = 'https://github.com/Xilinx/Vitis_Libraries.git'
client.update_example_repo(test_git_repo_obj)

print("Updated local repository")
print(client.get_example_repo(test_git_repo_obj.name))

# Delete example repositories local and git added
client.delete_example_repo(local_repo_obj.name)
print(f"Deleted local repository")

client.delete_example_repo(test_git_repo_obj.name)
print(f"Deleted git repository")
example_repo_list = client.list_example_repos()
if is_dir_exists_repos("test_git_Repo1", example_repo_list) or is_dir_exists_repos('test_local_repo1', example_repo_list):
    print("Failed to delete the user example repositories")
    exit()

# Adding a local repository for testing reset repository
local_repo_name = 'test_local_repo-1'
local_repo_path = repo_local_path
local_repo_description = "Test local example repository"
os.makedirs(local_repo_path, exist_ok = True)
client.add_local_example_repo(name=local_repo_name, description = local_repo_description,
                                   local_directory=local_repo_path)
print(f"Added a local repository {local_repo_name}")
client.get_example_repo(local_repo_name)

# Reset the examples repositories to tool configured examples repositories
# To Reset the libraries repositories pass type 'LIBRARY' as an argument to the function
client.reset_example_repo('accl_app')
print("Reset example repositories to tool default repositories")
example_repos_list = client.list_example_repos()
if is_dir_exists_repos(local_repo_name, example_repos_list):
    print("Failed to reset example repositories")
    exit()

if (os.path.isdir(repo_local_path)):
    shutil.rmtree(repo_local_path)

if (os.path.isdir(workspace_path)):
    shutil.rmtree(workspace_path)

# Close the client connection and terminate the vitis server
vitis.dispose()
