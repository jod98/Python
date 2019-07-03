print ("---Program initialising---\n")
import pyaudio
import numpy as np
from matplotlib import pyplot as plt
import scipy.io.wavfile as wav
import wave
import scipy.fftpack
from scipy import signal

#GPIO libraries for led
import RPi.GPIO as GPIO
import time as t


#GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)


#*********************************************Recording Audio****************************************** 

recordTimeSeconds = 3

#MAX = 32000
sampleFrequency=32000
noOfFramesInBuffer = int(sampleFrequency * recordTimeSeconds)# fixed buffer size
print (noOfFramesInBuffer)

# initialize pyAudio - Opens a pyAudio session which can read or write to an audio device
audioDevicePort = pyaudio.PyAudio()
audioStream = audioDevicePort.open(format=pyaudio.paFloat32, 
                                   channels=1, 
                                   rate=sampleFrequency, 
                                   input=True, 
                                   frames_per_buffer=noOfFramesInBuffer)

print ("---Recording Audio (calibration)---\n")

# do this as long as you want fresh samples
rawAudioData = audioStream.read(noOfFramesInBuffer)

print ("---Finished recording Audio---\n")

#Creates an 1D array using the audio data
audioDataArray = np.fromstring(rawAudioData, dtype=np.float32)
print('Audio Data Array: ', audioDataArray)


# close stream
audioStream.stop_stream()
audioStream.close()
#terminate pyAudio Session
audioDevicePort.terminate()

#Writes the audio data to a wav file
wav.write('out2.wav',sampleFrequency,audioDataArray)


#*********************************************Playing Audio********************************************
##
##
###define stream chunk   
##noOfFramesInBuffer = 1024  
##
###opens a wav file with rb read only mode 
##audioFile = wave.open(r"out.wav","rb")  
##
### initialize pyAudio - Opens a pyAudio session which can read or write to an audio device
##audioDevicePort = pyaudio.PyAudio()  
#==============================================================================
# ##
#==============================================================================
###open stream  
##audioStream = audioDevicePort.open(format=pyaudio.paInt16, 
##                                   channels=1, rate=sampleFrequency, 
##                                   frames_per_buffer=noOfFramesInBuffer, 
##                                   output=True)
##
###read data  
##rawAudioData = audioFile.readframes(noOfFramesInBuffer)  
##
##print ("---Playing back audio---\n")
###play stream  
##while rawAudioData:  
##    audioStream.write(rawAudioData)  
##    rawAudioData = audioFile.readframes(noOfFramesInBuffer)
##    
##print ("---Finished playing back audio---\n")
##
###stop stream  
##audioStream.stop_stream()  
##audioStream.close()  
##
###close PyAudio  
##audioDevicePort.terminate()


#*********************************************Fourier Transforming Audio*******************************

print("---Calculating Fourier Transform---\n")
#FFT input
# Number of samplepoints
audioDataArrayLength = len(audioDataArray)
print("Audio Data Array Length: ", audioDataArrayLength, "\n")
# sample spacing
period_N = 1.0 / sampleFrequency  
print("Period (N): ", period_N, "\n")

FFTArrayOfAudioArray1 = scipy.fftpack.fft(audioDataArray)

