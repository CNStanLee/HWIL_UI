#!/usr/bin/env python3
import vitis
import os
import time
import shutil

print ("\n-----------------------------------------------------")
print ("Project Creation using Empty Application and Adding Pre-compiled XO Kernel\n")

# Create a client object -
# It starts Vitis Server
# Create a client object
# Establishes a connection between the server and the client
client = vitis.create_client()

# Set workspace
proj_name = "proj_xo_kernel"
workspace = "/tmp/workspace-" + proj_name
#Delete the workspace if already exists.
if (os.path.isdir(workspace)):
    shutil.rmtree(workspace)
    print(f"Deleted workspace {workspace}")

prjLocation = os.path.join(workspace, proj_name)
client.set_workspace(path=workspace)
print("Workspace set to : " + workspace)

# Add platform repository and get required platform
platforms_dir = os.environ.get('PLATFORM_REPO_PATHS')
if (platforms_dir == None):
    print(f"Set 'PLATFORM_REPO_PATHS' environment variable to add Platform repository")
    exit()
client.add_platform_repos(platforms_dir)
platform_xpfm = client.get_platform("xilinx_u250_gen3x16_xdma_4_1_202210")

# Get Empty Example template after synching the local libraries with Git
print(f"Sync vitis examples repositories")
examples_repo = 'vitis_examples'
client.sync_git_example_repo(examples_repo)

# Get Empty example accelerated application template
example = client.get_template('accl_app','empty')

# Create an application from 'Empty Accelerated Application' Template
proj = client.create_sys_project(name=proj_name, platform=platform_xpfm, template=example)

# Display the project details
proj.report()

# Update project component
app_cmp = client.create_app_component(name = 'app_cmp', platform = platform_xpfm)
proj.add_component(name = 'app_cmp')

# Import sources to application component
script_dir = os.path.dirname(os.path.abspath(__file__))
sources_dir = os.path.join(script_dir, "xo_kernel_srcs")

app_cmp.import_files(from_loc = sources_dir, files = ['vadd.cpp', 'vadd.h'], dest_dir_in_cmp = 'src')

# Build the component
proj.add_container(name = "binary_container_1")

# Import Pre-compiled XO kernel to the project
proj.import_files(from_loc = sources_dir, files = ['rtl_kernel_wizard_0.xo'])

#Add XO Kernel to the project
proj.add_precompiled_kernel(xo_file_path = "rtl_kernel_wizard_0.xo", containers = ['binary_container_1'])

#Build the project
proj.build(target = 'sw_emu')

# Close client and terminate the vitis server
vitis.dispose()