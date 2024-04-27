#!/usr/bin/env python3
import vitis
import os
import time
import shutil
from datetime import datetime

print ("\n-----------------------------------------------------")
print ("Application component use case: Component creation and building\n")

# Create a client object -
client = vitis.create_client()

# Set workspace
date = datetime.now().strftime("%Y%m%d%I%M%S")
workspace = '/tmp/workspace_'+date+'/'
comp_name = "app_component_test"

#Delete the workspace if already exists.
if (os.path.isdir(workspace)):
    shutil.rmtree(workspace)
    print(f"Deleted workspace {workspace}")

client.set_workspace(workspace)

# Add platform repository and get required platform
platforms_dir = os.environ.get('PLATFORM_REPO_PATHS')
if (platforms_dir == None):
    print(f"Set 'PLATFORM_REPO_PATHS' environment variable to add Platform repository")
    exit()

client.add_platform_repos(platforms_dir)
platform_xpfm = client.get_platform("xilinx_u250_gen3x16_xdma_4")

# Create app component
app_test_comp = client.create_app_component(name = comp_name, platform = platform_xpfm, template = "empty")
# Print component information
app_test_comp.report()

# Setting sysroot
sysroot_dir  = os.path.join(platforms_dir, 'sw/versal/xilinx-versal/sysroots/aarch64-xilinx-linux/')
app_test_comp.set_sysroot(sysroot_dir)
print("Sysroot", app_test_comp.get_sysroot())

# Import sources to component
xilinx_vitis = os.environ.get('XILINX_VITIS')
sources_dir  = os.path.join(xilinx_vitis, 'samples/vadd/')
print('sources dir = ', sources_dir)
# Import sources to app component
app_test_comp.import_files(from_loc = sources_dir, files = ['vadd.cpp', 'vadd.h'], dest_dir_in_cmp = 'src')

# Print component information
app_test_comp.report()

# Build component
app_test_comp.build()

# Clean the component
app_test_comp.clean()

# Delete app component to create new on different platform
client.delete_component(comp_name)

# Get new platform i.e. zcu102
platform_xpfm = client.get_platform("zcu102")
app_test_comp = client.create_app_component(name = comp_name, platform = platform_xpfm, template = "empty")

# Print component information
app_test_comp.import_files(from_loc = sources_dir, files = ['vadd.cpp', 'vadd.h'], dest_dir_in_cmp = 'src')
app_test_comp.report()

# Build component
app_test_comp.build()

# Clean the component
app_test_comp.clean()

# Delete app component to create new on different platform
client.delete_component(comp_name)

# Get new platform i.e. vck190
platform_xpfm = client.get_platform("vck190_base_2")
app_test_comp = client.create_app_component(name = comp_name, platform = platform_xpfm, template = "empty")

# Print component information
app_test_comp.import_files(from_loc = sources_dir, files = ['vadd.cpp', 'vadd.h'], dest_dir_in_cmp = 'src')
app_test_comp.report()

# Build component
app_test_comp.build()

# Clean the component
app_test_comp.clean()

# Delete application component to create new on different platform
client.delete_component(comp_name)

if (os.path.isdir(workspace)):
    shutil.rmtree(workspace, ignore_errors=True)
    print(f"Deleted workspace {workspace}")

# Close the client connection and terminate the vitis server
vitis.dispose()