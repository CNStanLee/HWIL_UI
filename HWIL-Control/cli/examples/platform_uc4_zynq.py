#!/usr/bin/env python3
import vitis
import os
import time
import shutil
from datetime import datetime
import platform as os_platform

print ("\n-----------------------------------------------------")
print ("Platform flow use case 4: Creation of zynq platform, baremetal domain creation, generation and app component creation\n")

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

# Create platform
platform = client.create_platform_component(name = platform_name, hw = 'zc702')
platform.report()

# Add another domain
standalone_a9_0 = platform.add_domain(name = "standalone_a9_0", cpu = "ps7_cortexa9_0", os = "standalone")
platform.list_domains()

# Build the platform
platform.build()

# Create an application component with generated platform using template
platform_xpfm = client.get_platform(platform_name)
app_component = client.create_app_component(name = 'app_component1', platform = platform_xpfm, domain = 'standalone_a9_0', template = 'hello_world')

# Build app component
app_component.build()

# Delete domain
platform.delete_domain("standalone_a9_0")
client.delete_platform_component(platform_name)

# # Delete the workspace
if (os.path.isdir(workspace)):
    shutil.rmtree(workspace, ignore_errors=True)
    print(f"Deleted workspace {workspace}")

# Close the client connection and terminate the vitis server
vitis.dispose()


