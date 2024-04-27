#!/usr/bin/env python3
import vitis
import os
import time
import shutil
from datetime import datetime

print ("\n-----------------------------------------------------")
print ("HLS bottom-up flow component use case: Creating component using already existing cfg. \n")

# Create a client object -
client = vitis.create_client()

# Set workspace
date = datetime.now().strftime("%Y%m%d%I%M%S")
workspace = '/tmp/workspace_'+date+'/'
comp_name = "hls_component_test"

#Delete the workspace if already exists.
if (os.path.isdir(workspace)):
    shutil.rmtree(workspace)
    print(f"Deleted workspace {workspace}")

client.set_workspace(workspace)

# Get config file object
script_dir = os.path.dirname(os.path.abspath(__file__))
cfg_path = os.path.join(script_dir, 'test_srcs/hls_config.cfg')

# Create hls component with existing cfg file
hls_test_comp = client.create_hls_component(name = comp_name, cfg_file = cfg_path)

# Print component information
hls_test_comp.report()

# Run synthesis and co-sim on hls component
hls_test_comp.execute('SYNTHESIS')

if (os.path.isdir(workspace)):
    shutil.rmtree(workspace, ignore_errors=True)
    print(f"Deleted workspace {workspace}")

# Close the client connection and terminate the vitis server
vitis.dispose()