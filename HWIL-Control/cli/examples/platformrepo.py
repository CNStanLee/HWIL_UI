#!/usr/bin/env python3
# This example demonstrates the use of different platform repository and platform management APIs

import vitis
import os
import shutil
import platform as os_platform

def is_dir_exists_repos(dir, repos):
    for repo in repos:
        if (dir in repo) or (os.path.abspath(dir) in repo):
            return True
    return False

print ("\n----------------------------------------")
print ("  Platform Repository Management Test \n")
print ("----------------------------------------")

# Create a client object
# It starts Vitis Server
# Create a client object
# Establishes a connection between the server and the client
client = vitis.create_client()

if(os_platform.system() == "Windows"):
    workspace_path = 'C:\\tmp\\workspace-platform-repo\\'
else:
    workspace_path = '/tmp/workspace-platform-repo/'
# Delete the workspace if it already exists
if (os.path.isdir(workspace_path)):
    shutil.rmtree(workspace_path)
    print(f"Deleted Workspace {workspace_path}")

# Sets the workspace to given path
client.set_workspace(workspace_path)

# Add platform repository and get required platform
# The tool should automatically consider PLATFORM_REPO_PATHS as platform repository
platform_repo_dir = os.environ.get('PLATFORM_REPO_PATHS')
if (platform_repo_dir == None):
    print(f"Set 'PLATFORM_REPO_PATHS' environment variable to add Platform repository")
    exit()

platform_paths = client.list_platform_repos()
if not is_dir_exists_repos(platform_repo_dir, platform_paths):
    print("Failed to load PLATFORM_REPO_PATHS as platform repository path")
    exit()

# Add different platform repository paths
platform_dirs = ['/tmp/platforms1', '/tmp/platforms2']
for i in platform_dirs:
    if (os.path.isfile(i) == False) and (os.path.isdir(i) == False):
        os.mkdir(i)

client.add_platform_repos(platform_dirs)
platform_paths = client.list_platform_repos()
if( (not is_dir_exists_repos(platform_dirs[0], platform_paths)) or (not is_dir_exists_repos(platform_dirs[1], platform_paths)) ):
    print("Failed to get the user platform repository paths")
    exit()

client.delete_platform_repos(platform_dirs)
platform_paths = client.list_platform_repos()
if is_dir_exists_repos(platform_dirs[0], platform_paths) or is_dir_exists_repos(platform_dirs[1], platform_paths):
    print("Failed to delete user repository paths from platform repositories")
    exit()

# Assume that u200 platform is available in PLATFORM_REPO_PATHS
u200 = client.get_platform("u200.*2021")

# Get HW platform information
hwPlatformInfo = client.get_hw_platform(u200)
print("\n HW Platfor information")
print(hwPlatformInfo)

# Get SW Platform information
swPlatformInfo = client.get_sw_platform(u200)
print("\n SW Platform Information")
print(swPlatformInfo)

# Assume that at least one u200 platforms are available in PLATFORM_REPO_PATHS
client.get_platforms("u200")

# Rescan the platform repository
client.rescan_platform_repos(platform_repo_dir)

# Close the client and terminate the server
vitis.dispose()
