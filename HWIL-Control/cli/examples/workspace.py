#!/usr/bin/env python3
import vitis
import os
import shutil
import platform as os_platform

#This example demonstrates the use of different workspace management APIs
print ("\n---------------------------------------")
print ("        Workspace APIs example ")
print ("---------------------------------------")

def is_dir_exists_repos(dir, repos):
    for repo in repos:
	    if dir in repo:
		    return True
    return False

client = vitis.create_client()
client.info()

#Workspace is first step the user should set
if(os_platform.system() == "Windows"):
    workspacePath1 = 'C:\\tmp\\workspace1\\'
else:
    workspacePath1 = '/tmp/workspace1/'
#Delete the workspace if it already exists
if (os.path.isdir(workspacePath1)):
    shutil.rmtree(workspacePath1)
    print(f"Deleted Workspace {workspacePath1}")

#checking wheher the workspace is already set or not
status = client.check_workspace()
if status == False:
    client.set_workspace(path=workspacePath1)
    print(f"Set Workspace to : {workspacePath1}")
else:
    #If workspace is already set, get the workspace
     wsPath = client.get_workspace()
     print(f"Workspace is : {wsPath}")

#Set platform repository path, this information will be stored in workspace
#Tool will read the information and set this so that the users can get the 
#platforms as soon as he sets the workspace
if(os_platform.system() == "Windows"):
    platform_dirs = ['C:\\tmp\\platforms1', 'C:\\tmp\\platforms2']
else:
    platform_dirs = ['/tmp/platforms1', '/tmp/platforms2']
for i in platform_dirs:
    if (os.path.isfile(i) == False) and (os.path.isdir(i) == False):
        os.mkdir(i)

client.add_platform_repos(platform_dirs)
platform_paths = client.list_platform_repos()
if( (not is_dir_exists_repos(platform_dirs[0], platform_paths)) or (not is_dir_exists_repos(platform_dirs[1], platform_paths)) ):
    print("Failed to get platform repositories")
    exit()

#Change the workspace to different path
if(os_platform.system() == "Windows"):
    workspacePath2 = 'C:\\tmp\\workspace2\\'
else:
    workspacePath2 = '/tmp/workspace2/'
    
#Delete the workspace if it already exists
if (os.path.isdir(workspacePath2)):
    shutil.rmtree(workspacePath2)
    print(f"Deleted Workspace {workspacePath2}")

client.set_workspace(path=workspacePath2)
wsPath = client.get_workspace()
print(f"Switching Workspace to : {wsPath}")
platform_paths = client.list_platform_repos()
if is_dir_exists_repos(platform_dirs[0], platform_paths) or is_dir_exists_repos(platform_dirs[1], platform_paths) :
    print("New workspace should not show the platforms added to the previous workspace")
    exit()

#Change the workspace back to the previous path
client.set_workspace(path=workspacePath1)
wsPath = client.get_workspace()
print(f"Switching Workspace back to : {wsPath}")
platform_paths = client.list_platform_repos()
if( (not is_dir_exists_repos(platform_dirs[0], platform_paths)) or (not is_dir_exists_repos(platform_dirs[1], platform_paths)) ):
    print("Failed to load platform repository paths from the workspace")
    exit()

# Set the log level to info
client.log_level('INFO')

#Close the client and terminate the server
vitis.dispose()

