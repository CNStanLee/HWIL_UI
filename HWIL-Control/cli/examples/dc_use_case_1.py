#!/usr/bin/env python3
import sys
import vitis
import os
import time
import shutil

print ("\n-----------------------------------------------------")
print ("DC USE CASE - 1: Project Creation using Empty System Project and Extending\n")

# Create a client object -
# It starts Vitis Server
# Create a client object
# Establishes a connection between the server and the client
client = vitis.create_client()

# Set workspace
proj_name = "proj_dc_uc_1"
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
platform_xpfm = client.get_platform("xilinx_u250_gen3x16_xdma_4")

# Get Empty Example template after synching the local libraries with Git
print(f"Sync vitis examples repositories")
examples_repo = 'vitis_examples'
client.sync_git_example_repo(examples_repo)

# Get Empty example accelerated system project template
example = client.get_template('accl_app','empty',platform_xpfm)

# Create a system project from 'Empty Accelerated Application' Template
proj = client.create_sys_project(name=proj_name, platform=platform_xpfm, template=example)

# Update Host component
app_component = client.create_app_component(name = 'app_component1', platform = platform_xpfm)

# Import sources to Host component
xilinx_vitis = os.environ.get('XILINX_VITIS')
sources_dir  = os.path.join(xilinx_vitis, 'samples/vadd/')
app_component.import_files(from_loc = sources_dir, files = ['vadd.cpp', 'vadd.h'], dest_dir_in_cmp = 'src')

# Build app component
app_component.build()

# Add app component
proj.add_component('app_component1')

# Get kernel component to update the component with sources and defining kernels
comp_name = 'kernel_cmp'
kernel_cmp = client.create_hls_component(name = comp_name)

# Getting the component instance for demo after setting it to None
kernel_cmp = None
kernel_cmp = client.get_component('kernel_cmp')

# Import sources to HLS component
kernel_cmp.import_files(from_loc = sources_dir, files = ['krnl_vadd.cpp'], dest_dir_in_cmp = 'src')

# Get config file object
cfg_path = os.path.join(workspace, comp_name, 'hls_config.cfg')
cfg_obj = client.get_config_file(cfg_path)

# Add source and test bench files
cfg_obj.add_lines('hls',['syn.file=./src/krnl_vadd.cpp'])
cfg_obj.set_value('',key = 'part', value='xcu250-figd2104-2L-e')
cfg_obj.add_lines('hls',['syn.top=krnl_vadd'])
cfg_obj.add_lines('hls',['flow_target=vitis'])

# Create a binary containers and Add kernels to the binary container
proj.add_container("binary_container_1")
proj.add_component(name = 'kernel_cmp', container_name = ['binary_container_1'])

# List components in the project
proj.list_components()

# Display the project details
proj.report()

# Generate build files. This step is optional
proj.generate_build_files()

# Build component
proj.build(target = 'sw_emu')

# Remove component
proj.remove_component('kernel_cmp')

# Delete component
client.delete_component('kernel_cmp')

# List components in the workspace
client.list_components()

#Delete binary container
proj.delete_container(name = 'binary_container_1')

# Close client and terminate the vitis server
vitis.dispose()