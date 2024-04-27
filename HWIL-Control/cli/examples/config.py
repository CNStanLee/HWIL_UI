#!/usr/bin/env python3
import vitis

print ("\n-----------------------------------------------------")
print ("Config file APIs \n")

# Create a client object -
# It starts Vitis Server
# Create a client object
# Establishes a connection between the server and the client
client = vitis.create_client()

cfg = client.get_config_file(path = "test_srcs/sample_cfg.cfg")
sections = cfg.get_sections()

# Printing app object info
print("\n get_sections:")
print(sections)


# Close client and terminate the vitis server
vitis.dispose()
