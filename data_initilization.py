#################################################################################################
# This python file will generate simulated signals for spike sorting
# the file consists of 4 functions: 
# spike_timeline_generator will generate the appear time nodes for a single cell
# wave_form_generator will generate the signals corresponding to a certain time nodes
# noise function will add noise to certain signal
# multi_electrons_generator will generate signals for multiple cells that can be detected
# in different electrons

import numpy as np
import random as rand
from matplotlib import pyplot as plt
import random as rand
from matplotlib.pyplot import cm 



#######################################################################################
# The function spike_timeline_generator will generate the time nodes that the spike signal appear
# the time interval between two consecutive is generated by exponential distribution of 
# parameter lambda 


# Input: 
# time: the set total time for the signal 
# interval_parameter: the exponential distribution parameter lambda
# plot: True/False to plot the time node
# spike_len: the length of each spike(the cut-off length of spike simulated by Gaussian difference)

# Output: 
# an array indicate the time nodes 

def spike_timeline_generator(time,interval_parameter,plot=False,spike_len=100):
# Initilization
	var=0
	start_time=[]
	index=0
# Main loop to generate the time axis
	while var < time-spike_len:
		interval=rand.expovariate(1.0/interval_parameter)
		interval=int(interval)

		var=var+interval+spike_len	
		start_time.append(var)
		
		index=index+1

	start_time[-1]=time
	spike_time=np.array(start_time)
	
	x_axis=np.arange(0,time)
	y=np.zeros(time)
		
	for item in x_axis:
		if item in spike_time:
			y[item]=2

	if(plot!=False):
		plt.plot(x_axis,y)
		plt.axis([0,time,0,5])
		plt.show()
	return spike_time




###################################################################################
# waveform_generator will generate the spike wave forms according to the time nodes

# Input: 
# spike_timeline: the time nodes generated byspike_timeline_generator
# shape_parameter: an 3 by 2 array, each row corresponding to mu, sigma, and the heights 
# parameters for two Gaussian difference
# Plot: True is to plot for a single spike 
# spike_len: the length of each spike(the cut-off length of spike simulated by Gaussian difference)



def waveform_generator(spike_timeline,shape_parameter,plot=False,spike_len=100):
	# get shape parameters
	mu1=shape_parameter[0,0]
	mu2=shape_parameter[0,1]

	sigma1=shape_parameter[1,0]
	sigma2=shape_parameter[1,1]

	height1=shape_parameter[2,0]
	height2=shape_parameter[2,1]
	# Convert unit
	# start_time=np.array(spike_time)/unit
	time=spike_timeline[-1]
	
	# time_unit=time/unit
	# spike_len_unit=spike_len/unit
	
	# set the length for waveform
	x=np.arange(time)
	y=np.zeros(time)
	spike_y=y.copy()

	
	# set for axis
	x_axis=x

	# draw the spikes
	spike_x=np.arange(-spike_len/2,spike_len/2)

	spike1=height1*np.exp(-np.power(spike_x/1.0 - mu1, 2.) / (2 * np.power(sigma1, 2.)))
	spike2=height2*np.exp(-np.power(spike_x/1.0- mu2, 2.) / (2 * np.power(sigma2, 2.)))
	spike=spike1-spike2

	if(plot!=False):
		
		plt.plot(spike)
		plt.show()

	# put spike into axis
	index=len(spike_timeline)
	for item in spike_timeline[0:index-2]:
		spike_y[item:item+spike_len]=spike

	spike_y=np.array(spike_y)
	return spike_y


#################################################################
# Noise function: 
# adding noise to the original signal

# input: 
# signal: original signal
# epsilon: control the degree of noise 

def noise(signal,epsilon):
	length=len(signal)
	noise_fun=[]
	for index in range(1,length+1):
		random=epsilon*rand.gauss(0, 2)
		noise_fun.append(random)
	
	output=signal+noise_fun
	return output

##################################################################
# Multi_electrons_generator function

