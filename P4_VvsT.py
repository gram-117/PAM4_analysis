# Purpose:
# take large amount of raw/unprocessed PAM4 and clk oscilloscope data and plots onto V vs T chart
# adds markers for middle of half period (where value would be read)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from extract_csv import extract_increment_rigol
from extract_csv import extract_increment_tek
from extract_csv import extract_voltage_rigol
from extract_csv import extract_voltage_tek


PAM4_PERIOD = 1 / (10.00e6 * 0.5)
#PAM4_PERIOD = 1.08e-7
# for lvds use 10.22e6, for new use 10.00

SAMPLES_TO_READ = 10000

# for rigol
BOTTOM_TRESHHOLD = -0.001228
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
        mid_data = []
        mid_time = []
        rising_data = []
        rising_time = []

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
        data.append(current_voltage)
        time.append(current_time)
        rising_data.append(current_voltage)
        rising_time.append(current_time)

        # get to middle of rising edge
        mid_found = False
        while line and not mid_found:
            line = file.readline()
            if (rigol):
                current_voltage = extract_voltage_rigol(line)
            else:
                current_voltage = extract_voltage_tek(line)
            if current_voltage is not None:
                data.append(current_voltage)
                time.append(current_time)
                if current_time > (PAM4_PERIOD / 4):
                    mid_data.append(current_voltage)
                    mid_time.append(current_time)
                    mid_found = True
            current_time += sample_period

        # add remaining data

        count = 0
        # for adjusting number of samples
        time_next_mid = current_time + PAM4_PERIOD / 2
        next_rising_edge = current_time + PAM4_PERIOD / 4 
        while line:
            # add all data to data add mid data to mid
            # read until rising edge
            while current_time < next_rising_edge:
                line = file.readline()
                if (rigol):
                    current_voltage = extract_voltage_rigol(line)
                else:
                    current_voltage = extract_voltage_tek(line)
                if current_voltage is not None:
                    data.append(current_voltage)
                    time.append(current_time)
                current_time += sample_period
                count += 1
            # add rising edge 
            line = file.readline()
            if (rigol):
                current_voltage = extract_voltage_rigol(line)
            else:
                current_voltage = extract_voltage_tek(line)
            if current_voltage is not None:
                data.append(current_voltage)
                time.append(current_time)
                rising_data.append(current_voltage)
                rising_time.append(current_time)
            # read until next middle
            while current_time < time_next_mid:
                line = file.readline()
                if (rigol):
                    current_voltage = extract_voltage_rigol(line)
                else:
                    current_voltage = extract_voltage_tek(line)
                if current_voltage is not None:
                    data.append(current_voltage)
                    time.append(current_time)
                current_time += sample_period
                count += 1
            # add next middle
            line = file.readline()
            if (rigol):
                current_voltage = extract_voltage_rigol(line)
            else:
                current_voltage = extract_voltage_tek(line)
            if current_voltage is not None:
                data.append(current_voltage)
                time.append(current_time)
                mid_data.append(current_voltage)
                mid_time.append(current_time)           
            time_next_mid += PAM4_PERIOD / 2
            next_rising_edge += PAM4_PERIOD / 2
            if count > SAMPLES_TO_READ:
                break
    

        plt.scatter(mid_time, mid_data, label="mid", zorder=2) # mid markers
        plt.scatter(rising_time, rising_data, label="new period", zorder=3, color="red") # rising edge markers
        plt.plot(time, data, linestyle='-', alpha=1, markersize=4, marker='', color="pink", zorder=1) # all data
        
        plt.xlabel("time")
        plt.ylabel("voltage")
        plt.legend()
        plt.title("PAM4 V vs T (using prev calculated period)")
        plt.grid(True)
        plt.show()
if __name__ == "__main__":
    main()