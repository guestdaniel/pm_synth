#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@title: pm_synth_defaults.py
@date: 08/17/2016
@author: Daniel Guest
@purpose: Provide a defaults file that is accesible to all other pm_synth
          files. Changing a default here will change the operation of the
          pm_synth.
"""
# ----- SYNTH_THREAD PARAMETERS -----
BLOCK_LEN = 50

# ----- SYNTH PARAMETERS -----
FS = 20000
N_OP = 6
N_GEN = 1

# ----- BUFFER PARAMETERS -----
BUFFER_LEN = 50

# ----- OP PARAMETERS ----- 
OP_DELAY_LEN = FS*2
LFO_FREQ = 5

# ----- GENERATOR PARAMETERS -----
WINDOW_TYPE = "hamming"
MAX_GRAINS_PER_GEN = 50

CURR_GEN_LAG = 0
MAX_LAG_LEN = OP_DELAY_LEN*0.5

CURR_LAG_JITTER = 0
MIN_LAG_JITTER = 0
MAX_LAG_JITTER = 500

CURR_GRAIN_LEN_JITTER = 0
MIN_GRAIN_LEN_JITTER = 0
MAX_GRAIN_LEN_JITTER = 500
CURR_GRAIN_LEN = 150
MIN_GRAIN_LEN = 5
MAX_GRAIN_LEN = 5000

CURR_GEN_PERIOD_JITTER = 0
MIN_GEN_PERIOD_JITTER = 0
MAX_GEN_PERIOD_JITTER = 500
CURR_GEN_PERIOD = 500
MIN_GEN_PERIOD = 10
MAX_GEN_PERIOD = 5000