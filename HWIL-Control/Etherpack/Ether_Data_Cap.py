from scapy.all import sniff, Ether
from vcd.writer import VCDWriter

# Specify the source MAC address to filter
target_mac = "00:11:22:33:44:55"  # Replace with the MAC address you want to monitor

# Open the VCD file and create a writer
vcd_file = open("network_data.vcd", "w")
vcd_writer = VCDWriter(vcd_file, timescale='1 ns', comment="Captured Network Payload Data")

# Define maximum payload size and register signals
payload_size = 64  # Set to the maximum payload size you expect

# Register signals for each bit of the first byte
bit_signals = {}
for bit_index in range(8):  # 8 bits in a byte
    signal_name = f'payload_byte_0_bit_{bit_index}'
    bit_signals[(0, bit_index)] = vcd_writer.register_var(scope='', name=signal_name, var_type='integer', size=1)

# Register signals for each byte from the second byte onward
data_signals = {}
for byte_index in range(1, payload_size):
    data_signals[byte_index] = vcd_writer.register_var(scope='', name=f'payload_byte_{byte_index}', var_type='integer', size=8)

# Timestamp for the VCD file (incrementing each time a packet is captured)
timestamp = 0

# Function to update the VCD file with captured data
def update_vcd(payload):
    global timestamp
    # Ensure the payload length does not exceed the defined size
    payload_length = min(len(payload), payload_size)
    
    # Process the first byte's bits
    if payload_length > 0:
        first_byte = payload[0]
        for bit_index in range(8):  # Process each bit of the first byte
            bit_value = (first_byte >> bit_index) & 1
            vcd_writer.change(bit_signals[(0, bit_index)], timestamp, bit_value)
    
    # Process remaining bytes as whole bytes
    for byte_index in range(1, payload_length):
        if byte_index < payload_size:
            vcd_writer.change(data_signals[byte_index], timestamp, payload[byte_index])
    
    timestamp += 1  # Increment the timestamp for each new data change
    vcd_writer.flush()  # Ensure the data is written to the file

# Callback function, executed when a matching packet is captured
def packet_callback(packet):
    if Ether in packet:
        ether_frame = packet[Ether]
        
        # Check if the source MAC address matches
        if ether_frame.src == target_mac:
            # Extract the entire payload
            payload = bytes(packet.payload)
            
            # Convert payload to hex format and print it
            payload_hex = payload.hex()
            print(f"Captured payload data from source MAC address {ether_frame.src}: {payload_hex}")
            
            # Save the payload to VCD (first byte as bits, others as bytes)
            update_vcd(payload)

# Start sniffing packets on the specified interface (replace 'WLAN' with your interface)
try:
    sniff(iface="WLAN", prn=packet_callback)
except KeyboardInterrupt:
    # Handle user interruption (Ctrl+C)
    print("Interrupted by user")
finally:
    # Ensure files are closed properly
    vcd_writer.close()
    vcd_file.close()
