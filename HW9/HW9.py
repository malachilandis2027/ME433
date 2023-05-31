import csv
import matplotlib.pyplot as plt # for plotting
import numpy as np # for sine function
from kaiserBesselFIR import kaiserBesselFIR

plt.rcParams['figure.figsize'] = [20, 10]

filenames = ['sigA.csv','sigB.csv','sigC.csv','sigD.csv']

# Create csv read function
def csvRead(filename): 
    with open(filename) as f:
    # open the csv file
        reader = csv.reader(f)
        data = []
        for row in reader:
            # read the rows 1 one by one
            data.append([float(row[0]),float(row[1])])
    return data

# Create convolution filter
def convolution(data,weights):
    # Inputs:
    #   data - vector of data
    #   weights - weights that are applied when calculating the average
    # Outputs:
    #   outputData - vector of same length as the input data
    length = np.size(data) # Get the length of the data set
    points = np.size(weights) # Number of weights
    modifiedData = np.hstack((data[0]*np.ones(points-1),data,data[-1]*np.ones(points-1))) # Create new data set with points-1 prepended and appended
    outputData = np.zeros(length) # Allocate output
    for i in range(0,length): # Loop over every element in the data set
        tot = 0
        for j in range(0,points): # Loop over every weight
            tot = tot + modifiedData[i+j]*weights[j]
        outputData[i] = tot
    return outputData

# Create IIR filter
def IIR(data,weights):
    # Inputs:
    #   data - vector of data
    #   weights - vector [A,B]
    # Outputs:
    #   outputData - vector of same length as the input data
    length = np.size(data) # Get the length of the data set
    A = weights[0]
    B = weights[1]
    outputData = np.zeros(length) # Allocate output
    outputData[0] = data[0] # First value doesn't change
    for i in range(1,length): # Loop over n-1
        outputData[i] = outputData[i-1]*A + data[i]*B
    return outputData

# Create list of all data
sig = []
for i in filenames:
    sig.append(csvRead(i))

# Create different set of weights corresponding to a moving average
movingAverageWeights = []
movingAverageNumbers = [1000, 2000, 100, 1000] # Different number of items to average over for each data set
for i in range(0,len(movingAverageNumbers)):
    print(i)
    movingAverage = np.ones(movingAverageNumbers[i]) # Create vector
    movingAverage = movingAverage/np.size(movingAverage) # Normalize
    movingAverageWeights.append(movingAverage)
    
# Create different IIR weights for each data set
IIRweights = [[0.999, 0.001],[0.999, 0.001],[0.9, 0.1],[0.999, 0.001]]

# Create different FIR weights for each data set
FIRweights = [kaiserBesselFIR(10000, 0, 10, 999, 10),
              kaiserBesselFIR(3300, 0, 10, 999, 10),
              kaiserBesselFIR(2500, 0, 10, 999, 10),
              kaiserBesselFIR(10000, 0, 10, 999, 10)]

fig1, ax1 = plt.subplots(2,4) # Create 2 by 4 (data and FFT for each data set, 4 sets of data)
fig2, ax2 = plt.subplots(2,4) # Create 2 by 4 (moving average and IIR for each data set, 4 sets of data)
fig3, ax3 = plt.subplots(1,4) # Create 1 by 4 (FIR for each data set, 4 sets of data)

# We want to graph all the data using subplots
for i in range(len(sig)): # for each data set
    # Extracting the data
    data = np.array(sig[i]) # Create np.array
    time = data[:,0] # time is the first column
    voltage = data[:,1] # voltage is the second column
    samples = np.size(time) # number of samples
    totTime = time[-1]-time[0] # total time for all samples
    sampleRate = int(samples/totTime) # samples per second
    fftDecomp = np.fft.fft(voltage)/samples # fft normalized by number of samples
    fftDecomp = abs(fftDecomp[range(int(samples/2))]) # take only half of the data
    frequencies = np.arange(samples)*sampleRate/samples # get the frequencies
    frequencies = frequencies[range(int(samples/2))] # take only half of the frequencies
    
    # Get the top three frequencies
    sorted = np.sort(fftDecomp) # sort the magnitudes into ascending order
    index1 = np.where(fftDecomp==sorted[-1])[0][0]
    top1 = frequencies[index1]
    index2 = np.where(fftDecomp==sorted[-2])[0][0]
    top2 = frequencies[index2]
    index3 = np.where(fftDecomp==sorted[-3])[0][0]
    top3 = frequencies[index3]
    print(f"Data set {i+1} has {samples} samples with a sample rate of {sampleRate}Hz. Top 3 frequencies: {top1}Hz, {top2}Hz, {top3}Hz.")
    
    # Making plot 1
    ax1[0,i].plot(time,voltage,markersize=0.3,linewidth=0.3) # plotting the raw data
    ax1[0,i].set_xlabel("Time (s)")
    ax1[0,i].set_ylabel("Voltage (V)")
    ax1[0,i].set_title("Raw Data, Sample %i" % (i+1))
    ax1[1,i].loglog(frequencies,fftDecomp,markersize=0.3,linewidth=0.3) # plotting the fft
    ax1[1,i].set_xlabel("Frequency (Hz)")
    ax1[1,i].set_ylabel("Amplitude")
    ax1[1,i].set_title("FFT, Sample %i (Peaks: %.2fHz, %.2fHz, %.2fHz)" % ((i+1),top1,top2,top3))
    
    # Take a moving average
    movAvgData = convolution(voltage, movingAverageWeights[i]) # Find the moving average of each data
    
    # Apply an IIR
    IIRdata = IIR(voltage, IIRweights[i])
    
    # Making plot 2
    ax2[0,i].plot(time,voltage,markersize=0.3,linewidth=0.3,c='k',label="Raw Data") # plotting the raw data in black
    ax2[0,i].plot(time,movAvgData,markersize=1,linewidth=1,c='r',label="Moving Average") # plotting the moving averaged data in red
    ax2[0,i].set_xlabel("Time (s)")
    ax2[0,i].set_ylabel("Voltage (V)")
    ax2[0,i].set_title("Moving Average, Sample %i, %i points" % ((i+1), movingAverageNumbers[i]))
    ax2[1,i].plot(time,voltage,markersize=0.3,linewidth=0.3,c='k',label="Raw Data") # plotting the raw data in black
    ax2[1,i].plot(time,IIRdata,markersize=1,linewidth=1,c='r',label="IIR") # plotting the IIR data in red
    ax2[1,i].set_xlabel("Time (s)")
    ax2[1,i].set_ylabel("Voltage (V)")
    ax2[1,i].set_title("IIR, Sample %i, A:%.3f B:%.3f" % ((i+1), IIRweights[i][0], IIRweights[i][1]))
    
    # Apply FIR filter
    FIRdata = convolution(voltage, FIRweights[i])
    
    # Making plot 3
    ax3[i].plot(time,voltage,markersize=0.3,linewidth=0.3,c='k',label="Raw Data") # plotting the raw data in black
    ax3[i].plot(time,FIRdata,markersize=1,linewidth=1,c='r',label="FIR") # plotting the FIR data in red
    ax3[i].set_xlabel("Time (s)")
    ax3[i].set_ylabel("Voltage (V)")
    ax3[i].set_title("FIR, Sample %i" % (i+1))
    
#plt.show()