###convert to log###
absFFT = (np.abs(FFTArrayOfAudioArray1[:audioDataArrayLength //2]))
FFTArrayOfAudioArray = 20*np.log10((2.0/audioDataArrayLength  * absFFT)/ 1000)

print("FFT Audio Array: \n\n", FFTArrayOfAudioArray, "\n")
print("Length of FFT array: ", len(FFTArrayOfAudioArray))

evenlySpacedArray = np.linspace(0.0, 1.0/(2.0*period_N), audioDataArrayLength/2)
#evenlySpacedArray = np.linspace(0.0, period_N, audioDataArrayLength)
print("Frequency Graph X-Axis: \n\n", evenlySpacedArray, "\n")

sampleRate = noOfFramesInBuffer/sampleFrequency
time = np.linspace(0.0,recordTimeSeconds,audioDataArrayLength)

#*********************************************Plotting Graphs****************************************** 

print("---Displaying graphs---\n")

fig, ax = plt.subplots()
#ax.plot(xf, 2.0/N * (np.abs(yf[:N//2])))
ax.plot(evenlySpacedArray, FFTArrayOfAudioArray)
ax.set_title('Power Spectrum Density')
plt.xlabel("Frequency(Hz)")
plt.ylabel("Power(dB)")
plt.show()


print ('abs of fft', FFTArrayOfAudioArray)

minThresholdHz = 1000
maxIndex = int(recordTimeSeconds*minThresholdHz);  
maxFreq = (FFTArrayOfAudioArray[maxIndex])
i = maxIndex+1;
while i< audioDataArrayLength//2 - 1:
    #print(evenlySpacedArray[i],' -----  ', 2/audioDataArrayLength * np.abs(FFTArrayOfAudioArray[i]))
    #print(FFTArrayOfAudioArray[i])
    if(maxFreq< (FFTArrayOfAudioArray[i])):
       maxIndex = i
       maxFreq = (FFTArrayOfAudioArray[i])
    i = i + 1


#find peaks
#print (np.arange(5,20))
#peakind = signal.find_peaks_cwt(FFTArrayOfAudioArray,np.arange(5,10),noise_perc=0.1)
#print('peaks', peakind)


freqToLookFor = int(evenlySpacedArray[maxIndex])
print('max freq', evenlySpacedArray[maxIndex])
print('max freq Amplitude in db: ', maxFreq)

if(evenlySpacedArray[maxIndex] >1800 and evenlySpacedArray[maxIndex] < 2200):
    print ('true')
else:
    print('false')
   

#plt.show()
print("---Program has ended---")


print("\n\n---Listening for Whistles---")

recordTimeSeconds = 0.32
noOfFramesInBuffer = int(sampleFrequency * recordTimeSeconds)

j = 0
z = 0
whistleRange = 200
while True:
    #Record Audio
    audioDevicePort = pyaudio.PyAudio()
    audioStream = audioDevicePort.open(format=pyaudio.paFloat32, 
                                       channels=1, 
                                       rate=sampleFrequency, 
                                       input=True, 
                                       frames_per_buffer=noOfFramesInBuffer)
    
    #print ("---Recording Audio---\n")
    
    # do this as long as you want fresh samples
    rawAudioData = audioStream.read(noOfFramesInBuffer)
    
    #print ("---Finished recording Audio---\n")
    
    #Creates an 1D array using the audio data
    audioDataArray = np.fromstring(rawAudioData, dtype=np.float32)
    
    
    # close stream
    audioStream.stop_stream()
    audioStream.close()
    #terminate pyAudio Session
    audioDevicePort.terminate()
    
    
    #FFT
    audioDataArrayLength = len(audioDataArray)
    #print("Audio Data Array Length: ", audioDataArrayLength, "\n")
    # sample spacing
    period_N = 1.0 / sampleFrequency  
    #print("Period (N): ", period_N, "\n")
    
    FFTArrayOfAudioArray1 = scipy.fftpack.fft(audioDataArray)
    absFFT = (np.abs(FFTArrayOfAudioArray1[:audioDataArrayLength//2]))
    FFTArrayOfAudioArray = 20*np.log10((2.0/audioDataArrayLength * absFFT)/ 1000)
    ##print("FFT Audio Array: \n\n", FFTArrayOfAudioArray, "\n")
    
    evenlySpacedArray = np.linspace(0.0, 1.0/(2.0*period_N), audioDataArrayLength/2)
    #evenlySpacedArray = np.linspace(0.0, period_N, audioDataArrayLength)
    #print("Frequency Graph X-Axis: \n\n", evenlySpacedArray, "\n")
    
    #sampleRate = noOfFramesInBuffer/sampleFrequency
    #time = np.linspace(0.0,recordTimeSeconds,audioDataArrayLength)
    
    minThresholdHz =1000
    #maxTresholdHz = 3000
    maxIndex = int(recordTimeSeconds*minThresholdHz);  
    #maxIndex2 = int(recordTimeSeconds*minThresholdHz);  
    maxFreq = FFTArrayOfAudioArray[maxIndex]
    i = maxIndex+1;
    
    while i< audioDataArrayLength//2 - 1:
        #print(evenlySpacedArray[i],' -----  ', 2/audioDataArrayLength * np.abs(FFTArrayOfAudioArray[i]))
        if(maxFreq< (FFTArrayOfAudioArray[i])):
           maxIndex = i
           maxFreq = FFTArrayOfAudioArray[i]
        i= i + 1
    
    #print('max freq', evenlySpacedArray[maxIndex])
    
    if(evenlySpacedArray[maxIndex] > (freqToLookFor-whistleRange) and evenlySpacedArray[maxIndex] < (freqToLookFor+whistleRange) and int(FFTArrayOfAudioArray[maxIndex]) > -100):
        print ('\nPossible Whistle!! No.', j+1 , '\tFrequency: ', int(32000/audioDataArrayLength*maxIndex) , 'Hz\tArray position: ' , maxIndex , '\tAmplitude: ', int(FFTArrayOfAudioArray[maxIndex]))
        j = j + 1
        z = z+1
    else:
       #print("Reset. Not a whistle")
        GPIO.output(18, GPIO.LOW)
        z = 0
    
    if(z>=2):
        print("Whistle Detected")
        #light LED
        GPIO.output(18, GPIO.HIGH)
        #t.sleep(1)
        
        
    #else:
        #print('false')
