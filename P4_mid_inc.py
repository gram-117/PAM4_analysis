# Purpose:
# plot edges and mid values for moderate sized data sets of PAM4 from metarock chip
# drift occurs due to imperfect PAM4 period value, sync up data with clock for future

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from extract_csv import extract_increment_rigol
from extract_csv import extract_increment_tek
from extract_csv import extract_voltage_rigol
from extract_csv import extract_voltage_tek

PAM4_PERIOD = 1 / (10.22e6 * 0.5)
#PAM4_PERIOD = 1.08e-7

SAMPLES_TO_READ = 1000000

# for rigol
BOTTOM_TRESHHOLD = -0.001228
MID_TRESHOLD = 0
TOP_TRESHHOLD = 0.001228
# for tek


def main():
    rigol = False;   
    # Get the current script directory (PAM4/)
    current_dir = Path(__file__).parent

    # Construct full paths
    input_file = (current_dir.parent / "oscope_data" / "tek0002CH3.csv").resolve()

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

        line = file.readline()
        # if data crosses 0, must be transitioning 
        if (rigol):
                current_voltage = extract_voltage_rigol(line)
        else:
                current_voltage = extract_voltage_tek(line)

        while line:
            prev_voltage = current_voltage
            line = file.readline()
            if (rigol):
                current_voltage = extract_voltage_rigol(line)
            else:
                current_voltage = extract_voltage_tek(line)
            # if abs of two nums less than abs of them seperate, one is pos one is neg
            if (abs(current_voltage + prev_voltage) < (abs(current_voltage) + abs(prev_voltage))):
                break
            # or if one of them is zero, break
            if current_voltage == 0:
                break
        current_time = 0

        # get to middle of rising edge
        mid_found = False
        while line and not mid_found:
            line = file.readline()
            if (rigol):
                current_voltage = extract_voltage_rigol(line)
            else:
                current_voltage = extract_voltage_tek(line)
            if current_voltage is not None:
                if current_time > (PAM4_PERIOD / 4):
                    data.append(current_voltage)
                    mid_found = True
            current_time += sample_period

        # add remaining data

        count = 0
        # for adjusting number of samples
        time_next_mid = current_time + PAM4_PERIOD / 2
        while line:
            # read until next middle
            while current_time < time_next_mid:
                line = file.readline()
                current_time += sample_period
                count += 1
            # add next middle
            if (rigol):
                current_voltage = extract_voltage_rigol(line)
            else:
                current_voltage = extract_voltage_tek(line)
            if current_voltage is not None:
                data.append(current_voltage)        
            time_next_mid += PAM4_PERIOD / 2
            if count > SAMPLES_TO_READ:
                break
        # freq of each bin, edge of bins
        plt.hist(data, bins=250, color="pink") 
        
    
        plt.xlabel("voltage")
        plt.ylabel("freq")
        plt.title("PAM4 raw histogram")
        plt.show()
        
if __name__ == "__main__":
    main()