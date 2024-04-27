#!/usr/bin/env python3
import vitis
import os
import time
import shutil
from datetime import datetime

print ("\n-----------------------------------------------------")
print ("AIE component use case: Component creation and building\n")

# Create a client object -
client = vitis.create_client()

# Set workspace
date = datetime.now().strftime("%Y%m%d%I%M%S")
workspace = '/tmp/workspace_'+date+'/'
comp_name = "aie_component_test"

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
platform_xpfm = client.get_platform("xilinx_vck190_base_2023")

# Create aie component
aie_test_comp = client.create_aie_component(name = comp_name, platform = platform_xpfm, template = "empty")
# Print component information
aie_test_comp.report()

# Import sources to component
xilinx_vitis = os.environ.get('XILINX_VITIS')
sources_dir  = os.path.join(xilinx_vitis, 'samples/aie_system_examples/aie_sys_design/src/')
print('sources dir = ', sources_dir)

# Import sources to AIE component
aie_test_comp.import_files(from_loc = sources_dir, files = ['graph.cpp', 'graph.h', 'kernels.h', 'include.h', 'classify.cc', 'hb27_2i.cc'])

# Add top level level
aie_test_comp.update_top_level_file(top_level_file = 'graph.cpp')

# Build component on target x86sim (default target)
aie_test_comp.build()

# Print component information
aie_test_comp.report()

if (os.path.isdir(workspace)):
    shutil.rmtree(workspace, ignore_errors=True)
    print(f"Deleted workspace {workspace}")


# Close the client connection and terminate the Vitis server
vitis.dispose()
