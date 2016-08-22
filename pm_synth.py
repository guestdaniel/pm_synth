#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@title: pm_synth.py
@date: 08/15/2016
@author: Daniel Guest
@purpose: Phase modulation synthesizer ala Yamaha DX7. 
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
        self.curr_output = [0]*default.BUFFER_LEN
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
        
    Attributes:
        curr_master_freq (list) -- current master frequency input. On a real
            synthesizer, would be the frequency input by the keyboard.
        midi (list) --
        phase_incs (list) --
        ops (list) --
        gens (list) --
        output_module (object) --
        
    Phase_Mod_Synth first initializes attributes which store all the input
    arguments. Then, Phase_Mod_Synth creates lists which correspond to the
    frequencies in Hz and phase increments at each integer MIDI frequency
    value. This is used by oscillators in the synthesizer. Next,
    Phase_Mod_Synth intializes all of the operator and generator objects, 
    chooses an algorithm, and calls the algorithm's implement() method, which
    makes all of the necesssary connections between the operators and
    generators. Finally, Phase_Mod_Synth has a synthesize() method, which 
    runs the synthesizer. 
    
    TODO -- finish doc string
    FIXME -- there's still some errors, I think, in the phase calculations...
        Need to make sure that since the switch to buffers things are done
        correctly...
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
        self.algorithm = a1_2op_1gen(self.ops, self.gens, self.output_module)
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
        

class a1_2op(Algorithm):
    def __init__(self, ops, output_module):
        Algorithm.__init__(self, ops=ops, output_module=output_module)
        
    def run_wires(self):
        self.ops[1].input_connect = [self.ops[0]]
        self.ops[1].give_delay_line(delay_len=default.OP_DELAY_LEN)
        self.output_module.input_connect = [self.ops[1]]
        self.order = [0, 1]

        for op in range(len(self.ops)):
            self.ops[op].set_pull()
        self.output_module.set_pull()

        
class a1_2op_1gen(Algorithm):
    def __init__(self, ops, gens, output_module):
        Algorithm.__init__(self, ops=ops, gens=gens,
                           output_module=output_module)
            
    def run_wires(self):
        self.ops[1].input_connect = [self.ops[0]]
        self.ops[1].give_delay_line(delay_len=default.OP_DELAY_LEN)
        self.gens[0].input_connect = [self.ops[1]]
        self.output_module.input_connect = [self.gens[0]]
        self.order = [0, 1]

        for op in range(len(self.ops)):
            self.ops[op].set_pull()
        for gen in range(len(self.gens)):
            self.gens[gen].set_pull()
        self.output_module.set_pull()
        
        
class a1_2op_Xgen(Algorithm):
    def __init__(self, ops, gens, output_module):
        Algorithm.__init__(self, ops=ops, gens=gens,
                           output_module=output_module)
        
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
        

class a1_6op(Algorithm):
    
    def __init__(self, ops, output_module):
        Algorithm.__init__(self, ops=ops, output_module=output_module)
        
    def run_wires(self):
        self.ops[1].input_connect = [self.ops[0]]
        self.ops[3].input_connect = [self.ops[2]]
        self.ops[5].input_connect = [self.ops[4]]
        self.output_module.input_connect = [self.ops[1],
                                            self.ops[3],
                                            self.ops[5]]
        self.order = [0, 2, 4, 1, 3, 5]


class a2_6op_1gen(Algorithm):
    
    def __init__(self, ops, gens, output_module):
        Algorithm.__init__(self, ops=ops, gens=gens,
                           output_module=output_module)
        
    def run_wires(self):
        for i in range(len(self.ops)):
            if i < (len(self.ops)-1):
                self.ops[i].input_connect = [self.ops[i+1]]
        self.ops[0].give_delay_line(delay_len=default.OP_DELAY_LEN)
        self.gens[0].input_connect = [self.ops[0]]
        self.output_module.input_connect = [self.ops[0]]
        self.order = [5, 4, 3, 2, 1, 0]
        
        [op.set_pull() for op in self.ops]
        [gen.set_pull() for gen in self.gens]
        self.output_module.set_pull()


