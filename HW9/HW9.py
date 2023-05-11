import csv
import matplotlib.pyplot as plt # for plotting
import numpy as np # for sine function

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

# Create moving average filter
def convolution(data,weights):
    # Inputs:
    #   data - vector of data
    #   weights - weights that are applied when calculating the average
    length = np.size(data) # Get the length of the data set
    points = np.size(weights) # Number of weights
    modifiedData = np.hstack((np.zeros(points-1),data,np.zeros(points-1))) # Create new data set with points-1 zeros prepended and 
    outputData = np.zeros(length) # Allocate output
    for i in range(0,length): # Loop over every element in the data set
        tot = 0
        for j in range(0,points): # Loop over every weight
            tot = tot + modifiedData[i+j]*weights[j]
        outputData[i] = tot
    return outputData

# Create list of all data
sig = []
for i in filenames:
    sig.append(csvRead(i))

movingAverage = np.ones(10) # Create vector
movingAverage = movingAverage/np.size(movingAverage) # Normalize

fig1, ax1 = plt.subplots(2,4) # Create 2 by 4 (data and FFT for each data set, 4 sets of data)
fig2, ax2 = plt.subplots(2,4) # Create 2 by 4 (moving average and IIR for each data set, 4 sets of data)

# We want to graph all the data using subplots
for i in range(len(sig)): # for each data set
    data = np.array(sig[i]) # Create np.array
    time = data[:,0] # time is the first column
    voltage = data[:,1] # voltage is the second column
    samples = np.size(time) # number of samples
    totTime = time[-1]-time[0] # total time for all samples
    sampleRate = int(samples/totTime) # samples per second
    fftDecomp = np.fft.fft(voltage)/samples # fft normalized by number of samples
    fftDecomp = abs(fftDecomp[range(int(samples/2))]) # 
    frequencies = np.arange(samples)*sampleRate/samples #
    frequencies = frequencies[range(int(samples/2))] #
    
    ax1[0,i].plot(time,voltage,markersize=0.3,linewidth=0.3) # plotting the raw data
    ax1[0,i].set_xlabel("Time (s)")
    ax1[0,i].set_ylabel("Voltage (V)")
    ax1[0,i].set_title("Raw Data, Sample %i" % (i+1))
    ax1[1,i].loglog(frequencies,fftDecomp,markersize=0.3,linewidth=0.3) # plotting the raw data
    ax1[1,i].set_xlabel("Frequency (Hz)")
    ax1[1,i].set_ylabel("Amplitude")
    ax1[1,i].set_title("FFT, Sample %i" % (i+1))
    
    # Get the top three frequencies
    sorted = np.sort(fftDecomp) # sort the magnitudes into ascending order
    index1 = np.where(fftDecomp==sorted[-1])[0][0]
    top1 = frequencies[index1]
    index2 = np.where(fftDecomp==sorted[-2])[0][0]
    top2 = frequencies[index2]
    index3 = np.where(fftDecomp==sorted[-3])[0][0]
    top3 = frequencies[index3]
    print(f"Data set {i+1} has {samples} samples with a sample rate of {sampleRate}Hz. Top 3 frequencies: {top1}Hz, {top2}Hz, {top3}Hz.")
    
    movAvgData = convolution(data, movingAverage) # Find the moving average of each data
plt.show()