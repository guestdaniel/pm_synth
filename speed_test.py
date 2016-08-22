"""
pm_synth speed testing
"""

import pm_synth_buffer
import pm_synth_defaults as default

n_op = 2
fs = 20000
synth_kernel = pm_synth_buffer.Phase_Mod_Synth(fs=fs, n_op=n_op)
output = [synth_kernel.synthesize() for x in range(int(fs*5/default.BUFFER_LEN))] # Synthesize 5 seconds of audio
print(len(output))
