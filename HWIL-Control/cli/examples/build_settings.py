#!/usr/bin/env python3
import vitis
import os
import time
import shutil
from datetime import datetime
import platform as os_platform

print ("\n-----------------------------------------------------")
print ("C/C++ build settings : Demo to edit C/C++ build settings.\n")

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
platform = client.create_platform_component(name = platform_name, hw = 'zcu102', domain_name = "standalone_a53_0", cpu = "psu_cortexa53_1", os = "standalone")
platform.report()

# Get the domain
standalone_a53_0 = platform.get_domain('standalone_a53_0')
standalone_a53_0.report()

# Edit domain options
sources_dir = os.path.join(xsa_dir, "data/emulation/platforms/zynqmp/sw/")
standalone_a53_0.add_qemu_args('PS', sources_dir+'a53_standalone/qemu/qemu_args.txt')
platform.build()

# Create an application component with generated platform using template
platform_xpfm = client.get_platform(platform_name)
app_component = client.create_app_component(name = 'app_component1', platform = platform_xpfm, domain = 'standalone_a53_0', template = 'hello_world')

# Get build settings
print("\nApplication configuration:")
app_component.get_app_config()

# Get info regarding various build settings
print("=======================================================================")
print("\nConfig information regarding various keys")
print("USER_COMPILE_WARNINGS_AS_ERRORS = ",app_component.get_config_info(key = 'USER_COMPILE_WARNINGS_AS_ERRORS'),"\n")
print("USER_COMPILE_DEBUG_LEVEL = ",app_component.get_config_info(key = 'USER_COMPILE_DEBUG_LEVEL'),"\n")
print("USER_INCLUDE_DIRECTORIES = ",app_component.get_config_info(key = 'USER_INCLUDE_DIRECTORIES'),"\n")

# Edit build settings
app_component.set_app_config(key = 'USER_COMPILE_WARNINGS_AS_ERRORS',values = 'TRUE')
app_component.set_app_config(key = 'USER_COMPILE_DEBUG_LEVEL', values = '-g1')
app_component.set_app_config(key = 'USER_INCLUDE_DIRECTORIES', values = '/tmp/inc_dir1')

# Print changed settings
print("=======================================================================")
print("\nConfig information of changed keys")
print("USER_COMPILE_WARNINGS_AS_ERRORS = ",app_component.get_app_config(key = 'USER_COMPILE_WARNINGS_AS_ERRORS'))
print("USER_COMPILE_DEBUG_LEVEL = ",app_component.get_app_config(key = 'USER_COMPILE_DEBUG_LEVEL'))
print("USER_INCLUDE_DIRECTORIES = ",app_component.get_app_config(key = 'USER_INCLUDE_DIRECTORIES'))

print("Appending and removing values from the config settings:")
app_component.append_app_config(key = 'USER_INCLUDE_DIRECTORIES', values = '/tmp/inc_dir2')
print('Value after appendingl')
app_component.get_app_config(key = 'USER_INCLUDE_DIRECTORIES')
app_component.remove_app_config(key = 'USER_INCLUDE_DIRECTORIES', values = '/tmp/inc_dir1')
print('Value after removing')
app_component.get_app_config(key = 'USER_INCLUDE_DIRECTORIES')


# Delete the component
client.delete_component('app_component1')

# Delete domain
client.delete_platform_component(platform_name)

# # Delete the workspace
if (os.path.isdir(workspace)):
    shutil.rmtree(workspace, ignore_errors=True)
    print(f"Deleted workspace {workspace}")

# Close the client connection and terminate the vitis server
vitis.dispose()