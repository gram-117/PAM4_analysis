import numpy as np
import pandas as pd

def extract_increment_rigol(line):
    # line is in form X,CH2,Start,Increment, where increment is sample period
    parts = line.split(",")
    return float(parts[3])

def extract_increment_tek(line):
    parts = line.split(",")
    return float(parts[1])

def extract_voltage_rigol(line):
    # line is in form num,data,   
    parts = line.split(",")
    if len(parts) < 2 or parts[1].strip() == '':
        return None  # Or raise an error or skip this line
    return float(parts[1])

def extract_voltage_tek(line):
    #line is in form time, voltage where time approaches 0
    parts = line.split(",")
    if len(parts) < 2 or parts[1].strip() == '':
        return None  # Or raise an error or skip this line
    return float(parts[1])

def extract_voltage_tek_2chan(line):
    #line is in form time, voltage(PAM4), voltage(clk) where time approaches 0
    parts = line.split(",")
    if len(parts) < 3 or parts[2].strip() == '':
        return None  # Or raise an error or skip this line
    return float(parts[0]), float(parts[1]), float(parts[2])