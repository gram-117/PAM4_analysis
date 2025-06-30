# Purpose:
# takes edges % PAM4 period to give phase shift 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from extract_csv import extract_increment_rigol
from extract_csv import extract_increment_tek
from extract_csv import extract_voltage_rigol
from extract_csv import extract_voltage_tek
from extract_csv import extract_voltage_tek_2chan


# 10.22e6 for lvds data
PAM4_PERIOD = 1 / (10.00e6 * 0.5)
SAMPLE_LIMIT = 1000000
# for rigol
BOTTOM_TRESHHOLD = -0.001228
MID_TRESHOLD = 0
TOP_TRESHHOLD = 0.001228
# for tek
# BOTTOM_TRESHHOLD = -0.0047
# MID_TRESHOLD = 0.00098
# TOP_TRESHHOLD = 0.0068

def main():
    rigol = False;

    # Get the current script directory (PAM4/)
    current_dir = Path(__file__).parent
    input_file = (current_dir.parent / "oscope_data" / "tekfALL.csv").resolve()

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
            while n < 15:
                line = file.readline()
                n += 1

        phase_shift = []

        line = file.readline()
        # get first voltage value
        if (rigol):
                current_voltage = extract_voltage_rigol(line)
        else:
            result = extract_voltage_tek_2chan(line)
            t, voltage_pam, voltage_clk = result
            if voltage_pam != None:
                current_voltage = voltage_pam

        # if data crosses 0, must be transitioning 
        total_phase = 0
        phase_count = 0
        current_time = 0
        sample_points = 0
        while line:
            prev_voltage = current_voltage
            line = file.readline()
            sample_points += 1
            if (rigol):
                current_voltage = extract_voltage_rigol(line)
            else:
                result = extract_voltage_tek_2chan(line)
                if result is None:
                    continue
                t, voltage_pam, voltage_clk = result
                if voltage_pam != None:
                    current_voltage = voltage_pam
            # if abs of two nums less than abs of them seperate, one is pos one is neg
            if current_voltage is not None:
                if (abs(current_voltage + prev_voltage) < (abs(current_voltage) + abs(prev_voltage))) or current_voltage == 0:
                    # add phase shift to data
                    phase_shift.append(current_time % (PAM4_PERIOD / 2))
                    total_phase += current_time % (PAM4_PERIOD / 2)
                    phase_count += 1
            current_time += sample_increment
            if (SAMPLE_LIMIT < sample_points):
                 break            
    

        plt.hist(phase_shift, bins=200, color="pink")
        
        plt.xlabel("rising edges % p4")
        plt.ylabel("count")
        plt.title("rising edges % p4 histogram")
        plt.show()
        print(str(total_phase / phase_count))
if __name__ == "__main__":
    main()