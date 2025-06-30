# Purpose:
# take large amount of raw/unprocessed PAM4 oscilloscope data and plots onto histogram 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from extract_csv import extract_increment_rigol
from extract_csv import extract_increment_tek
from extract_csv import extract_voltage_rigol
from extract_csv import extract_voltage_tek
from extract_csv import extract_voltage_tek_2chan

def main():
    rigol = False;   
    # Get the current script directory (PAM4/)
    current_dir = Path(__file__).parent

    # Construct full paths
    input_file = (current_dir.parent / "oscope_data" / "tek0003ALL.csv").resolve()

    with open(input_file, "r") as file:
        if (rigol):
            # extract increment from rigol .csv file
            # first line doesn't contain any data
            line = file.readline()
            # second line contains times between samples
            line = file.readline()
            sample_period = extract_increment_rigol(line)
            print(sample_period)
        else:
            # extract increment from tektronix .csv file
            n = 0
            while n < 7:
                line = file.readline()
                n += 1
            sample_period = extract_increment_tek(line)
            print(sample_period)
            while n < 15:
                line = file.readline()
                n += 1

        data = []
        while line:
            line = file.readline()
            result = extract_voltage_tek_2chan(line)
            if result is None:
                continue
            t, voltage_pam, voltage_clk = result
            voltage = voltage_pam
            if voltage is not None:
                data.append(voltage)
        # freq of each bin, edge of bins
        plt.hist(data, bins=250, color="pink") 
        
    
        plt.xlabel("voltage")
        plt.ylabel("freq")
        plt.title("PAM4 raw histogram")
        plt.show()
if __name__ == "__main__":
    main()