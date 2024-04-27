#!/usr/bin/env python3
import vitis
import os
import shutil

print ("\n------------------------------------------------------------------------------")
print ("EDGE USE CASE - 1: AIE Project Creation using Empty System Project and Extending\n")

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
if (rootfs == None):
    print(f"Set 'IDE_VERSAL_ROOT_FS' environment variable with valid rootfs value.")
    exit()

# Check for kernel image env variable
image = os.environ.get('IDE_VERSAL_KERNEL_IMAGE')
if (image == None):
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
proj_name = "edge_uc_1"
workspace = "/tmp/workspace-" + proj_name
#Delete the workspace if already exists.
if (os.path.isdir(workspace)):
    shutil.rmtree(workspace)
    print(f"Deleted workspace {workspace}")

prjLocation = os.path.join(workspace, proj_name)
client.set_workspace(path=workspace)
print("Workspace set to : " + workspace)

client.add_platform_repos(platforms_dir)
platform_xpfm = client.get_platform("xilinx_vck190_base_202")

# Get Empty Example template after synching the local libraries with Git
print(f"Sync vitis examples repositories")
examples_repo = 'vitis_examples'
client.sync_git_example_repo(examples_repo)

# Get Empty example accelerated application template
example = client.get_template('accl_app','empty')

# Create a project from 'Empty Accelerated Application' Template
proj = client.create_sys_project(name=proj_name, platform=platform_xpfm, template=example)

# Display the project details
proj.report()

# Add AIE component
aie_component = client.create_aie_component(name = "aie_test", platform = platform_xpfm)
xilinx_vitis = os.environ.get('XILINX_VITIS')
sources_dir  = os.path.join(xilinx_vitis, 'samples/aie_system_examples/aie_sys_design/src/')

# Add aie top level file to aie component
aie_component.import_files(from_loc = sources_dir, files = ['graph.cpp', 'graph.h', 'kernels.h', 'include.h', 'classify.cc', 'hb27_2i.cc', 'host.h', 'input.h', 'golden.h'], dest_dir_in_cmp = '.')
aie_component.update_top_level_file(top_level_file = 'graph.cpp')
proj.add_component(name = "aie_test")

# Add hls comp1
hls_comp1 = client.create_hls_component(name = 'hls_comp1')
hls_comp1.import_files(from_loc = sources_dir, files = ['mm2s.cpp'], dest_dir_in_cmp = 'src')

# Get config file object
cfg_path = os.path.join(workspace, 'hls_comp1', 'hls_config.cfg')
cfg_obj = client.get_config_file(cfg_path)

# Set sources and kernel function
cfg_obj.add_lines('hls',['syn.file=./src/mm2s.cpp'])
cfg_obj.set_value('',key = 'part', value='xcvc1902-vsva2197-2MP-e-S')
cfg_obj.add_lines('hls',['syn.top=mm2s'])
cfg_obj.add_lines('hls',['flow_target=vitis'])
proj.add_container(name = "binary_container_1")
proj.add_component(name = 'hls_comp1', container_name = ['binary_container_1'])

# Add hls comp2
hls_comp1 = client.create_hls_component(name = 'hls_comp2')
hls_comp1.import_files(from_loc = sources_dir, files = ['s2mm.cpp'], dest_dir_in_cmp = 'src')

# Get config file object
cfg_path = os.path.join(workspace, 'hls_comp2', 'hls_config.cfg')
cfg_obj = client.get_config_file(cfg_path)

# Set sources and kernel function
cfg_obj.add_lines('hls',['syn.file=./src/s2mm.cpp'])
cfg_obj.set_value('',key = 'part', value='xcvc1902-vsva2197-2MP-e-S')
cfg_obj.add_lines('hls',['syn.top=s2mm'])
cfg_obj.add_lines('hls',['flow_target=vitis'])
proj.add_component(name = 'hls_comp2', container_name = ['binary_container_1'])

# Add hls comp3
hls_comp1 = client.create_hls_component(name = 'hls_comp3')
hls_comp1.import_files(from_loc = sources_dir, files = ['polar_clip.cpp'], dest_dir_in_cmp = 'src')

# Get config file object
cfg_path = os.path.join(workspace, 'hls_comp3', 'hls_config.cfg')
cfg_obj = client.get_config_file(cfg_path)

# Set sources and kernel function
cfg_obj.add_lines('hls',['syn.file=./src/polar_clip.cpp'])
cfg_obj.set_value('',key = 'part', value='xcvc1902-vsva2197-2MP-e-S')
cfg_obj.add_lines('hls',['syn.top=polar_clip'])
cfg_obj.add_lines('hls',['flow_target=vitis'])
proj.add_component(name = 'hls_comp3', container_name = ['binary_container_1'])

# Remove cfg files
proj.remove_cfg_files(name = 'binary_container_1', cfg_files = ['hw_link/binary_container_1-link.cfg'])
proj.remove_files(['hw_link/binary_container_1-link.cfg'])

cfg_path = os.path.join(xilinx_vitis, 'samples/aie_system_examples/aie_sys_design/')
proj.import_files(from_loc = cfg_path, files = ['system.cfg'])
proj.add_cfg_files(name = 'binary_container_1', cfg_files = ['system.cfg'])

# Display the project details
proj.report()

# Update Host component
app_cmp = client.create_app_component(name = 'app_cmp', platform = platform_xpfm)
app_cmp.import_files(from_loc = sources_dir, files = ['host.cpp','golden.h', 'graph.h', 'host.h', 'include.h','input.h', 'kernels.h'], dest_dir_in_cmp = 'src')
data_path = os.path.join(xilinx_vitis, 'samples/aie_system_examples/aie_sys_design/data')
app_cmp.import_files(from_loc = data_path, dest_dir_in_cmp = 'data')
app_cmp.build()
proj.add_component('app_cmp')

# Display the project details
proj.report()

# Build project
proj.build(target = 'sw_emu')

#Deleting the project
client.delete_sys_project(proj_name)

# Close client and terminate the vitis server
vitis.dispose()