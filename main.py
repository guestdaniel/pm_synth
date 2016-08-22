"""
@title: main.py
@date: 08/13/16
@author: Daniel Guest
@purpose: start file for pm_synth, a cool demonstration of real-time phase
          modulation synthesis and granular synthesis in Python! For more 
          information about phase modulation synthesis (aka frequency 
          modulation, or FM synthesis), check out fm_resources at the bottom of 
          this doc string. For more information about granular synthesis, check
          out grain_resources at the bottom of this doc string.

@instructions: To start pm_synth, simply run this main.py folder. In a python
               terminal, you can type "run main.py", or in a Linux terminal
               you can type "python main.py".
@requirements: PyQt5, sounddevice, numpy
@contact: Daniel Guest at drg130130@utdallas.edu

@fm_resouces: Chowning's original paper on FM synthesis -- https://goo.gl/G7pEQl
@grain_resources: Microsound, by Curtis Roads -- https://goo.gl/A3IKV3
"""

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 
import sounddevice as sd
from functools import partial
#import rtmidi
import pm_synth
import pm_synth_widgets as widg
import pm_synth_controller as ctrl
import pm_synth_defaults as default

__version__ = "0.1"

class MainWindow(QMainWindow):
    """
    Main window for application.
    
    Creates the central widget (containing the proper number of interface
    groups for the number of operators and generators being used) and then
    initializes a Synth_Thread with the proper controller callback. Finally the
    Synth_Thread's begin() method is called.
    """
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        # Set number of operators per voice and central widget
        self.n_op = default.N_OP
        self.n_gen = default.N_GEN
        self.cw = widg.CenterWidget(self, n_op=self.n_op)
        self.setCentralWidget(self.cw)
    
        # Create synth thread and give it the proper control setup callback
        op_ctrls = []
        synth_ctrl = None
        gen_ctrl = []
        def establish_ctrl(n_op, n_gen):
            for i in range(n_op):
                op_ctrls.append(ctrl.Operator_Controller(self.synth.synth_kernel.ops[i]))
                op_ctrls[i].bind_interface(self.cw.opgs[i])
            synth_ctrl = ctrl.Synth_Controller(self.synth.synth_kernel)
            synth_ctrl.bind_interface(self.cw)
            for i in range(n_gen):
                gen_ctrl.append(ctrl.Generator_Controller(self.synth.synth_kernel.gens[i]))
                gen_ctrl[i].bind_interface(self.cw.gengs[i])
        controller_setup = partial(establish_ctrl, n_op=self.n_op,
                                   n_gen=self.n_gen)
        self.synth = Synth_Thread(controller_setup=controller_setup,
                                  n_op=self.n_op, n_gen=self.n_gen)
        
        # Start synth
        self.synth.begin()
        
        # Create midi thread and run
#        self.midi = MIDI_Thread()
#        self.midi.input_main(device_id=24)
        

class Synth_Thread(QThread):
    """
    Provides a QThread for the synthesizer.
    
    Initializes a pm_synth instance with the proper number of operators and
    generators. Then, when its begin() method is called by the main window
    __init__(), it sets up the controllers and initializes a sounddevice output
    stream. 
    """
    def __init__(self, parent=None, controller_setup=None, n_op=default.N_OP,
                 n_gen=default.N_GEN):
        QThread.__init__(self, parent)
        
        self.exiting = False
        self.synth_kernel = pm_synth.Phase_Mod_Synth(fs=default.FS, n_op=n_op,
                                                     n_gen=n_gen)
        self.controller_setup = controller_setup
        self.block_size = default.BLOCK_LEN
        
    def callback(self, outdata, frames, time, status):
        outdata[:,0] = self.synth_kernel.synthesize()[:]

    def begin(self):
        self.controller_setup()
        self.start()
    
    def run(self):
        with sd.OutputStream(samplerate=default.FS, blocksize=self.block_size,
                             channels=1, callback=self.callback):
            print("press Return to quit")
            input()
            
            
#class MIDI_Thread(QThread):
#    def __init__(self, parent=None):
#        QThread.__init__(self, parent)
#        midi_in = rtmidi.MidiIn()
#        available_ports = midi_in.get_ports()
#        print(available_ports)
#        def midi_callback(*args):
#            print("CALLED BACK")
#        cb = partial(midi_callback, *args)
#        midi_in.open_port(0) # Should be 2nd midi device in available ports
#        midi_in.set_callback(cb)
        
    
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Phase Modulation Synthesizer")
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()

    
main()

