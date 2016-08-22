-----
INTRO
-----
pm_synth is a demo project. The code is designed to be fairly readable and be well documented so that others learning Python (like myself) can readily learn from the code and adapt it to their own projects. pm_synth is a real-time phase modulation and granular synthesizer. It provides the user with an interface to control various parameters of the synthesizer and plays back the output of the synthesizer over the user's default playback device. This is more of a demonstration of the idea of PM/granular synthesis and real-time synthesis than a rigorous implementation of it - pure Python is not really the ideal language for such a thing. 

To run pm_synth, you can type "run main.py" in a Python terminal opened in the pm_synth folder, or you can type "ipython main.py" from a Linux terminal opened in the pm_synth folder (probably similar in Windows/OSX). 

---------
SYNTHESIS
---------

pm_synth generates a source waveform through phase modulation synthesis. The source waveform is then sampled by a grain generator to create grains, which are tiny snippets of audio. The sum of all active grains is the output played back to the user. For more information about how phase modulation and granular synthesis work, check out the doc strings in the pm_synth.py file. 

---
FAQ
---

Q: Why does it sound so bad?

A: Python is not really designed for real-time audio playback or real-time input. Unless you have a fast computer, even the default settings for pm_synth may be too much for your PC to handle in real-time. If they are, you'll get all sorts of glitches/noise on playback. You may get better audio quality by lowering the sample rate, number of operators, number of generators, etc. If you fiddle around with it and still can't get it to run smoothly on your computer, shoot me an email (my contact info is available below). 

It's also possible you're just synthesizing a bad sound! We're used to hearing synthesized sounds with time-varying envelopes, filters, etc., and without those things raw phase modulation and granulation can sound grating. Try removing the grain generator by changing N_GEN to 0 in pm_synth_defaults.py and replacing "a1_2op_1gen" with "a1_2op" in definition of the algorithm attribute in Phase_Mod_Synth's __init__() method. This will result in just the rendering of two oscillators, and no grains. If you can't get a nice, pure sine tone out of the synthesizer at this point, something has gone seriously awry! 


Q: Why is the controller file so complicated? Couldn't you just manually assign controls to parameters?

A: Yes, it's possible and possibly more readable at first to just manually create controls and then assign them to synthesis paramters. However, this system allows for a variable number of operators and generators in virtually any  combination, with the interface updating to accomodate the different numbers! Play around with it and see what you can come up with! In my experience, I've been able to get a generator with up to 50 grains and 6+ operators running at the same time. If some of the core processing was replaced with Cython or Numba code, you could probably get even more.

-------------
BIO & CONTACT
-------------

My name is Daniel Guest, and I'm a student of psychology at the University of Texas at Dallas. I study hearing and speech and play synthesizers and program in my free time. If you'd like to contact me to discuss pm_synth, any of my other projects, or anything related to speech/hearing/synthesis/DSP, please shoot me an email at daniel.guest@utdallas.edu. Thanks! 
