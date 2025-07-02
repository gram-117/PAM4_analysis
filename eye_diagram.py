# Purpose:
# creates eye diagram from raw oscope data

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from extract_csv import extract_increment_rigol
from extract_csv import extract_increment_tek
from extract_csv import extract_voltage_rigol
from extract_csv import extract_voltage_tek
from extract_csv import extract_voltage_tek_2chan

OUTPUT_CHART = True

PAM4_PERIOD = 1 / (10.00e6 * 0.5) # when VCO = 2500MHz and ndiv = 250
# for lvds use 10.22e6, now use 10.00e6

# number of samples to read from csv file
SAMPLES_TO_READ = 800000
# read offset: PAM4 signal is read at (1/2 + READ_OFFSET) witin half period (give as a fraction)
READ_OFFEST = 0
# phase offset between clk and pam4 (give in seconds), found using histogram
PHASE_OFFSET = 4.363e-8

#for tek
BOTTOM_TRESHHOLD = -0.01250
MID_TRESHOLD = -0.0005
TOP_TRESHHOLD = 0.0115

def main():
    rigol = False;
    # Get the current script directory (PAM4/)
    current_dir = Path(__file__).parent
    # Construct full paths
    input_file = (current_dir.parent / "oscope_data" / "tekfALL.csv").resolve()
    

    with open(input_file, "r") as infile:
        if (rigol):
            # extract increment from rigol .csv file
            # first line doesn't contain any data
            line = infile.readline()
            # second line contains times between samples
            line = infile.readline()
            sample_period = extract_increment_rigol(line)
            print(sample_period)
        else:
            # extract increment from tektronix .csv file
            n = 0
            while n < 7:
                line = infile.readline()
                n += 1
            sample_period = extract_increment_tek(line)
            print(sample_period)
            while n < 15:
                line = infile.readline()
                n += 1

        pam_voltage = []
        eye_times = []

        # read until current_clk is valid
        current_clk = None
        increments_read = 0
        while current_clk is None:
            line = infile.readline()
            result = extract_voltage_tek_2chan(line)
            if result is None:
                continue
            t, voltage_pam, voltage_clk = result
            if voltage_pam != None and voltage_clk != None and t != None:
                current_clk = voltage_clk
            increments_read += 1

        # calculate how many increments to skip to get to total offset
        # total offset = phase offset + optional additional offset 
        # could cause error if increments_read is large (but it should be 2)
        offset_increments = (PAM4_PERIOD / sample_period) * READ_OFFEST + (PHASE_OFFSET / sample_period) - increments_read
        n = 0
        while n < offset_increments:
            line = infile.readline()
            result = extract_voltage_tek_2chan(line)
            if result is None:
                continue
            t, voltage_pam, voltage_clk = result
            current_clk = voltage_clk
            if voltage_pam != None and voltage_clk != None and t != None:
                n += 1      
            

        # read PAM4 data on rising edge of clock (in the middle of each half PAM4 period)
        # falling edge of clock occurs when clk goes from < 0.12 to > 0.18
        # convert to voltages to binary and write to raw file
    
        
        count = 0
        if current_clk < 0.12:
            clk_low = True
        else:
            clk_low = False
        clk_count = 0 # for eye diagram have 4 clock cycles in view
        eye_time = 0;
        while line:
            line = infile.readline()
            result = extract_voltage_tek_2chan(line)
            if result is None:
                continue
            t, voltage_pam, current_clk = result
            if voltage_pam != None and voltage_clk != None and t != None:
                eye_time += sample_period
                eye_times.append(eye_time)
                pam_voltage.append(voltage_pam)
                # falling edge of clock  
                if current_clk < 0.12:
                    clk_low = True
                if clk_low and current_clk > 0.18:         
                    clk_count += 1
                if current_clk > 0.18:
                    clk_low = False
            count += 1
            if clk_count > 3:
                eye_time = 0
                clk_count = 0

            if count > SAMPLES_TO_READ:
                break
    

    plt.plot(eye_times, pam_voltage, linestyle='-', markersize=4, marker='', color="purple", alpha=.5, lw=.1)  
    
    plt.xlabel("time")
    plt.ylabel("voltage")
    plt.legend()
    plt.title("eye diagram")
    plt.grid(True)
    plt.show()



        
 
if __name__ == "__main__":
    main()