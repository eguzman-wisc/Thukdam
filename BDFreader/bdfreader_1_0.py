# -*- coding: utf-8 -*-
#!/usr/bin/python

"""
File name: bdfreader.py
Author: Enrique Guzman
Date created: 3/25/2019
Date last modified: 3/25/2019
Version: 1.0.0
Credits: [Enrique Guzman, Dan Fitch, John V. Koger]
Copyright: 2019 Board of Regents of University of Wisconsin System

Description: BDFreader allows for the viewing of .BDF EEG data through the MNE EEG signal viewer.

Arguments:
    --infile=[filename.bdf] or a complete file path (e.g Y:/study/year/folder/filename.bdf)  
    
    
Required Libraries:
    MNE
"""

import mne
import sys
import os

# Measures how many arguments used when calling program, if none, throws error.
args = sys.argv
numargs = len(sys.argv) - 1     # -1 because [0] = self

if numargs == 0:
    print("No arguments provided. Must provide file to read\n")
    sys.exit(0)
    
# Checks if input file exists in current directory, or input path, if it doesn't throws error
input_file = next(s for s in args if 'infile' in s)
infile_string = input_file.split('=')
fname = infile_string[1]

if os.path.isabs(os.path.realpath(fname)) == True:
    fdir = os.path.dirname(fname)
    if os.path.dirname(fname) != '':
        os.chdir(fdir)      #changes current working directory to file directory if not already
    if os.path.isfile(os.path.basename(fname)) == False:
        print("Input file does not exist in indicated directory, please input a different file name, or a correct file path\n")
        sys.exit(0)
    fname = os.path.basename(fname)
elif os.path.isfile(fname) != True:
     print('Input file does not exist in current directory, please input different file name, or a complete file path (Use "/" not "\\")\n')
     sys.exit(0)  

# Reads raw data and begins finding beginning and end of each MMN and ABR events.
raw = mne.io.read_raw_edf(fname, verbose = False)
print("Input file overview:", raw)
raw.plot(duration=1.0, n_channels=len(raw.info['ch_names']), color={'eeg':'b', 'stim':'darkblue'}, scalings={'mag':0, 'grad':0, 'eeg':10e-5, 'eog':0, 'ecg':0, 'emg':0, 'ref_meg':0, 'misc':1e-3, 'stim':1, 'resp':1, 'chpi':1e-4}, title=fname)

raw_input("Press any key to continue... ")
