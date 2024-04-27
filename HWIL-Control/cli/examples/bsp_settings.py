#!/usr/bin/env python3
import vitis
import os
import time
import shutil
from datetime import datetime
import platform as os_platform

print ("\n-----------------------------------------------------")
print ("Platform flow use case 3: Demonstration for BSP editing.\n")

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

# Create a standlone domain and edit the bsp settings
standalone_a53_0 = platform.add_domain(name = "standalone_a53_0", cpu = "psu_cortexa53_1", os = "standalone")
standalone_a53_0.report()

# Add, get libraries and library parameters
print("Applicable libraries:")
standalone_a53_0.get_applicable_libs()
print("Adding xilskey library..")
standalone_a53_0.set_lib('xilskey')
print("List of configured libraries:")
standalone_a53_0.get_libs()
standalone_a53_0.remove_lib("xilskey")

print("===============================================================")
print("List of xiltimer parameters")
standalone_a53_0.list_params('lib','xiltimer')
print("Value of XILTIMER_tick_timer:")
standalone_a53_0.get_config('lib','XILTIMER_tick_timer','xiltimer')
standalone_a53_0.set_config('lib','XILTIMER_tick_timer','psu_ttc_1','xiltimer')
print("Value of XILTIMER_tick_timer after setting:")
standalone_a53_0.get_config('lib','XILTIMER_tick_timer','xiltimer')

# Set os parameter
print("===============================================================")
print("Value of standalone_stdout:")
standalone_a53_0.get_config('os','standalone_stdout')
standalone_a53_0.set_config('os','standalone_stdout','psu_uart_1')
print("Value of standalone_stdout after setting:")
standalone_a53_0.get_config('os','standalone_stdout')

# Delete domain
platform.delete_domain("linux_a53")
platform.delete_domain("standalone_a53_0")
client.delete_platform_component(platform_name)

# # Delete the workspace
if (os.path.isdir(workspace)):
    shutil.rmtree(workspace, ignore_errors=True)
    print(f"Deleted workspace {workspace}")

# Close the client connection and terminate the vitis server
vitis.dispose()
