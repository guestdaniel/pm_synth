#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@title: pm_synth_controller.py
@date: 08/13/2016
@author: Daniel Guest
@purpose: Provide controller system for pm_synth.
"""
import pm_synth_defaults as default


class Controller(object):
    """
    Controller object master class.
    
    Each major section of the pm_synth and a corresponding section of
    pm_synth_widgets are assigned to a controller. Each controller has the 
    appropriate methods to bind the interfaces within the widgets to the
    appropriate parameters in the synth. 
    
    TODO -- do doc strings for Operator_Controller, Generator_Controller, and
        Synth_Controller.
    """
    def __init__(self):
        self.name = "Controller"
        
        
class Operator_Controller(Controller):
    """
    Operator Controller class.
    
    Arguments:
        operator (Operator object) -- the Operator object this Controller 
            connects to.
    
    An Operator_Controller is passed an Operator at initialization, and then
    an OperatorGroup later on using the bind_interface() method. When this
    method is called, all sliders/buttons in the OperatorGroup are connected to
    the proper parameters in the Operator.
    """
    def __init__(self, operator):
        Controller.__init__(self)
        self.op = operator
        self.freq_slider = None
        self.amp_slider = None
        
    def bind_freq(self, slider):
        self.freq_slider = slider
        def change_freq():
            self.op.curr_freq[:] = [self.freq_slider.value()]*default.BUFFER_LEN
        self.freq_slider.valueChanged.connect(change_freq)
        change_freq()
        
    def bind_amp(self, slider):
        self.amp_slider = slider
        def change_amp():
            self.op.amp_amt = self.amp_slider.value()/100
        self.amp_slider.valueChanged.connect(change_amp)
        change_amp()
        
    def bind_integral(self, checkbox):
        self.integral_checkbox = checkbox
        def set_integral_freq():
            boolean = None
            if self.integral_checkbox.checkState() == 0:
                boolean = False
            elif self.integral_checkbox.checkState() == 1 or 2:
                boolean = True
            self.op.set_integral_freq(boolean=boolean)
            self.freq_slider.set_integral_freq(boolean=boolean)
        self.integral_checkbox.stateChanged.connect(set_integral_freq)
        set_integral_freq()
        
    def bind_interface(self, OperatorGroup):
        freq_slider = OperatorGroup.freqSlider
        amp_slider = OperatorGroup.ampSlider
        integral_checkbox = OperatorGroup.integralCheckBox
        self.bind_freq(freq_slider)
        self.bind_amp(amp_slider)
        self.bind_integral(integral_checkbox)
        
        
class Generator_Controller(Controller):
    """
    Generator Controller class.
    
    Arguments:
        Generator (Generator object) -- the Generator object this Controller 
            connects to.
    
    An Generator_Controller is passed an Generator at initialization, and then
    an GeneratorGroup later on using the bind_interface() method. When this
    method is called, all sliders/buttons in the GeneratorGroup are connected to
    the proper parameters in the Generator.
    """    
    def __init__(self, generator):
        Controller.__init__(self)
        self.gen = generator
        self.period_slider = None
        self.dur_slider = None
        
    def bind_period(self, slider, jitter_slider):
        self.period_slider = slider
        self.period_jitter_slider = jitter_slider
        def change_period():
            self.gen.curr_period = self.period_slider.value()
        def change_period_jitter():
            self.gen.curr_period_jitter = self.period_jitter_slider.value()
        self.period_slider.valueChanged.connect(change_period)
        self.period_jitter_slider.valueChanged.connect(change_period_jitter)
        change_period()
        change_period_jitter()
        
    def bind_dur(self, slider, jitter_slider):
        self.dur_slider = slider
        self.dur_jitter_slider = jitter_slider
        def change_dur():
            self.gen.curr_dur = self.dur_slider.value()
        def change_dur_jitter():
            self.gen.curr_dur_jitter = self.dur_jitter_slider.value()
        self.dur_slider.valueChanged.connect(change_dur)
        self.dur_jitter_slider.valueChanged.connect(change_dur_jitter)
        change_dur()
        change_dur_jitter()
        
    def bind_lag(self, slider, jitter_slider):
        self.lag_slider = slider
        self.lag_jitter_slider = jitter_slider
        def change_lag():
            self.gen.curr_lag = self.lag_slider.value()
        def change_lag_jitter():
            self.gen.curr_lag_jitter = self.lag_jitter_slider.value()
        self.lag_slider.valueChanged.connect(change_lag)
        self.lag_jitter_slider.valueChanged.connect(change_lag_jitter)
        change_lag()
        change_lag_jitter()
        
    def bind_interface(self, GeneratorGroup):
        period_slider = GeneratorGroup.periodSlider
        period_jitter_slider = GeneratorGroup.periodJitterSlider
        dur_slider = GeneratorGroup.durSlider
        dur_jitter_slider = GeneratorGroup.durJitterSlider
        lag_slider = GeneratorGroup.lagSlider
        lag_jitter_slider = GeneratorGroup.lagJitterSlider
        self.bind_period(period_slider, period_jitter_slider)
        self.bind_dur(dur_slider, dur_jitter_slider)
        self.bind_lag(lag_slider, lag_jitter_slider)
            
        
class Synth_Controller(Controller):
    """
    Synthesizer Controller class.
    
    Arguments:
        Synthesizer (Synthesizer object) -- the Synthesizer object this Controller 
            connects to.
    
    An Synthesizer_Controller is passed an Synthesizer at initialization, and then
    an SynthesizerGroup later on using the bind_interface() method. When this
    method is called, all sliders/buttons in the SynthesizerGroup are connected to
    the proper parameters in the Synthesizer.
    """        
    def __init__(self, synth):
        Controller.__init__(self)
        self.synth = synth
        
    def bind_master_freq(self, slider):
        self.master_freq_slider = slider
        def change_master_freq():
            self.synth.curr_master_freq = self.master_freq_slider.value()
        self.master_freq_slider.valueChanged.connect(change_master_freq)
        change_master_freq()
        
    def bind_interface(self, CenterWidget):
        master_freq_slider = CenterWidget.masterFreqSlider
        self.bind_master_freq(master_freq_slider)