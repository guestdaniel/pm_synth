#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@title: pm_synth.py
@date: 08/13/16
@author: Daniel Guest
@purpose: Provide classes to create phase modulation synthesizer.
"""

import numpy as np
import math

class Synth(object):
    
    def __init__(self, fs=10000, inv_samp=50, n_op=6):
        
        # Initialize parameters
        self.fs = fs
        self.inv_samp = inv_samp
        self.output = [0]*self.inv_samp
        self.current_inv = 0
        self.amp_val = 0
        self.n_op = 6
        
        # Initialize components
        self.ops = []
        for op in range(self.n_op):
            self.ops.append(Operator(self))
        self.output_module = Output(self)
        
        # Choose algorithm
        self.algorithm = a1(ops=self.ops, output_module=self.output_module)
        self.algorithm.implement()
        
    def synth(self):
        for op in range(self.n_op):
            self.ops[op].run()
        self.output_module.run()
        self.update_inv()
        
    def update_inv(self):
        self.current_inv = self.current_inv + 1
        
        
class Algorithm(object):
    
    def __init__(self, ops, output_module):
        self.ops = ops
        self.output_module = output_module
        
    def implement(self):
        print("DO SOMETHING HERE?")
        

class a1(Algorithm):
    
    def __init__(self, ops, output_module):
        Algorithm.__init__(self, ops, output_module)
        
    def implement(self):
        self.ops[1].input_connect = [self.ops[0]]
        self.ops[3].input_connect = [self.ops[2]]
        self.ops[5].input_connect = [self.ops[4]]
        self.output_module.input_connect = [self.ops[1],
                                            self.ops[3],
                                            self.ops[5]]
        

class a2(Algorithm):
    
    def __init__(self, ops, output_module):
        Algorithm.__init__(self, ops, output_module)
        
    def implement(self):
        self.ops[0].input_connect = [self.ops]

    
class Component(object):
    
    def __init__(self, master, input_connect=None):
        self.master = master
        self.input = [0]*self.master.inv_samp
        self.output = [0]*self.master.inv_samp
        self.input_connect = input_connect
        
    def pull(self):
        self.input = [0]*self.master.inv_samp
        self.output = [0]*self.master.inv_samp
        if self.input_connect == None:
            self.input[:] = [0]*self.master.inv_samp
        elif len(self.input_connect) == 1:
            self.input[:] = self.input_connect[0].output[:]
        else:
            inputs = []
            for i in range(len(self.input_connect)):
                inputs.append(self.input_connect[i].output[:])
            self.input[:] = [sum(x) for x in zip(*inputs)]


class Operator(Component):
    
    def __init__(self, master, init_freq=200, input_connect=None):
        Component.__init__(self, master, input_connect)
        self.freq = init_freq
        self.phase = [0]*self.master.inv_samp
        self.phase_inc = 0
        self.phase_delay = [0]
        self.amp_val = 0
        
    def run(self):
        self.pull()
        self.phase_inc = (self.freq/self.master.fs)*(2*np.pi)
        for n in range(self.master.inv_samp):
            if n == 0:
                self.phase[0] = self.phase_delay[0] + self.phase_inc\
                                + self.input[0]
            else:
                self.phase[n] = self.phase[n-1] + self.phase_inc\
                                + self.input[n]
            if self.phase[n] > math.pi:
                self.phase[n] = self.phase[n] - 2*math.pi
            self.output[n] = math.sin(self.phase[n])*self.amp_val
        self.phase_delay[0] = self.phase[-1]


class Output(Component):
    
    def __init__(self, master, input_connect):
        Component.__init__(self, master, input_connect)
        
    def run(self):
        self.pull()
        self.master.output[:] = self.input[:]