# Given m cells, multi_electons_generator will stimulate 
# the signals perceived in n (n>=1) electrons

# Input: 
# num_electron : number of electrons
# num_cell: number of cells
# time: total time to generate signal
# noise_level: control the level of  noise, set between 0 to 1.0
# overlap_level: control the level of overlap, set from spike_len 

# Output: 
# boolean: a matrix of size num_electron times num_cell, the entries of boolean is 1/0
# 1/0 indicate whether a cell can be detected in a certain electron

# matrix_electron: a matrix of size num_electron*time 
# each row of this matrix is the stimulated signal of a certain electron

# spike_shape_parameter: a 3-D array of size num_electron* num_cell*time
# suppose we see the matrix as a 2-D matrix. Then each element in the matrix
# is an array of length time is the signal for a certain cell 
# in a certain electron

def multi_electrons_generator(num_electron,num_cell,time,noise_level,overlap_level,plot=False):
# set the boolean matrix for whether an electron can detect a single cell
	# random set
	boolean=np.random.randint(0,2,size=(num_electron,num_cell))
	num_eachElectron=boolean.sum(axis=1)

# set the matrix that records the signal delays for each cell in different electrons
	matrix_delay=np.zeros([num_electron,num_cell])

# set the matrix for spike in cell in different electron
	spike_shape_parameter=np.zeros((num_electron,num_cell,time))


	for j in range(num_cell):
		interval_parameter=overlap_level
		
		spike_timeline=spike_timeline_generator(time,interval_parameter,plot=False,spike_len=100)

		for i in range(num_electron):
			
			delay=np.random.randint(1,100)
			matrix_delay[i,j]=delay
			spike_timeline=spike_timeline+delay
			spike_timeline[-1]=time

			# set random spike shape parameter
			loc=np.random.permutation([-1,1])
			mu1=loc[0]*rand.randint(10,40)
			mu2=loc[1]*rand.randint(10,40)
			sigma1=rand.randint(1,20)
			sigma2=rand.randint(1,20)
			height1=rand.randint(100,500)
			height2=rand.randint(100,500)
			

			shape_parameter=np.array([[mu1,mu2],[sigma1,sigma2],[height1,height2]])

			signal=waveform_generator(spike_timeline,shape_parameter,False,spike_len=100)*boolean[i,j]
			spike_shape_parameter[i,j]=noise(signal,epsilon=(height1+height2)/2*noise_level)
			# get the matrix for different electrons
			matrix_electron=spike_shape_parameter.sum(axis=1)


		# add plot 
	if(plot!=False):
		color1=cm.rainbow(np.linspace(0,1,num_cell))
		#color2=cm.rainbow(np.linspace(num_cell+1,1,num_electron))

		f,ax=plt.subplots(num_electron,sharex=True, sharey=True)
	

		for i in range(num_electron):
			number=num_eachElectron[i]

			for j in range(num_cell):
				if(boolean[i,j]!=0):
					signal=np.array(spike_shape_parameter[i,j])
				else:
					signal=0
				ax[i].plot(signal,color=color1[j])
				ax[i].set_title('Electron %s can receive signals from %s cells' %(i,number))
		plt.savefig('image/SeperateSignalsOfElectron.png')



		f2,ax2=plt.subplots(num_electron,sharex=True, sharey=True)
		for i in range(num_electron):
			signal=np.array(matrix_electron[i])
			ax2[i].plot(signal,color='k')
			ax2[i].set_title('Signals of Electron %s' %(i))
		plt.savefig('image/ComposedSignalsOfElectron.png')



	return matrix_electron, boolean, spike_shape_parameter



#################################################################################
# A test for the above functions 

time=10000
interval_parameter=500
time1=spike_timeline_generator(time,interval_parameter,False)

shape_parameter=np.array([[45,-45],[1,1],[100,500]])
spike=waveform_generator(time1,shape_parameter,False)

a,b,c=multi_electrons_generator(5,5,10000,0.01,1000,True)















