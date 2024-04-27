#!/usr/bin/env python3
import vitis
import os
import time
import shutil

print ("\n-----------------------------------------------------")
print ("EDGE USE CASE - 2: AIE Project creation using aie sys design template.\n")

# Add platform repository and get required platform
platforms_dir = os.environ.get('PLATFORM_REPO_PATHS')
if (platforms_dir == None):
    print(f"Set 'PLATFORM_REPO_PATHS' environment variable to add Platform repository")
    exit()

# Check for sysroot env variable
sysroot = os.environ.get('IDE_VERSAL_SYSROOT')
if (sysroot == None):
    print(f"Set 'IDE_VERSAL_SYSROOT' environment variable with valid sysroot value.")
    exit()

# Check for rootfs env variable
rootfs = os.environ.get('IDE_VERSAL_ROOT_FS')
if (sysroot == None):
    print(f"Set 'IDE_VERSAL_ROOT_FS' environment variable with valid rootfs value.")
    exit()

# Check for kernel image env variable
image = os.environ.get('IDE_VERSAL_KERNEL_IMAGE')
if (sysroot == None):
    print(f"Set 'IDE_VERSAL_KERNEL_IMAGE' environment variable with valid kernel image value.")
    exit()

# Check for XRT variable
# xrt_root_dir = os.environ.get('XRT_ROOT_DIR')
# if (xrt_root_dir == None):
#     print(f"Set 'XRT_ROOT_DIR' environment variable with valid Xilinx Runtime.")
#     exit()

# Create a client object -
# It starts Vitis Server
# Create a client object
# Establishes a connection between the server and the client
client = vitis.create_client()

# Set workspace
proj_name = "edge_uc_2"
workspace = "/tmp/workspace-" + proj_name
#Delete the workspace if already exists.
if (os.path.isdir(workspace)):
    shutil.rmtree(workspace)
    print(f"Deleted workspace {workspace}")

prjLocation = os.path.join(workspace, proj_name)
client.set_workspace(path=workspace)
print("Workspace set to : " + workspace)

client.add_platform_repos(platforms_dir)
platform_xpfm = client.get_platform("vck190_base_202")

# Get template for aie sys design and create a system project
example = client.get_template('accl_app','aie_sys_design')

# Create Application
proj = client.create_sys_project(name=proj_name, platform=platform_xpfm, template=example)

# Display the project details
proj.report()

# Build the project
proj.build()

# Clean the project
proj.clean()

# Dispose the server and client
vitis.dispose()