class a2_6op(Algorithm):
    
    def __init__(self, ops, output_module):
        Algorithm.__init__(self, ops=ops, output_module=output_module)
        
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
    
    Arguments:
        master (Phase_Mod_Synth object) -- master synth object, allows for
            reference to top-level synthesis parameters if necessary.
        input_connect (None, or list of Component(s)) -- see below
        
    Attributes:
        curr_input (list) -- input buffer.
        curr_output (list) -- output buffer.
        has_delay_line (boolean) -- whether or not Component has delay line.
        delay_line (None, or Delay_Line) -- contains delay line.
        pull (None) -- replaced by a pull() method when Algorithm is run.
        
    A Component is a single audio processing unit, like an oscillator, filter,
    or grain generator. Every component has an input and output buffer, whose
    lengths are determined by BUFFER_LEN in pm_synth_defaults.py. All
    components also use the input_connect system. When a component is 
    initialized, other components can be connected by passing them inside a
    list to the component's input_connect argument. Then, when the component is
    run using its run() method, the component will call on its pull() method 
    to fill its input buffer with the output(s) of the components in its 
    input_connect. This allows for a perpetuation of the signal through 
    components. 
    """    
    def __init__(self, master, input_connect=None):
        self.master = master
        self.curr_input = [0]*default.BUFFER_LEN
        self.curr_output = [0]*default.BUFFER_LEN
        self.input_connect = input_connect
        self.has_delay_line = False
        self.delay_line = None
        self.pull = None
    
    def pull_none(self):
        """ Pull() method if input is None. """
        self.curr_input = [0]*default.BUFFER_LEN
        
    def pull_one(self):
        """ Pull() method if input is len 1. """
        self.curr_input[:] = self.input_connect[0].curr_output[:]

    def pull_many(self):
        """ Pull() method if input len > 1. """
        inputs = [x.curr_output for x in self.input_connect]
        self.curr_input[:] = [sum(x) for x in zip(*inputs)]
            
    def set_pull(self):
        """
        Sets the proper pull() method for this Component.
        
        pull() methods come in three flavors - none, one, and many, for,
        respectively, no, one, and more than one Component in the
        input_connect. This assigns the correct method to this Component's
        pull(). More efficient than running a check every time! Should be
        called inside of this synth's Algorithm's run_wires() method. 
        """
        if self.input_connect == None:
            self.pull = self.pull_none
        elif len(self.input_connect) == 1:
            self.pull = self.pull_one
        else:
            self.pull = self.pull_many
        
    def run(self):
        """ 
        Pulls, processes, and processes delay line if appropriate. 
        
        Every child class of the parent Component class implements a custom
        process() method, which the universal run() method calls. This allows
        the synth to interface with all components in the same way (i.e. using
        each component's run() method), while allowing each component to have 
        its own processing code.
        """
        self.pull()
        self.process()
        if self.has_delay_line:
            self.delay_line.sample()
            
    def give_delay_line(self, delay_len):
        """ 
        Gives a delay line to this component. 
        
        Arguments:
            delay_len (int) -- length of delay line in samples.
        """
        self.delay_line = Delay_Line(master=self.master, input_connect=[self],
                                     delay_len=delay_len)
        
    def process(self):
        """ Should be filled in by the child class definition. """
        print("Do something here?")
        
        
class Operator(Component):
    """
    Operator, ala DX7.
    
    Arguments:
        master -- see Component doc string.
        number (int) -- unique identifying number for the operator.
        init_freq (int) -- initial frequency on MIDI scale.
        input_connect -- see Component doc string.
        
    Attributes:
        curr_freq (list) -- buffer containing oscillator input frequency values 
            for each sample in the buffer.
        curr_phase (list) -- buffer containing phase values for each sample
            in the buffer.
        phase_inc (list) -- buffer containing phase increments derived from
            curr_freq for each sample in the buffer.
        amp_amt (float) -- scales the amplitude of the output wave on a scale
            of 0 to 1.
        integral_freq (boolean) -- if False, curr_freq is treated as the input
            frequency on a MIDI scale. If True, curr_freq is treated as an 
            integer multiplier of the current master frequency. The result of
            this multiplication operation is then treated as the current input
            frequency. On a DX7, this is locking the Operator frequency to the
            keyboard input frequency, versus having it on an independent 
            frequency scale.
        number (int) -- unique ID number
        phase_delaylet (list, len 1) -- used to store the final curr_phase
            value, which is needed in each loop of processing. 
        
    An Operator is simply a single cosine wave.
    """
    def __init__(self, master, number, init_freq=0, input_connect=None):
        Component.__init__(self, master, input_connect)
        self.curr_freq = [init_freq]*default.BUFFER_LEN
        self.curr_phase = [0]*default.BUFFER_LEN
        self.phase_inc = [0]*default.BUFFER_LEN
        self.amp_amt = 0
        self.integral_freq = False
        self.number = number
        self.phase_delaylet = [0]
        
    def process(self):
        """ process() method for Operator objects. """
        self.calculate_phase_inc()
        self.render()
    
    def calculate_phase_inc(self):
        """
        Calculates phase increment for Operator.
        
        If integral_freq is False, the phase increment is simply the 
        corresponding phase increment to the current frequency. If
        integral_freq is True, the current frequency value is treated as an 
        integer multiplier of the current master frequency, and the phase
        increment is calculated accordingly. 
        """
        if self.integral_freq == False:
            self.phase_inc[:] = [self.master.phase_incs[x] for x in self.curr_freq][:]
        if self.integral_freq == True:
            self.phase_inc[:] = [self.master.phase_incs[self.master.curr_master_freq+(x*12)] for x in self.curr_freq][:]

    def render(self):
        """
        Loops through range(BUFFER_LEN), calculating phase.
        
        At each point in the phase buffer, calculates current phase based on
        past phase, current phase increment, and the output of any Operators
        connected to it through input_connect. Then, calculates the output of
        each phase value with math.cos().
        """
        self.curr_phase[0] = self.phase_delaylet[0] + self.phase_inc[0] + self.curr_input[0]
        for j in range(1, int(default.BUFFER_LEN)):
            self.curr_phase[j] = self.curr_phase[j-1] + self.phase_inc[j] + self.curr_input[j]
        self.phase_delaylet[0] = self.curr_phase[-1]
        self.curr_output[:] = [math.cos(x)*self.amp_amt for x in self.curr_phase][:]

    def set_integral_freq(self, boolean):
        self.integral_freq = boolean
        
        
class Output(Component):
    """ 
    Output component.
    
    Writes the output of whatever is connected to its input_connect to the 
    synth-level output. Only this class should reference the master output.
    """
    def __init__(self, master, input_connect=None):
        Component.__init__(self, master, input_connect)
        
    def process(self):
        self.master.curr_output[:] = self.curr_input[:]
        
     
#class LFO(Component):
#    
#    def __init__(self, master, input_connect=None):
#        Component.__init__(self, master, input_connect)
        
        
# ----- THE REALM OF GRAIN -----
        
                
class Grain_Generator(Component):
    """
    Grain generator component, generates and manages grains.
    
    Arguments:
        master -- see Component doc string.
        input_connect -- see Component doc string.
        
    Attributes:
        progeny (list) -- list of generated grains that are still being
            processed.
        dur_since_last_birth (int) -- time since last generated grain, in
            samples.
        curr_period (int) -- duration between grain generations in samples.
        curr_dur (int) -- duration of generated grains in samples.
        curr_lag (int) -- how far back into the delay line to grab grains from
            in samples.
        curr_XXXX_jitter -- amount of random jitter to be applied to curr_XXXX
            in samples. Works for period and lag, but not dur yet!
        envelope_generator (function) -- really should be a method... what was
            I doing?
            
    Generates grains, which are tiny snippets of audio, by sampling audio
    from the delay_line on the single component in its input_connect. 
    """
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
            """ Generates hamming windowing function. """
            envelope = list(np.hamming(length))
            return(envelope)
        self.envelope_generator = generate_envelope

    def generate_grain(self):
        """ Generates a single grain. """
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
        """ 
        process() method for Generator objects.
        
        Calculates its own output as the sum of all of its progeny grains' 
        outputs. Then, if the max number of grains has not been exceeded, it
        checks if its an appropriate time to generate a grain.
        """
        if len(self.progeny) > 0:
            progeny_outputs = [grain.run() for grain in self.progeny]
            self.curr_output[:] = [sum(output) for output in zip(*progeny_outputs)]
        else:
            self.curr_output[:] = [0]*default.BUFFER_LEN
        for i in range(default.BUFFER_LEN):
            self.dur_since_last_birth = self.dur_since_last_birth + 1
            if self.curr_period_jitter != 0:
                period = self.curr_period + random.randrange(0, self.curr_period_jitter)
            else:
                period = self.curr_period
            if self.dur_since_last_birth > period:
                self.generate_grain() 
        
    def notify_death(self, id_number):
        """ Notifies Generator that a grain has come to its final sample. """
        self.progeny.pop(id_number)
        for i in range(len(self.progeny)):
            self.progeny[i].id_number = i
        
            
class Grain(object):
    """
    A grain.
    
    Arguments:
        generator (Generator object) -- parent Generator.
        content (list) -- audio content of grain.
        envelope (list) -- envelope values (len should match len of content).
        id_number (int) -- unique ID number for grain.
        
    Attributes:
        curr_output (list) -- output buffer
        curr_index (int) -- current "playback" position, used to keep track
            of how long the grain has been playing back and, therefore, when
            it needs to die.
        duration (int) -- length of content in samples.
    """
    def __init__(self, generator, content, envelope, id_number):
        self.generator = generator
        self.content = content
        self.duration = len(content)
        self.envelope = envelope
        self.curr_output = [0]*default.BUFFER_LEN
        self.curr_index = 0
        self.id_number = id_number
        
    def run(self):
        """
        Processes grain. 
        
        If curr_index has reached duration, then the grain self-terminates
        using its kill() method. Otherwise, it outputs its content.
        """
        self.curr_output = [0]*default.BUFFER_LEN
        for i in range(default.BUFFER_LEN):
            if self.curr_index == self.duration-1:
                self.kill()
                return(self.curr_output)
            self.curr_output[i] = self.content[self.curr_index]
            self.curr_index = self.curr_index + 1
        return(self.curr_output)
        
    def kill(self):
        """ Kills this grain. """
        self.generator.notify_death(self.id_number)
        
        
# ----- EVERYTHING ELSE -----
    
    
class Delay_Line(object):
    """
    Delay line object.
    
    Arguments:
        master -- although this is not a Component, see Component doc string.
        input_connect -- same as above.
        delay_len (int) -- length of delay line in samples.
    
    Can sample a Component's current output and return either a single sample
    or a segment of the delay line. Uses deques instead of lists because
    deques have faster pop and append methods.
    """
    def __init__(self, master, input_connect=None, delay_len=10):
        self.bank = deque([0]*round(delay_len))
        self._length = round(delay_len)
        self.input_connect = input_connect
        self.input_connect[0].has_delay_line = True

    def sample(self):
        """ Samples connected Component's current output. """
        [self.bank.popleft() for x in range(int(default.BUFFER_LEN))]
        [self.bank.append(self.input_connect[0].curr_output[x]) for x in range(int(default.BUFFER_LEN))]
        
    def get_sample(self, n_taps):
        """ Gets sample from n_taps samples in the past. """
        return(self.bank[-(n_taps)])
        
    def get_segment(self, lag, duration):
        """ Gets segment starting lag samples in the past of duration samples. """
        left_index = self._length - lag - duration
        return([self.bank[x] for x in range(left_index, left_index+duration)])
        
    def __len__(self):
        """ Custom __len__ method so that len(Delay_Line) returns correctly. """
        return(self._length)