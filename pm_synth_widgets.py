#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@title: pm_synth_widgets.py
@date: 08/13/16
@author: Daniel Guest
@purpose: widgets for pm_synth!
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pm_synth_defaults as default 


class CenterWidget(QWidget):
    """
    Central widget of main.py's MainWidget.
    
    Contains n_op OperatorGroups and n_gen GeneratorGroups and one master 
    frequency slider.
    
    TODO -- doc strings for all widgets
    """
    def __init__(self, parent=None, n_op=2):
        super(QWidget, self).__init__(parent)
        
        mainGrid = QGridLayout()
        self.setLayout(mainGrid)
        
        self.opgs = []
        self.opg_labels = []
        for i in range(n_op):
            self.opgs.append(OperatorGroup())
        for i in range(len(self.opgs)):
            self.opg_labels.append(QLabel("Operator: " + str(i+1)))
        col_count = 0
        row_count = 0
        for i in range(len(self.opgs)):
            mainGrid.addWidget(self.opg_labels[i], col_count+1, row_count)
            col_count = col_count+1
            mainGrid.addWidget(self.opgs[i], col_count+1, row_count)
            col_count = col_count+1
            if (i+1) % 2  == 0:
                row_count = row_count + 1
                col_count = 0
                
        masterFreqLabel = QLabel("Master frequency")
        self.masterFreqSlider = QDial(minimum=0, maximum=127, value=68)
        mainGrid.addWidget(masterFreqLabel)
        mainGrid.addWidget(self.masterFreqSlider)
        
        self.gengs = []
        for i in range(default.N_GEN):
            self.gengs.append(GeneratorGroup())
            mainGrid.addWidget(self.gengs[i])

                
class OperatorGroup(QWidget):
    
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        
        box = QVBoxLayout()
        self.setLayout(box)
        freqLabel = QLabel("Frequency of operator: ")
        self.freqSlider = FreqKnob(minimum=0, maximum=127, value=68)
        self.freqSlider.setValue(68)
        ampLabel = QLabel("Amplitude of operator: ")
        self.ampSlider = QDial(minimum=0, maximum=100, value=0)
        self.ampSlider.setValue(0)
        self.integralCheckBox = QCheckBox("Lock frequency downstream")
        box.addWidget(freqLabel)
        box.addWidget(self.freqSlider)
        box.addWidget(ampLabel)
        box.addWidget(self.ampSlider)
        box.addWidget(self.integralCheckBox)
        self.integralCheckBox.setChecked(True)
        
        
class GeneratorGroup(QWidget):
    
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        
        box = QVBoxLayout()
        self.setLayout(box)
        lagLabel = QLabel("Grain lag")
        self.lagSlider = QSlider(minimum=0,
                                 maximum=default.MAX_LAG_LEN,
                                 value=0,
                                 orientation=Qt.Horizontal)
        self.lagSlider.setValue(0)
        lagJitterLabel = QLabel("Grain lag jitter")
        self.lagJitterSlider = QSlider(minimum=default.MIN_LAG_JITTER,
                                       maximum=default.MAX_LAG_JITTER,
                                       value=default.CURR_LAG_JITTER,
                                       orientation=Qt.Horizontal)
        self.lagJitterSlider.setValue(default.CURR_LAG_JITTER)
        
        periodLabel = QLabel("Inter-grain period")
        self.periodSlider = QSlider(minimum=default.MIN_GEN_PERIOD,
                                  maximum=default.MAX_GEN_PERIOD,
                                  value=default.CURR_GEN_PERIOD,
                                  orientation=Qt.Horizontal)
        self.periodSlider.setValue(default.CURR_GEN_PERIOD)
        periodJitterLabel = QLabel("Inter-grain period jitter")
        self.periodJitterSlider = QSlider(minimum=default.MIN_GEN_PERIOD_JITTER,
                                          maximum=default.MAX_GEN_PERIOD_JITTER,
                                          value=default.CURR_GEN_PERIOD_JITTER,
                                          orientation=Qt.Horizontal)
        self.periodJitterSlider.setValue(default.CURR_GEN_PERIOD_JITTER)
        
        durLabel = QLabel("Grain duration")
        self.durSlider = QSlider(minimum=default.MIN_GRAIN_LEN, 
                                 maximum=default.MAX_GRAIN_LEN, 
                                 value=default.CURR_GRAIN_LEN, 
                                 orientation=Qt.Horizontal)
        self.durSlider.setValue(default.CURR_GRAIN_LEN)
        durJitterLabel = QLabel("Grain duration jitter")
        self.durJitterSlider = QSlider(minimum=default.MIN_GRAIN_LEN_JITTER,
                                       maximum=default.MAX_GRAIN_LEN_JITTER,
                                       value=default.CURR_GRAIN_LEN_JITTER,
                                       orientation=Qt.Horizontal)
        self.durJitterSlider.setValue(default.CURR_GRAIN_LEN_JITTER)
        
        box.addWidget(lagLabel)
        box.addWidget(self.lagSlider)
        box.addWidget(lagJitterLabel)
        box.addWidget(self.lagJitterSlider)
        box.addWidget(periodLabel)
        box.addWidget(self.periodSlider)
        box.addWidget(periodJitterLabel)
        box.addWidget(self.periodJitterSlider)
        box.addWidget(durLabel)
        box.addWidget(self.durSlider)
        box.addWidget(durJitterLabel)
        box.addWidget(self.durJitterSlider)        
        
class FreqKnob(QDial):
    
    def __init__(self, minimum=0, maximum=127, value=68):
        QDial.__init__(self, minimum=minimum, maximum=maximum, value=value)
        self.set_integral_freq(boolean=True)
        
    def set_integral_freq(self, boolean):
        if boolean == True:
            self.setMinimum(0)
            self.setMaximum(4)
            self.setValue(0)
        if boolean == False:
            self.setMinimum(0)
            self.setMaximum(127)
            self.setValue(68)