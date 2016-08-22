#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@title: pm_synth.py
@date: 08/15/2016
@author: Daniel Guest
@purpose: Phase modulation synthesizer ala Yamaha DX7. 

TODO -- overhaul with buffers for more vectorization? Might help improve
        speed, which really should be much much better.
"""
import numpy as np
import math
import random
from collections import deque
import pm_synth_defaults as default


class Synthesizer(object):
    """ Generic top-level parent class for synthesizers. """
    def __init__(self, fs=10000):
        self.fs = fs
        self.curr_output = 0
        self.curr_inv = 0
        
    def synthesize(self):
        print("Do something here?")
        
    def update_inv(self):
        self.curr_inv = self.curr_inv + 1
        
        
class Phase_Mod_Synth(Synthesizer):
    """ 
    Top level parent class for pm_synth. 
    
    Arguments:
        fs (int) -- sampling rate in Hz
        n_op (int) -- number of operators
        n_gen (int) -- number of grain generators
        
    Phase_Mod_Synth first initializes attributes which store all the input
    arguments. Then, Phase_Mod_Synth creates lists which correspond to the
    frequencies in Hz and phase increments at each integer MIDI frequency
    value. This is used by oscillators in the synthesizer. Next,
    Phase_Mod_Synth intializes all of the operator and generator objects, 
    chooses an algorithm, and calls the algorithm's implement() method, which
    makes all of the necesssary connections between the operators and
    generators. Finally, Phase_Mod_Synth has a synthesize() method, which 
    runs the synthesizer. 
    """
    def __init__(self, fs=10000, n_op=default.N_OP, n_gen=default.N_GEN):
        Synthesizer.__init__(self, fs)
        self.n_op = n_op
        self.n_gen = n_gen
        self.curr_master_freq = 68
        
        # Create MIDI table
        self.midi = []
        self.phase_incs = []
        for i in range(128):
            self.midi.append(2**((i-69)/12)*400)
            self.phase_incs.append(self.midi[i]/self.fs*2*np.pi)
        
        # Initialize components
        self.ops = []
        for op in range(self.n_op):
            self.ops.append(Operator(self, number=(op+1)))
        self.gens = []
        for op in range(self.n_gen):
            self.gens.append(Grain_Generator(master=self))
        self.output_module = Output(self)
        
        # Choose algorithm
        self.algorithm = a1_6op_1gen(self.ops, self.gens, self.output_module)
        self.algorithm.implement()

    def synthesize(self):
        """
        Runs the synthesizer.
        
        Note, first runs the operators (in an order specified by the algorithm)
        and then the generators, running output_module last and returning the
        result.
        """
        for i in range(len(self.ops)):
            self.ops[self.algorithm.order[i]].run()
        for j in range(len(self.gens)):
            self.gens[j].run()
        self.output_module.run()
        return(self.curr_output)
        
        
# ----- ALGORITHMS -----
        
        
class Algorithm(object):
    """
    Top-level parent class for algorithms. 
    
    Algorithms, in FM parlance, are patterns of connections between operators.
    In pm_synth, algorithms are patterns of connections between operators, 
    generators, and output modules. Each child class of this parent class 
    is a specific implementation of an algorithm. Each child class implements
    a custom run_wires() method, which is called by the universal implement()
    method. 
    
    TODO -- clean up/organize algorithms
    TOOD -- add better doc strings
    """
    def __init__(self, ops=None, gens=None, output_module=None):
        self.ops = ops
        self.gens = gens
        self.output_module = output_module
        self.order = None
        
    def implement(self):
        self.run_wires()
        
        
class a1_2op_1gen(Algorithm):
    def __init__(self, ops, gens, output_module):
        Algorithm.__init__(self, ops, output_module)
        self.gens = gens
            
    def run_wires(self):
        self.ops[1].input_connect = [self.ops[0]]
        self.ops[1].give_delay_line(delay_len=default.OP_DELAY_LEN)
        self.gens[0].input_connect = [self.ops[1]]
        self.output_module.input_connect = [self.ops[1]]
        self.order = [0, 1]

        for op in range(len(self.ops)):
            self.ops[op].set_pull()
        for gen in range(len(self.gens)):
            self.gens[gen].set_pull()
        self.output_module.set_pull()
        
        
class a1_2op_Xgen(Algorithm):
    def __init__(self, ops, gens, output_module):
        Algorithm.__init__(self, ops, output_module)
        self.gens = gens
        
    def run_wires(self):
        self.ops[1].input_connect = [self.ops[0]]
        self.ops[1].give_delay_line(delay_len=default.OP_DELAY_LEN)
        for i in range(len(self.gens)):
            self.gens[i].input_connect = [self.ops[1]]
        self.output_module.input_connect = [*self.gens]
        self.order = [0, 1]
        
        for op in range(len(self.ops)):
            self.ops[op].set_pull()
        for gen in range(len(self.gens)):
            self.gens[gen].set_pull()
        self.output_module.set_pull()
        

class a1(Algorithm):
    
    def __init__(self, ops, output_module):
        Algorithm.__init__(self, ops, output_module)
        
    def run_wires(self):
        self.ops[1].input_connect = [self.ops[0]]
        self.ops[3].input_connect = [self.ops[2]]
        self.ops[5].input_connect = [self.ops[4]]
        self.output_module.input_connect = [self.ops[1],
                                            self.ops[3],
                                            self.ops[5]]
        self.order = [0, 2, 4, 1, 3, 5]


class a2(Algorithm):
    
    def __init__(self, ops, output_module):
        Algorithm.__init__(self, ops, output_module)
        
    def run_wires(self):
        for i in range(len(self.ops)):
            if i < (len(self.ops)-1):
                self.ops[i].input_connect = [self.ops[i+1]]
        self.output_module.input_connect = [self.ops[0]]
        self.order = [5, 4, 3, 2, 1, 0]
        

# ----- COMPONENTS -----


class Component(object):
    """
    Top-level parent class for components.
    
    A Component is a single audio processing unit, like an oscillator, filter,
    or grain generator. Every component 
    """
    def __init__(self, master, input_connect=None):
        self.master = master
        self.curr_input = 0
        self.curr_output = 0
        self.input_connect = input_connect
        self.has_delay_line = False
        self.delay_line = None
        self.pull = None
            
    def handshake(self):
        """
        Allows connected components to get to know one another.
        """
        pass
    
    def pull_none(self):
        self.curr_input = 0
        
    def pull_one(self):
        self.curr_input = self.input_connect[0].curr_output

    def pull_many(self):
        self.curr_input = sum([ic.curr_output for ic in self.input_connect])
            
    def set_pull(self):
        """
        Sets the proper pull() method for this Component.
        
        pull() methods come in three flavors - none, one, and many, for,
        respectively, no, one, and more than one Component in the
        input_connect. This assigns the correct method to this Component's
        pull(). More efficient than running a check every time!
        """
        if self.input_connect == None:
            self.pull = self.pull_none
        elif len(self.input_connect) == 1:
            self.pull = self.pull_one
        else:
            self.pull = self.pull_many
        
    def run(self):
        self.pull()
        self.process()
        if self.has_delay_line:
            self.delay_line.sample()
            
    def give_delay_line(self, delay_len):
        self.delay_line = Delay_Line(master=self.master, input_connect=[self],
                                     delay_len=delay_len)
        
    def process(self):
        print("Do something here?")
        
        
class Operator(Component):
    
    def __init__(self, master, number, init_freq=0, input_connect=None):
        Component.__init__(self, master, input_connect)
        self.curr_freq = init_freq
        self.curr_phase = 0
        self.phase_inc = None
        self.amp_amt = 0
        self.integral_freq = False
        self.number = number
        
    def process(self):
        if self.integral_freq == False:
            self.phase_inc = self.master.phase_incs[self.curr_freq]
        if self.integral_freq == True:
            self.phase_inc = self.master.phase_incs[self.master.curr_master_freq+(self.curr_freq*12)]
        self.curr_phase = self.curr_phase + self.phase_inc + (self.curr_input*2*math.pi)
        self.curr_output = math.cos(self.curr_phase)*self.amp_amt

    def set_integral_freq(self, boolean):
        self.integral_freq = boolean
        
        
class Output(Component):
    
    def __init__(self, master, input_connect=None):
        Component.__init__(self, master, input_connect)
        
    def process(self):
        self.master.curr_output = self.curr_input
        
        
class LFO(Component):
    
    def __init__(self, master, input_connect=None):
        Component.__init__(self, master, input_connect)
        
        
# ----- THE REALM OF GRAIN -----
        
                
class Grain_Generator(Component):
    
    def __init__(self, master, input_connect=None):
        Component.__init__(self, master, input_connect)
        self.master = master
        self.progeny = []
        self.dur_since_last_birth = 0
        self.curr_period = default.CURR_GEN_PERIOD
        self.curr_dur = default.CURR_GRAIN_LEN
        self.curr_lag = default.CURR_GEN_LAG
        self.curr_period_jitter = default.CURR_GEN_PERIOD_JITTER
        self.curr_dur_jitter = default.CURR_GRAIN_LEN_JITTER
        self.curr_lag_jitter = default.CURR_LAG_JITTER
        
        def generate_envelope(length):
            """ Generates triangular windowing function. """
            inc = 1/length*2
            envelope = [0]*int(length)
            for i in range(int(length/2)):
                envelope[i] = envelope[i-1] + inc
            for i in range(int(length/2), int(length)):
                envelope[i] = envelope[i-1] - inc
            return(envelope)
        self.envelope_generator = generate_envelope

    def generate_grain(self):
        if len(self.progeny) < default.MAX_GRAINS_PER_GEN:
            if self.curr_lag_jitter != 0:
                lag = self.curr_lag + random.randrange(0, self.curr_lag_jitter)
            else:
                lag = self.curr_lag
            content = self.input_connect[0].delay_line.get_segment(lag=lag,
                                                            duration=self.curr_dur)
            envelope = self.envelope_generator(self.curr_dur)
            self.progeny.append(Grain(generator=self, content=content, 
                                      envelope=envelope, id_number = len(self.progeny)))
            self.dur_since_last_birth = 0
        
    def process(self):
        self.curr_output = sum([progeny.run() for progeny in self.progeny])
        self.dur_since_last_birth = self.dur_since_last_birth + 1
        if self.curr_period_jitter != 0:
            period = self.curr_period + random.randrange(0, self.curr_period_jitter)
        else:
            period = self.curr_period
        if self.dur_since_last_birth > period:
            self.generate_grain() 
        
    def notify_death(self, id_number):
        self.progeny.pop(id_number)
        for i in range(len(self.progeny)):
            self.progeny[i].id_number = i
        
            
class Grain(object):
    
    def __init__(self, generator, content, envelope, id_number):
        self.generator = generator
        self.content = content
        self.duration = len(content)
        self.envelope = envelope
        self.curr_out = 0
        self.curr_index = 0
        self.id_number = id_number
        
    def run(self):
        if self.curr_index == self.duration-1:
            self.kill()
        self.curr_out = self.content[self.curr_index]
        self.curr_index = self.curr_index + 1
        return(self.curr_out)
        
    def kill(self):
        self.generator.notify_death(self.id_number)
        
        
# ----- EVERYTHING ELSE -----
    
    
class Delay_Line(object):
    
    def __init__(self, master, input_connect=None, delay_len=10):
        self.bank = deque([0]*round(delay_len))
        self._length = round(delay_len)
        self.input_connect = input_connect
        self.input_connect[0].has_delay_line = True

    def sample(self):
        _ = self.bank.popleft()
        self.bank.append(self.input_connect[0].curr_output)
        
    def get_sample(self, n_taps):
        return(self.bank[-(n_taps)])
        
    def get_segment(self, lag, duration):
        left_index = self._length - lag - duration
        return([self.bank[x] for x in range(left_index, left_index+duration)])
        
    def __len__(self):
        return(self._length)