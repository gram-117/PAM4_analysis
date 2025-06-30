# Purpose:
# take large amount of raw/unprocessed PAM4 oscilloscope data and decodes into binary

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
SAMPLES_TO_READ = 10000000
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
        time = []
        clk_voltage = []
        mid_values = []
        mid_time = []

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
                pam_voltage.append(voltage_pam)
                clk_voltage.append(voltage_clk)
                time.append(t)            
            n += 1

        # read PAM4 data on rising edge of clock (in the middle of each half PAM4 period)
        # rising clock occurs when clk goes from below 0.15V to above 0.15V
        # convert to voltages to binary and write to raw file
        output_file = (current_dir.parent / "output" / "raw_out.txt").resolve()
        with open(output_file, "w") as raw_out:
            count = 0
            if current_clk < 0.12:
                clk_low = True
            else:
                clk_low = False
            while line:
                line = infile.readline()
                result = extract_voltage_tek_2chan(line)
                if result is None:
                    continue
                t, voltage_pam, current_clk = result
                if voltage_pam != None and voltage_clk != None and t != None:
                    pam_voltage.append(voltage_pam)
                    clk_voltage.append(current_clk)
                    time.append(t)
                    if current_clk < 0.12:
                        clk_low = True
                    if clk_low and current_clk > 0.18: # falling edge of clock, READ PAM4
                        # optional offset from middle of half period                       
                        # convert voltage into binary values based off threshholds   
                        mid_values.append(voltage_pam)
                        mid_time.append(t)
                        if voltage_pam > TOP_TRESHHOLD:
                            raw_out.write("11")
                        elif voltage_pam > MID_TRESHOLD:
                            raw_out.write("01")
                        elif voltage_pam > BOTTOM_TRESHHOLD:
                            raw_out.write("10")
                        else:
                            raw_out.write("00")
                    if current_clk > 0.18:
                        clk_low = False
                count += 1
                if count > SAMPLES_TO_READ:
                    break
    
    # break into odd and even and show same seq. 

    # Construct full paths
    input_file = (current_dir.parent / "output" / "raw_out.txt")
    output_file_even = (current_dir.parent / "output" / "even_bits.txt")
    output_file_odd = (current_dir.parent / "output" / "odd_bits.txt")
    

    # first bit is classified as bit 0, first bit is even
    with open(input_file, "r") as infile, open(output_file_even, "w") as outfile_even, open(output_file_odd, "w") as outfile_odd:
        chunk_size = 127 # size of prbs7 sequence
        outfile_even.write("Even bits:\n")
        outfile_odd.write("Odd bits:\n")

        bit = infile.read(1)
        count = 0
        while bit != '':
            if count % 2 == 0:
                outfile_even.write(bit)
            else:
                outfile_odd.write(bit)
            count += 1
            bit = infile.read(1)
            if (count % (chunk_size * 2) == 0): # new line every 127 bits * 2 (even and odd)
                outfile_even.write("\n")
                outfile_odd.write("\n")
                


    if OUTPUT_CHART:
        fig, ax1 = plt.subplots()
        ax1.plot(time, clk_voltage, linestyle='-', alpha=1, color="pink", zorder=1, label="clk_voltage")
        ax1.set_ylabel("clk (V)", color="pink")
        ax1.tick_params(axis='y', labelcolor="pink")

        ax2 = ax1.twinx()
        ax2.plot(time, pam_voltage, linestyle='-', alpha=1, color="green", zorder=2, label="pam_voltage")
        ax2.set_ylabel("PAM4 (V)", color="green")
        ax2.tick_params(axis='y', labelcolor="green")
        xlim = ax2.get_xlim()
        ax2.hlines(y=[-0.01250, -0.0005, 0.0115], xmin=xlim[0], xmax=xlim[1], colors='b', linestyles='-')


        ax2.scatter(mid_time, mid_values, color="purple", s=8, label="mid", zorder=3) # mid markers

        ax1.set_xlabel("Time (s)" )
        plt.title("clk and PAM4 vs time")

        plt.show()

        plt.plot(time, pam_voltage, linestyle='-', alpha=1, markersize=4, marker='', color="green", zorder=2) # all data
        plt.plot(time, clk_voltage, linestyle='-', alpha=1, markersize=4, marker='', color="pink", zorder=1) # all data
         


    # histogram to make sure all middle values dont overlap
    # plt.hist(mid_values, bins=250, color="pink") 
    

    # plt.xlabel("voltage")
    # plt.ylabel("count")
    # plt.title("PAM4 mid histogram")
    # plt.show()
        
 
if __name__ == "__main__":
    main()