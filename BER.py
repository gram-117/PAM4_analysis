# Purpose:
# take in a raw PAM4 out, find the lock sequence, then compare to a expected sequence

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from extract_csv import extract_increment_rigol
from extract_csv import extract_increment_tek
from extract_csv import extract_voltage_rigol
from extract_csv import extract_voltage_tek
from extract_csv import extract_voltage_tek_2chan


SAMPLES_TO_READ = 500000


def main():
    total_samples_read = 0
    total_errors = 0
    filename = "raw_out.txt"

    # Get the current script directory (PAM4/)
    current_dir = Path(__file__).parent
    # Construct full paths
    input_file = (current_dir.parent / "output" / "raw_out.txt").resolve()

    lock_on_sequence = "01110011010110"
    prbs_sequence = "11000011101101101010011100011101111001010011100111101111001011001001101000111101001000001100010111111100000100110011111110100101100110001011100001111101100000011001001010101101000010001001000000101000010101011101010001000110111010111110001101110011010110"
    with open(input_file, "r") as infile:
        # when key matches lock, begin BER
        key_sequence = infile.read(14)
        while key_sequence != lock_on_sequence:
            key_sequence = key_sequence[1:] + infile.read(1)    
 
        # found lock, begin BER
        while True:
            # read next 254 bits
            data = infile.read(254)
            
            if len(data) < 254:
                for i in range(len(data)):
                    if data[i] != prbs_sequence[i]:
                        total_errors += 1
                break
            total_samples_read += 254
            # compare to prbs sequence
            errors = 0
            for i in range(254):
                if data[i] != prbs_sequence[i]:
                    total_errors += 1
            if total_samples_read > SAMPLES_TO_READ:
                break
            
    print("Total samples read: %d" % total_samples_read)
    print("Total errors: %d" % total_errors)
    print("Bit error rate: %f" % (total_errors / total_samples_read))
        # read PAM4 data on rising edge of clock (in the middle of each half PAM4 period)
        # rising clock occurs when clk goes from below 0.15V to above 0.15V
        # convert to voltages to binary and write to raw file
                
 
if __name__ == "__main__":
    main()