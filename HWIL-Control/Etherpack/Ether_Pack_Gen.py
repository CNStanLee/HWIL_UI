from scapy.all import Ether, sendp
import time
import random

# Function to generate a random 15-byte payload with a clock signal bit
def generate_payload_with_clock(length=16, clock_bit=0):
    # Create a payload with random bytes
    payload = bytes(random.getrandbits(8) for _ in range(length - 1))
    # Convert payload to a mutable bytearray
    payload = bytearray(payload)
    # Set the clock bit as the first bit of the first byte
    payload[0] = (payload[0] & 0xFE) | (clock_bit & 0x01)
    return bytes(payload)

# Initialize clock signal state
clock_signal = 0

# Set a specific Ethernet type, such as 0x0800 (IPv4) or 0xFFFF (undefined protocol for testing purposes)
while True:
    # Generate a payload with the current clock signal
    random_payload = generate_payload_with_clock(clock_bit=clock_signal)
    
    # Create a new Ethernet packet with the random payload
    ethernet_packet = Ether(dst="FF:FF:FF:FF:FF:FF", src="00:11:22:33:44:55", type=0xFFFF) / random_payload
    
    # Send the packet
    sendp(ethernet_packet, iface="WLAN")
    
    # Toggle the clock signal
    clock_signal ^= 1
    
    # Sleep for 1 second before sending the next packet
    time.sleep(1)
