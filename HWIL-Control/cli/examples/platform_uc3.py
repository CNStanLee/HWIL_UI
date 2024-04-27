#!/usr/bin/env python3
import vitis
import os
import time
import shutil
from datetime import datetime
import platform as os_platform

print ("\n-----------------------------------------------------")
print ("Platform flow use case 3: Platform creation, demonstration of various platform methods.\n")

# Create a client object -
client = vitis.create_client()

# Set workspace
date = datetime.now().strftime("%Y%m%d%I%M%S")
if(os_platform.system() == "Windows"):
   workspace = 'C:\\tmp\\workspace_'+date+'\\'
else:
    workspace = '/tmp/workspace_'+date+'/'
platform_name = "platform_test"

#Delete the workspace if already exists.
if (os.path.isdir(workspace)):
    shutil.rmtree(workspace)
    print(f"Deleted workspace {workspace}")

client.set_workspace(workspace)

# Get the path for xsa
xsa_dir = os.environ.get('XILINX_VITIS')

# Create platform, retarget fsbl
platform = client.create_platform_component(name = platform_name, hw = 'zcu102')
platform.report()
platform.retarget_fsbl()

# Add another domain
platform.add_domain(name = "standalone_a53_0", cpu = "psu_cortexa53_1", os = "standalone")

# Clone the platform, update the hw and build
platform2 = client.clone_component(platform_name, 'platform2')
platform2.report()
xsa_dir = os.environ.get('XILINX_VITIS')
xsa  = os.path.join(xsa_dir, 'data/embeddedsw/lib/fixed_hwplatforms/zcu102.xsa')
platform2.update_hw(xsa)
platform2.build()

# Regenerate bsp for the domain from platform
standalone_a53_0 = platform2.get_domain(name = "standalone_a53_0")
standalone_a53_0.regenerate()

# Remove boot bsp
platform2.remove_boot_bsp()

# Delete domain
client.delete_platform_component(platform_name)
client.delete_platform_component('platform2')

# # Delete the workspace
if (os.path.isdir(workspace)):
    shutil.rmtree(workspace, ignore_errors=True)
    print(f"Deleted workspace {workspace}")

# Close the client connection and terminate the vitis server
vitis.dispose()

