import matplotlib.pyplot as plt
import numpy as np
from scipy import signal as dsp

def gyro_filtration_plot(timesteps, gyro_unfiltered, gyro_filtered):
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(20,5))

    ax[0].plot(timesteps, gyro_unfiltered[0])
    ax[0].plot(timesteps, gyro_filtered[0])
    
    ax[1].plot(timesteps, gyro_unfiltered[1])
    ax[1].plot(timesteps, gyro_filtered[1])
    
    ax[2].plot(timesteps, gyro_unfiltered[2])
    ax[2].plot(timesteps, gyro_filtered[2])
    
    # plot 2 subplots
    ax[0].set_title('Gyro x')
    ax[1].set_title('Gyro y')
    ax[2].set_title('Gyro z')
     
    fig.suptitle('Gyro filtered and unfiltered plots')
    plt.show()

def gyro_filtration_periodogram_plot(gyro_unfiltered, gyro_filtered, fs):
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(20,5))

    # periodogram propertos
    n_per_segment = 128
    window = 'hann'
    scaling = 'spectrum'

    f, unfiltered_Pxx_den = dsp.welch(gyro_unfiltered[0], fs, scaling=scaling, window=window, nperseg=n_per_segment)
    f, filtered_Pxx_den = dsp.welch(gyro_filtered[0], fs, scaling=scaling, window=window, nperseg=n_per_segment)
    ax[0].plot(f, unfiltered_Pxx_den)
    ax[0].plot(f, filtered_Pxx_den)
    
    f, unfiltered_Pxx_den = dsp.welch(gyro_unfiltered[1], fs, scaling=scaling, window=window, nperseg=n_per_segment)
    f, filtered_Pxx_den = dsp.welch(gyro_filtered[1], fs, scaling=scaling, window=window, nperseg=n_per_segment)
    ax[1].plot(f, unfiltered_Pxx_den)
    ax[1].plot(f, filtered_Pxx_den)

    f, unfiltered_Pxx_den = dsp.welch(gyro_unfiltered[2], fs, scaling=scaling, window=window, nperseg=n_per_segment)
    f, filtered_Pxx_den = dsp.welch(gyro_filtered[2], fs, scaling=scaling, window=window, nperseg=n_per_segment)
    ax[2].plot(f, unfiltered_Pxx_den)
    ax[2].plot(f, filtered_Pxx_den)
    
    # plot 2 subplots
    ax[0].set_title('Gyro x')
    ax[1].set_title('Gyro y')
    ax[2].set_title('Gyro z')
     
    fig.suptitle('Gyro filtered and unfiltered plots')
    ax[0].grid()
    ax[1].grid()
    ax[2].grid()
    
    plt.show()
