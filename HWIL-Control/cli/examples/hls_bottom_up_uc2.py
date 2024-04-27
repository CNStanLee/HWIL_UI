#!/usr/bin/env python3
import vitis
import os
import time
import shutil
from datetime import datetime

print ("\n-----------------------------------------------------")
print ("HLS bottom-up flow component use case: Component creation and editing configuration file. \n")

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

# Create hls component
hls_test_comp = client.create_hls_component(name = comp_name)

# Print component information
hls_test_comp.report()

# Get config file object
cfg_path = os.path.join(workspace, comp_name, 'hls_config.cfg')
cfg_obj = client.get_config_file(cfg_path)

# Add kernel sources and test bench files
cfg_obj.set_value('',key = 'part', value='xcu250-figd2104-2L-e')
script_dir = os.path.dirname(os.path.abspath(__file__))
sources_dir = os.path.join(script_dir, "test_srcs")
cfg_obj.add_lines('hls',['syn.file='+sources_dir+'/krnl_vadd.cpp'])
cfg_obj.add_lines('hls',['tb.file='+sources_dir+'/krnl_vadd_test.cpp'])

# Adding top kernel function and clock
cfg_obj.add_lines('hls',['syn.top=krnl_vadd'])
cfg_obj.add_lines('hls',['clock=25'])

# Execute c-simulation on the component
hls_test_comp.execute('C_SIMULATION')

# Execute synthesis on the component
hls_test_comp.execute('SYNTHESIS')

# Execute co-simulation on the component
hls_test_comp.execute('CO_SIMULATION')

# Execute package on the component
hls_test_comp.execute('PACKAGE')

# Execute implementation on the component
hls_test_comp.execute('IMPLEMENTATION')

if (os.path.isdir(workspace)):
    shutil.rmtree(workspace, ignore_errors=True)
    print(f"Deleted workspace {workspace}")

# Close the client connection and terminate the vitis server
vitis.dispose()