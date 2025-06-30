# Purpose:
# manually calculate period for PAM4 
# currently unused / not needed. 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from extract_csv import extract_increment_rigol
from extract_csv import extract_increment_tek
from extract_csv import extract_voltage_rigol
from extract_csv import extract_voltage_tek

PAM4_PERIOD = 1 / (10.00e6 * 0.5)

# for lvds use 10.22e6, for new use 10.00

# for rigol
BOTTOM_TRESHHOLD = -0.001228
MID_TRESHOLD = 0
TOP_TRESHHOLD = 0.001228
# for tek
# BOTTOM_TRESHHOLD = -0.0047
# MID_TRESHOLD = 0.00098
# TOP_TRESHHOLD = 0.0068

def main():
    rigol = False
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
            sample_increment = extract_increment_rigol(line)
            print(sample_increment)
        else:
            # extract increment from tektronix .csv file
            n = 0
            while n < 7:
                line = file.readline()
                n += 1
            sample_increment = extract_increment_tek(line)
            print(sample_increment)
            while n < 1000:
                line = file.readline()
                n += 1

        data = []

        line = file.readline()
        # if data crosses 0, must be transitioning 
        if (rigol):
                current_voltage = extract_voltage_rigol(line)
        else:
                current_voltage = extract_voltage_tek(line)

        current_time = 0
        current_zero = None
        prev_zero = None
        zero_count = 0
        period_sum = 0
        lines_read = 0
        while line:
            prev_voltage = current_voltage
            line = file.readline()
            current_time += sample_increment
            lines_read += 1
            if (rigol):
                current_voltage = extract_voltage_rigol(line)
            else:
                current_voltage = extract_voltage_tek(line)
            # if abs of two nums less than abs of them seperate, one is pos one is neg or euq
            if current_voltage is not None and prev_voltage is not None:
                if (current_voltage > 0 and prev_voltage < 0) or (current_voltage < 0 and prev_voltage > 0) or current_voltage == 0 or prev_voltage == 0:
                    prev_zero = current_zero
                    current_zero = current_time
                    if prev_zero != None:
                        calc_period = current_zero - prev_zero
                        if calc_period < 1e-7:
                            zero_count += 1
                            period_sum += calc_period
                            data.append(calc_period)
                            print(calc_period)
                            print(current_voltage)
                            print(lines_read)
                    n = 0
                    while n < 10:
                        line = file.readline()
                        lines_read += 1
                        current_time += sample_increment
                        n += 1
            
        print(zero_count)
        print("calculated period")
        print(period_sum / zero_count)

        plt.hist(data, bins=100, color="pink")
        
        plt.xlabel("calculated period")
        plt.ylabel("count")
        plt.title("calculated period histogram")
        plt.show()

    
if __name__ == "__main__":
    main()