# !/usr/bin/env python3
import vitis
import os
import shutil
from datetime import datetime
import platform as os_platform

print ("\n-----------------------------------------------------")
print ("Demo for setting preferences on various levels \n")

# Create a client object -
# It starts Vitis Server
# Create a client object
# Establishes a connection between the server and the client
client = vitis.create_client()

# Set workspace
date = datetime.now().strftime("%Y%m%d%I%M%S")
if(os_platform.system() == "Windows"):
    workspace = 'C:\\tmp\\workspace_{date}'
else:
    workspace = '/tmp/workspace_{date}'

app_name = "create-app"
prjLocation = os.path.join(workspace, app_name)
client.set_workspace(path=workspace)
print("Workspace set to : " + workspace)

print("Setting user preferences")

# Set user preferences
client.set_preference(level = 'USER', device='VERSAL', key='KERNELIMAGE',value='/proj/xbuilds/2022.1_daily_latest/internal_platforms/sw/versal/xilinx-versal/Image')
print('\n',client.get_preference(level = 'USER', device='VERSAL', key='KERNELIMAGE'))

client.set_preference(level='USER' , device='ZYNQMP', key='SYSROOT',value='/proj/xbuilds/2022.1_daily_latest/internal_platforms/sw/zynqmp/xilinx-zynqmp-common-v2022.1/sysroots/cortexa72-cortexa53-xilinx-linux/')
print('\n',client.get_preference(level='USER' , device='ZYNQMP', key='SYSROOT'))

client.set_preference(level='USER', device='ZYNQ', key='ROOTFS',value = '/proj/xbuilds/2022.1_daily_latest/internal_platforms/sw/zynq/xilinx-zynq-common-v2022.1/rootfs.ext4')
print('\n',client.get_preference(level='USER', device='ZYNQ', key='ROOTFS'))

# Set workspace preferences
workspace_preference_location = workspace+'/.theia/settings.json'
os.mkdir(workspace+'/.theia')
f = open(workspace_preference_location, "a")
f.write("{}")
f.close()

print("Setting workspace preferences")

client.set_preference(level = 'WORKSPACE', device='VERSAL', key='KERNELIMAGE',value='/proj/xbuilds/2022.2_daily_latest/internal_platforms/sw/versal/xilinx-versal/Image')
print('\n',client.get_preference(level = 'WORKSPACE', device='VERSAL', key='KERNELIMAGE'))

client.set_preference(level='WORKSPACE' , device='ZYNQMP', key='SYSROOT',value='/proj/xbuilds/2022.2_daily_latest/internal_platforms/sw/zynqmp/xilinx-zynqmp-common-v2022.2/sysroots/cortexa72-cortexa53-xilinx-linux/')

client.set_preference(level='WORKSPACE', device='ZYNQ', key='ROOTFS',value = '/proj/xbuilds/2022.2_daily_latest/internal_platforms/sw/zynq/xilinx-zynq-common-v2022.2/rootfs.ext4')

# Print contents of .theia/settings.json
print("Contents of /.theia/settings.json")
with open(workspace_preference_location, 'r') as pref:
    data = pref.readlines()

for d in data:
    print(d,'\n')

#Clean the workspace directory
# if (os.path.isdir(workspace)):
#     shutil.rmtree(workspace)
#     print(f"Deleted Workspace {workspace}")