# Purpose:
# take large amount of raw/unprocessed PAM4 and clk oscilloscope data and plots onto V vs T chart

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from extract_csv import extract_increment_rigol
from extract_csv import extract_increment_tek
from extract_csv import extract_voltage_rigol
from extract_csv import extract_voltage_tek
from extract_csv import extract_voltage_tek_2chan


PAM4_PERIOD = 1 / (10.00e6 * 0.5)
#PAM4_PERIOD = 1.08e-7
# for lvds use 10.22e6, for new use 10.00

SAMPLES_TO_READ = 5000

# for rigol
BOTTOM_TRESHHOLD = -0.00125
MID_TRESHOLD = 0
TOP_TRESHHOLD = 0.001228
# for tek


def main():
    rigol = False;

    # Get the current script directory (PAM4/)
    current_dir = Path(__file__).parent
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
        time = []
        clk = []

        current_time = 0
        count = 0
        while line:
            line = file.readline()
            result = extract_voltage_tek_2chan(line)
            if result is None:
                continue
            t, voltage_pam, voltage_clk= result
            if voltage_pam != None and voltage_clk != None and t != None:
                data.append(voltage_pam)
                clk.append(voltage_clk)
                time.append(t)
            current_time += sample_period
            count += 1
            if count > SAMPLES_TO_READ:
                break

    

        plt.plot(time, data, linestyle='-', alpha=1, markersize=4, marker='', color="green", zorder=2) # all data
        plt.plot(time, clk, linestyle='-', alpha=1, markersize=4, marker='', color="pink", zorder=1) # all data
        
        plt.xlabel("time")
        plt.ylabel("voltage")
        plt.title("PAM4 and clk vs T")
        plt.grid(True)
        plt.show()
if __name__ == "__main__":
    main()