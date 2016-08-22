-----
INTRO
-----
pm_synth is a demo project. The code is designed to be fairly readable and be well documented so that others learning Python (like myself) can readily learn from the code and adapt it to their own projects. pm_synth is a real-time phase modulation and granular synthesizer. It provides the user with an interface to control various parameters of the synthesizer and plays back the output of the synthesizer over the user's default playback device. 

---------
SYNTHESIS
---------

pm_synth generates a source waveform through phase modulation synthesis. The source waveform is then sampled by a grain generator to create grains, which are tiny snippets of audio. The sum of all active grains is the output played back to the user. For more information about how phase modulation and granular synthesis work, check out the doc strings in the pm_synth.py file. 

---
FAQ
---

Q: Why does it sound so bad?
A: Python is not really designed for real-time audio playback or real-time input. Unless you have a fast computer, even the default settings for pm_synth may be too much for your PC to handle in real-time. If they are, you'll get all sorts of glitches/noise on playback. You may get better audio quality by lowering the sample rate, number of operators, number of generators, etc. If you fiddle around with it and still can't get it to run smoothly on your computer, shoot me an email (my contact info is available below). 

It's also possible you're just synthesizing a bad sound! We're used to hearing synthesized sounds with time-varying envelopes, filters, etc., and without those things raw phase modulation and granulation can sound grating. Try switching the algorithm to [fill in details]. 

-------------
BIO & CONTACT
-------------

My name is Daniel Guest, and I'm a student of psychology at the University of Texas at Dallas. I study hearing and speech and play synthesizers and program in my free time. If you'd like to contact me to discuss pm_synth, any of my other projects, or anything related to speech/hearing/synthesis/DSP, please shoot me an email at daniel.guest@utdallas.edu. Thanks! 
