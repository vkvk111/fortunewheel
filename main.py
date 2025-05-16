import spidev
import time

class MCP3002:
    def __init__(self, bus=0, device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 1000000  # 1 MHz (safe for 3.3V)
        self.spi.mode = 0b00  # SPI Mode 0 (CPOL=0, CPHA=0)
        
    def read_channel(self, channel):
        """Read MCP3002 with correct 2-byte SPI transaction."""
        if channel not in [0, 1]:
            raise ValueError("MCP3002 only has channels 0 or 1")

        # MCP3002 expects:
        # Byte 1: [Start (1), SGL/DIFF (1), CH (0/1), Don't Care (0000)]
        # Byte 2: [Don't Care (xxxx xxxx)]
        cmd = 0b01100000 | (channel << 4)  # Start=1, SGL=1, CH=0/1, D0-D3=0
        reply = self.spi.xfer2([cmd, 0x00])  # Only 2 bytes!

        # The 10-bit result is in:
        # - reply[0] (bits 1-0 = B9-B8)
        # - reply[1] (bits 7-0 = B7-B0)
        value = ((reply[0] & 0b00000011) << 8) | reply[1]
        return value
    
    def close(self):
        self.spi.close()

if __name__ == "__main__":
    adc = MCP3002()
    try:
        while True:
            ch0 = adc.read_channel(0)
            print(f"CH0: {ch0:4d}", end='\r')
          
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        adc.close()