#!/usr/bin/python
from dronekit_sitl import SITL
# Import DroneKit-Python
from dronekit import connect, VehicleMode
from Tkinter import *
import time, thread, sys, struct, os
from curses import ascii
from pymavlink import mavparm, mavutil
from pymavlink.dialects.v10 import common as mavlink

# Connect to the Vehicle.
#print("Connecting to vehicle on: %s" % (connection_string,))
updatePanes = None
vehicle = None
sitl = None
root = None
connected = False
#connects to a drone sitting at ip:port and dispatches a thread to display it's
#inforamtion to the readout window
def connectToDrone(ip, port):
  
  global vehicle
  #connect to vehicle at ip:port
  vehicle = connect(ip+':'+port, wait_ready=True)
  global connected 
  connected = True
  
  # create thread to update readout information in real time
  thread.start_new_thread(updateVehicleStatus, (vehicle,))
  
def connectToSITL(ip, port):
  
  global sitl
  sitl = mavutil.mavlink_connection('tcp:'+ip+':'+port, dialect='ardupilotmega', write=True, input=False)
  print("Waiting for APM heartbeat")
  msg = sitl.recv_match(type='HEARTBEAT', blocking=True)
  print("Heartbeat from APM")
  
  #mav_param = mavparm.MAVParmDict()
  #mav_param.mavset(sitl, "SIM_WIND_DIR", float(70))
  #mav_param.mavset(sitl, "SIM_WIND_SPD", float(1000))

#disconnects the vehicle and cleans the readout
def disconnect():
  #close vehicle connection
  vehicle.close()
  updateReadoutWindow(updatePanes[0], "Disconneced")
  global connected
  connected = False

#def disconnectSTIL():
  #todo 

#continually updates the readout with vehicle information
def updateVehicleStatus(vehicle):
  while(connected): 
    #update the readout with vehicle information
    updateReadoutWindow(updatePanes[0], "%s" % vehicle.gps_0 +
    "\n%s" % vehicle.battery +
    "\nLast Heartbeat: %s" % vehicle.last_heartbeat +
    "\nIs Armable?: %s" % vehicle.is_armable +
    "\nSystem status: %s" % vehicle.system_status.state +
    "\nMode: %s" % vehicle.mode.name)  
    print(vehicle)
    root.update()
    #wait for 1 second
    time.sleep(1)
  print "out"

#helper function to write information to the readout
def updateReadoutWindow(textWindow, text):
  #sets the readout window from read only to read/write
  textWindow.config(state=NORMAL)
  #clears the readout window
  textWindow.delete('1.0', END)
  #inserts text into readout window
  textWindow.insert(END, text)
  #sets window back to read only 
  textWindow.config(state=DISABLED)

#adds toolbar to root frame
def loadToolbar(root):
  #Creates toolbar frame
  toolbar = Frame(root);
  mpToolbar = Frame(toolbar);
  sToolbar = Frame(toolbar);

  mpLabel = Label(mpToolbar, text = "Connect to Mavproxy: ")
  mpLabel.pack(side=LEFT, padx=2, pady=2)
  #creates IP label
  MPipLabel = Label(mpToolbar, text="IP Address")
  MPipLabel.pack(side=LEFT, padx=2, pady=2)
  
  #creates IP entry box
  MPipBox = Entry(mpToolbar)
  MPipBox.delete(0, END)
  MPipBox.insert(0, "127.0.0.1")  
  MPipBox.pack(side=LEFT, padx=2, pady=2)
 
  #creates port label
  MPportLabel = Label(mpToolbar, text="Port")
  MPportLabel.pack(side=LEFT, padx=2, pady=2)

  #creates port entry box
  MPportBox = Entry(mpToolbar)
  MPportBox.delete(0, END)
  MPportBox.insert(0, "14550")  
  MPportBox.pack(side=LEFT, padx=2, pady=2)
  
  #creates connection button
  MPcon = Button(mpToolbar, text="Connect", width=6, command=lambda: connectToDrone(MPipBox.get(), MPportBox.get()))
  MPcon.pack(side=LEFT, padx=2, pady=2)  
  #creates disconnect button
  MPdis = Button(mpToolbar, text="Disconnect", width=6, command=disconnect)
  MPdis.pack(side=LEFT, padx=2, pady=2)
  
  sLabel = Label(sToolbar, text="Connect to SITL:         ")
  sLabel.pack(side=LEFT, padx=2, pady=2)  

  SipLabel = Label(sToolbar, text="IP Address")
  SipLabel.pack(side=LEFT, padx=2, pady=2)
  
  #creates IP entry box
  SipBox = Entry(sToolbar)
  SipBox.delete(0, END)
  SipBox.insert(0, "127.0.0.1")  
  SipBox.pack(side=LEFT, padx=2, pady=2)
 
  #creates port label
  SportLabel = Label(sToolbar, text="Port")
  SportLabel.pack(side=LEFT, padx=2, pady=2)

  #creates port entry box
  SportBox = Entry(sToolbar)
  SportBox.delete(0, END)
  SportBox.insert(0, "5763")  
  SportBox.pack(side=LEFT, padx=2, pady=2)
  
  #creates connection button
  Scon = Button(sToolbar, text="Connect", width=6, command=lambda: connectToSITL(SipBox.get(), SportBox.get()))
  Scon.pack(side=LEFT, padx=2, pady=2)  
  #creates disconnect button
  Sdis = Button(sToolbar, text="Disconnect", width=6, command=disconnect)
  Sdis.pack(side=LEFT, padx=2, pady=2)

  mpToolbar.pack(side=TOP, fill=X)
  sToolbar.pack(side=TOP, fill=X)
  toolbar.pack(side=TOP, fill=X)

#creates a split panned window, with a text box on the left, and fault buttons on the left
def loadInfoPane(root):
  window = PanedWindow(orient=HORIZONTAL)
  window.pack(fill=BOTH, expand=1) 
  
  leftSubwindow = PanedWindow(orient=VERTICAL) 
  #TBH not sure what bottom left will do yet, but it's here
  bottomLeft = PanedWindow(orient=HORIZONTAL)
  bottomLeft.pack()

  #creates a text box on the left side (this is the readout window)
  readout = Text(root, height=20, width=50)
  readout.pack(side=LEFT)
  readout.config(state=DISABLED)
  
  leftSubwindow.add(readout)
  leftSubwindow.add(bottomLeft)
  
  window.add(leftSubwindow)

  #creates a simple paned window on the right side
  buttonArray = PanedWindow(orient=VERTICAL)
  window.add(buttonArray)
  
  #returns panes
  return [readout, buttonArray, bottomLeft]

def wind():
  print "boy, it's windy"

#adds faults to the window
def createFaultButtons(pane):
  #add wind button
  windB = Button(pane, text="Wind", width = 3, command = wind)
  windB.pack()

def main():
  global root
  root = Tk()
  root.geometry("760x600")
  loadToolbar(root)
  global updatePanes 
  updatePanes = loadInfoPane(root)
  updateReadoutWindow(updatePanes[0],"Use the connect button to connect to a drone!")
  createFaultButtons(updatePanes[1]) 
  root.mainloop()
  
if __name__ == "__main__":
  main()
