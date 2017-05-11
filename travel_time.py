#initialise python modules
import datetime
from datetime import date, timedelta

import obspy
from obspy.clients.fdsn import Client
client = Client("IRIS")

import matplotlib.pyplot as plt
from matplotlib.dates import date2num

#initialise label plotting array
from array import array
axis_array = array('f', [0.9,0.75,0.6,0.9,0.75,0.6,0.9,0.75,0.6,0.9,0.75,0.6,0.9,0.75,0.6,
                         0.9,0.75,0.6,0.9,0.75,0.6,0.9,0.75,0.6,0.9,0.75,0.6,0.9,0.75,0.6,
                         0.9,0.75,0.6,0.9,0.75,0.6,0.9,0.75,0.6,0.9,0.75,0.6,0.9,0.75,0.6,
                         0.9,0.75,0.6,0.9,0.75,0.6,0.9,0.75,0.6,0.9,0.75,0.6,0.9,0.75,0.6])

#user input
yr4jday = raw_input('Enter in year, default is 2017 >')
if yr4jday == "":
   yr4jday = 2017
else:
   yr4jday = int(yr4jday)

jdayin = raw_input('Enter in julian day e.g. 089, default is yesterday >')
if jdayin == "":
   today = date.today()
   yesterday = date.today() - timedelta(1)
   jday1 = yesterday.strftime('%j')
   jday2 = today.strftime('%j')
else:
   jday1 = jdayin
   jday2 = str(int(jdayin) + 1)

minmag = raw_input('Enter in minimum magnitude, default is 5.5 >')
if minmag == "":
   minmag = 5.5

#time period for processing
starttime = obspy.UTCDateTime(year=yr4jday, julday=jday1)
endtime = obspy.UTCDateTime(year=yr4jday, julday=jday2)

#set-up location of data files and receiver station lat and long ***change this***
file = "/Applications/swarm/Data/AM.RD4A6.00.SHZ.D." + str(yr4jday) +"." + jday1
stationlatitude=56.36
stationlongitude=15.2

#read file and plot dayplot
st = obspy.read(file)
#change filter to what suits your Shake best
st.filter("bandpass", freqmin=0.5, freqmax=2.0)
st.plot(type="dayplot", interval=60, right_vertical_labels=False, 
        vertical_scaling_range=5e2, one_tick_per_line=True, 
        color=['k', 'r', 'b', 'g'], show_y_UTC_label=False, 
        events={'min_magnitude': minmag})

#retrive catalog of events for day selected and greater than minimum magnitude
catalog = client.get_events(starttime=starttime, endtime=endtime, minmagnitude=minmag)
print(catalog)

#initialise theoretical arrival time model
from obspy.taup import TauPyModel
from obspy.geodetics import gps2DistAzimuth, kilometer2degrees
model = TauPyModel(model="iasp91")

#plot each event individually and overlay phase arrival times
for event in catalog:
    origin = event.origins[0]

    print(event)

    distance, _, _ = gps2DistAzimuth(origin.latitude, origin.longitude,
                                         stationlatitude, stationlongitude)
    distance = kilometer2degrees(distance / 1e3)
    arrivals = model.get_travel_times(origin.depth / 1e3, distance)
    print(arrivals)
    traveltime = arrivals[0].time
    arrival_time = origin.time + traveltime
    st = obspy.read(file, starttime=origin.time, endtime=origin.time + 4000)
#change filter to what suits your Shake best
    st.filter("bandpass", freqmin=0.5, freqmax=2.0)
    trmax = max(st.max())
    fig = plt.figure()
    st.plot(fig=fig, show=False)
    ax = fig.axes[0]
    font = {
            'size': 6,
           }
    i = 0
    switch = 1
    #while i < 38:
    while True:
              try:
                  arr = arrivals[i]
              except IndexError:
                  break
              else:
                  arrt = arr.time
                  arrp = arr.name
                  p_onset2 = origin.time + arr.time
                  ax.axvline(date2num(p_onset2.datetime), lw=0.5)
                  ymin, ymax = ax.get_ylim()
                  if switch == 1:
                     position = ymax*axis_array[i]
                  else:
                     position = ymin*axis_array[i]
                  plt.text(date2num(p_onset2.datetime), position, arrp, rotation=90, fontdict = font)
                  i += 1
                  switch = switch*-1
    plt.suptitle(origin.time)
    plt.show()
