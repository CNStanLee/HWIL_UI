#!/usr/bin/env python3
import vitis
import os
import time
import shutil
from datetime import datetime
import platform as os_platform

print ("\n-----------------------------------------------------")
print ("Platform flow use case 1: Platform creation, linux domain creation, generation and app component creation\n")

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

# Create platform
platform = client.create_platform_component(name = platform_name, hw = 'zcu102', cpu = "psu_cortexa53", os = "linux", domain_name = "linux_a53")
platform.report()

# List all the domains in the platform and build the platform
platform.list_domains()
platform.build()

# Create an app component with generated platform
platform_xpfm = client.get_platform(platform_name)
app_component = client.create_app_component(name = 'app_component1', platform = platform_xpfm, domain = 'linux_a53')

# Disable to import custom sources to application component.
# app_component.import_files(from_loc = <sources_dir>, files = ['helloworld.c'])

# Build an application component
app_component.build()

# Delete domain
platform.delete_domain("linux_a53")
client.delete_platform_component(platform_name)

# # Delete the workspace
if (os.path.isdir(workspace)):
    shutil.rmtree(workspace, ignore_errors=True)
    print(f"Deleted workspace {workspace}")

# Close the client connection and terminate the vitis server
vitis.dispose()


