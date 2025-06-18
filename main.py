# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 15:41:54 2020

@author: xavier.mouy

"""

# import sys
# sys.path.append("..") # Adds higher directory to python modules path.
from ecosound.core.audiotools import Sound
from ecosound.core.spectrogram import Spectrogram
#from ecosound.core.measurement import Measurement
from ecosound.detection.detector_builder import DetectorFactory
from ecosound.visualization.grapher_builder import GrapherFactory
from ecosound.measurements.measurer_builder import MeasurerFactory
import time
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
## Input paraneters ##########################################################

#single_channel_file = r"../ecosound/resources/67674121.181018013806.wav"
#single_channel_file = r"../ecosound/resources/JASCOAMARHYDROPHONE742_20140913T084017.774Z.wav"
#single_channel_file = r"C:\Users\xavier.mouy\Documents\PhD\Projects\Dectector\datasets\DFO_snake-island_rca-in_20181017\audio_data\67674121.181018040806.wav"


#grunts
single_channel_file = r'C:\Users\xavier.mouy\Documents\Projects\2025_Galapagos\test_PAMGuard\annotated\6474.220717154632_excerpt.wav'
t1 = 1 #197 #22#24
t2 = 84#160 #217 #40#24#40
# Spectrogram parameters
frame = 0.04266 #3000
nfft = 0.04266 #0.0853 4096
step = 0.007 # 500
#ovlp = 2500
fmin = 100
fmax = 5000
window_type = 'hann'
# denoising
denoise_window_duration=10
# detector
kernel_duration=0.05
kernel_bandwidth=1000
threshold=20
duration_min=0.05
bandwidth_min=500


## whistles
single_channel_file = r'C:\Users\xavier.mouy\Documents\Projects\2025_Galapagos\test_PAMGuard\Pamguard Files\DOLPHINS DATASET 1\5783.221110191544_1.wav'

#single_channel_file = r'C:\Users\xavier.mouy\Documents\Projects\2025_Galapagos\test_PAMGuard\5783.221110191544_1.wav'
t1 = 364 #197 #22#24
t2 = 380#160 #217 #40#24#40
# Spectrogram parameters
frame = 0.1 #3000
nfft = 0.1 #0.0853 4096
step = 0.03 # 500
#ovlp = 2500
fmin = 5000
fmax = 40000
window_type = 'hann'
# denoising
denoise_window_duration=1
# detector
kernel_duration=0.05
kernel_bandwidth=1000
threshold=8
duration_min=0.3
bandwidth_min=2000

## ###########################################################################
tic = time.perf_counter()

# load audio data
sound = Sound(single_channel_file)
sound.read(channel=0, chunk=[t1, t2], unit='sec', detrend=True)

# Calculates  spectrogram
spectro = Spectrogram(frame, window_type, nfft, step, sound.waveform_sampling_frequency, unit='sec')
spectro.compute(sound, dB=True, use_dask=True, dask_chunks=40)

# Crop unused frequencies
spectro.crop(frequency_min=fmin, frequency_max=fmax, inplace=True)

# Denoise
spectro.denoise('median_equalizer', window_duration=denoise_window_duration, use_dask=True, dask_chunks=(2048,1000), inplace=True)

# Detector
detector = DetectorFactory('BlobDetector', use_dask=True, dask_chunks=(2048,2000), kernel_duration=kernel_duration, kernel_bandwidth=kernel_bandwidth, threshold=threshold, duration_min=duration_min, bandwidth_min=bandwidth_min)
detections = detector.run(spectro, debug=False)

toc = time.perf_counter()
print(f"Executed in {toc - tic:0.4f} seconds")

# Plot
graph = GrapherFactory('SoundPlotter', title='Recording', frequency_max=fmax)
graph.add_data(sound)
graph.add_annotation(detections, panel=0, color='red',label='Detections')
graph.add_data(spectro)
graph.add_annotation(detections, panel=1,color='red',label='Detections')
graph.colormap = 'binary'
#graph.colormap = 'jet'
graph.show()

plt.show()

# calculate Q-index (freq/time)
# calculate energy
# remove first 4 sec
# add class name
# merge overlapped

print('Done')



## To test the .crop method
#detecSpectro = spectro.crop(time_min=2,time_max=10, inplace=False)
#detecSpectro = spectro.crop(time_max=10, inplace=False)
#detecSpectro = spectro.crop(frequency_min=50, inplace=False)
#detecSpectro = spectro.crop(frequency_max=800,inplace=False)
# detecSpectro = spectro.crop(frequency_min=0,frequency_max=600,time_min=10,time_max=10.3, inplace=False)
# graph = GrapherFactory('SoundPlotter', title='Detection', frequency_max=1000)
# graph.add_data(detecSpectro)
# graph.show()



