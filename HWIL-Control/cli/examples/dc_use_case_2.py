#!/usr/bin/env python3
import vitis
import os
import shutil

print ("\n-----------------------------------------------------")
print ("DC USE CASE - 2: Extending an example project by adding new PL component and binary container\n")

# Create a client object -
# It starts Vitis Server
# Create a client object
# Establishes a connection between the server and the client
client = vitis.create_client()

# Set workspace
proj_name = "proj_dc_uc_2"
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

# List all the platforms matching with the mentioned string
client.get_platforms("xilinx_u200_gen3x16_xdma")

platform_xpfm = client.get_platform("xilinx_u250_gen3x16_xdma_4")

# Get kmeans Example template after synching the local libraries with Git
print(f"Sync vitis examples repositories")
examples_repo = 'vitis_examples'
client.sync_git_example_repo(examples_repo)
example = client.get_template('accl_app','simple_vadd')

# Create an project from 'kmeans Application' Template
proj = client.create_sys_project(name=proj_name, platform=platform_xpfm, template=example)

# Getting the project instance for demo after setting it to None
proj = None
proj = client.get_sys_project(proj_name)

# Display the project details
proj.report()

# Add new HLS component
comp_name = 'hls_component1'
kernel_cmp = client.create_hls_component(name = comp_name)

xilinx_vitis = os.environ.get('XILINX_VITIS')
sources_dir  = os.path.join(xilinx_vitis, 'samples/vadd/')
print(sources_dir)

# Import sources to the new PL component
kernel_cmp.import_files(sources_dir, ['krnl_vadd.cpp'], 'src')

# Get config file object
cfg_path = os.path.join(workspace, comp_name, 'hls_config.cfg')
cfg_obj = client.get_config_file(cfg_path)

# Add source and set kernel function
cfg_obj.add_lines('hls',['syn.file=./src/krnl_vadd.cpp'])
cfg_obj.set_value('',key = 'part', value='xcu250-figd2104-2L-e')
cfg_obj.add_lines('hls',['syn.top=krnl_vadd'])
cfg_obj.add_lines('hls',['flow_target=vitis'])
proj.add_component(comp_name)

# Build the project
proj.build('sw_emu')

# Dispose the server and client
vitis.dispose()