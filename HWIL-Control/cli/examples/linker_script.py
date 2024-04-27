#!/usr/bin/env python3
import vitis
import os
import time
import shutil
from datetime import datetime
import platform as os_platform

print ("\n-----------------------------------------------------")
print ("Linker script editing : Example to edit various fields of linker script.\n")

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

# Build the platform
platform.build()

# Create an application component with generated platform using template
platform_xpfm = client.get_platform(platform_name)
app_component = client.create_app_component(name = 'app_component1', platform = platform_xpfm, domain = 'standalone_a53_0', template = 'hello_world')

# Get the linker script from the app component
ld_file = app_component.get_ld_script()

# Regenerate ld file with default values
ld_file.regenerate()

# Get and set the stack size and heap size
print("Stack size :",ld_file.get_stack_size())
print("Heap size :",ld_file.get_heap_size())
ld_file.set_stack_size('0x4000')
ld_file.set_heap_size('0x4000')
print("New stack size :",ld_file.get_stack_size())
print("New heap size :",ld_file.get_heap_size())

# Add and update a memory region
ld_file.add_memory_region(name = 'psu_ddr_3', base_address = '0x900000000', size = '0x4000000')
ld_file.update_memory_region(name = 'psu_ddr_3', base_address = '0x900000000', size = '0x5000000')
ld_file.get_memory_regions()

# Update ld section
ld_file.get_ld_sections()
ld_file.update_ld_section(region = 'psu_ddr_1', section = '.stack')

# Build the component with the updated linker script
app_component.build()

# Delete the component
client.delete_component('app_component1')

# Delete domain
client.delete_platform_component(platform_name)

# Delete the workspace
if (os.path.isdir(workspace)):
    shutil.rmtree(workspace, ignore_errors=True)
    print(f"Deleted workspace {workspace}")

# Close the client connection and terminate the vitis server
vitis.dispose()