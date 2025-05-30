import spidev
import time

class MCP3002:
    def __init__(self, bus=0, device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 1300000  # 1 MHz (safe for 3.3V)
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
    lastpin = -1
    streak = 0
    try:
        while True:
            ch0 = adc.read_channel(0)
            v = ch0 / 1023.0 * 3.3
            #round to 2 decimal places
            v = round(v, 2)
            pin = -1
            #compare wich of the 8 possible pins

            if v > 0.02:
                if v <= 0.04:
                    pin = 6
                elif v <= 0.085:
                    pin = 1
                elif v <= 0.11:
                    pin = 2
                elif v < 0.13:
                    pin = 3
                elif v < 0.16:
                    pin = 4
                elif v < 0.24:
                    pin = 5
                elif v < 3:
                    pin = 8
                else:
                    pin = 7

            else:
                pin = -1

            if pin != -1:
                if lastpin == pin:
                    streak += 1
                else:
                    streak = 0
                if streak > 5:
                    print(f"CH0: {ch0:4d} V: {v:.2f} Pin: {pin} ")
                    
            lastpin = pin


            #print(f"CH0: {ch0:4d}", end='\r')
          
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        adc.close()