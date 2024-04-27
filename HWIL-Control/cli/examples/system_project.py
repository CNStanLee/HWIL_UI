#!/usr/bin/env python3
import vitis
import os
import time
import shutil

print ("\n-----------------------------------------------------")
print ("System Project build files generation and build APIs \n")

#Create a client object -
# It starts Vitis Server
# Create a client object
# Establishes a connection between the server and the client
client = vitis.create_client()

#Set workspace
proj_name = "build-proj"
workspace = "/tmp/workspace-" + proj_name
#Delete the workspace if already exists.
if (os.path.isdir(workspace)):
    shutil.rmtree(workspace)
    print(f"Deleted workspace {workspace}")

prjLocation = os.path.join(workspace, proj_name)
client.set_workspace(path=workspace)
print("Workspace set to : " + workspace)

#Add platform repository and get required platform
platforms_dir = os.environ.get('PLATFORM_REPO_PATHS')
if (platforms_dir == None):
    print(f"Set 'PLATFORM_REPO_PATHS' environment variable to add Platform repository")
    exit()
client.add_platform_repos(platforms_dir)

# List all the platforms available
client.list_platforms()
platform_xpfm = client.get_platform("xilinx_u50_gen3x4_xdma")

# Get Empty Example template after synching the local libraries with Git
print(f"Sync vitis examples repositories")
examples_repo = 'vitis_examples'
client.sync_git_example_repo(examples_repo)

# List all the templates matching with the given string
client.get_templates(name = 'simple_vadd')

#Get vector add application template
example = client.get_template(name = 'simple_vadd')

#Create an system project from the Template
proj = client.create_sys_project(name=proj_name, platform=platform_xpfm, template=example)

#List the Application projects in the workspace
client.list_sys_projects()

#Update the platform of a project to new platform
new_platform = client.get_platform("xilinx_u250_gen3x16_xdma_4_1_202210")
proj.update_platform(platform = new_platform)

# Printing project object info
print("\n Application object information:")
print(proj)

# Clone project demo
cloned_proj = client.clone_sys_project(proj_name, 'cloned_comp')
cloned_proj.report()

#Application has components- APP, HLS, AIE, the user can build components too
# proj.build(target = "sw_emu")

# Cleaning the build
# proj.clean()

#Close client and terminate the Vitis server
vitis.dispose()
