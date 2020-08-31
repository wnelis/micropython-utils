#
# Class millisDelay allows for multiple functions to run with independent timing
# on an ESP8266 (and similar?) microcontroller. Each timed function ('task')
# checks if it is time to do it's work. A typical skeleton for the script will
# look like:
#
#  import millisDelay
#  tmr = millisDelay.millisDelay()
#  tmr.start( <RepeatTime> )        # Repeat time [ms]
#
#  def DoSomething():               # Task definition
#    if tmr.justFinished():
#      tmr.repeat()
#      <Do the job>
#
#  def main():
#    while True:
#      DoSomething()
#
# The class maintains a list of times at which a timer will expire. Assuming
# that all I/O is performed using blocking I/O-calls, and assuming that all
# sleep-like calls use this class, it is possible to minimise power consumption
# by using function machine.lightsleep to wait for the next timer to expire.
#
# This class is a rewrite of the C++ class millisDelay written by the Forward
# Computing and Control Pty. Ltd., www.forward.com.au.
#
# Written by W.J.M. Nelis, wim.nelis@ziggo.nl, 2020.07
#
# To do:
# - include an initial delay
#
import machine
import time

class millisDelay():

 #
 # Allocate a list, a class variable, which will contain the expiration times of
 # the active timers, that is the times at which the various tasks should resume
 # their work.
 #
  cvmd_lst_task = 0
  cvmd_max_task = 8
  cvmd_wait_time= [None] * cvmd_max_task

 #
 # Method __init__ presets the instance variables.
 #
  def __init__( self ):
    self.TimePeriod= 0
    self.TimeStart = None
    self.TimeEnd   = None
    self.running   = False
    self.finishNow = False

 #
 # Define the methods to manage list cvmd_wait_time.
 # -------------------------------------------------
 #
 # Private method _md_add_timer adds a timer to the list of active timers. Each
 # entry in this list contains the time at which a timer will expire. The list
 # is sorted on expiration time.
 # This data structure will change quite often. In order to minimise the number
 # of object constructions and destructions, the list has a fixed length.
 # Methods causing a dynamic list length, such as slicing and list.insert, are
 # therefore not used.
 #
  def _md_add_timer( self ):
#   print( 'a0', millisDelay.cvmd_lst_task, self.cvmd_lst_task, millisDelay.cvmd_wait_time )  # TEST
    assert millisDelay.cvmd_lst_task<millisDelay.cvmd_max_task, "Task timer table overflow"

    if millisDelay.cvmd_lst_task == 0:
      millisDelay.cvmd_wait_time[0]= self.TimeEnd
    elif time.ticks_diff(millisDelay.cvmd_wait_time[millisDelay.cvmd_lst_task-1],self.TimeEnd) <= 0:
      millisDelay.cvmd_wait_time[millisDelay.cvmd_lst_task]= self.TimeEnd
    else:
      for i,t in enumerate(millisDelay.cvmd_wait_time):
        if time.ticks_diff(t,self.TimeEnd) > 0:
          for j in range(millisDelay.cvmd_lst_task,i,-1):
            millisDelay.cvmd_wait_time[j]= millisDelay.cvmd_wait_time[j-1]
          millisDelay.cvmd_wait_time[i]= self.TimeEnd
          break
    millisDelay.cvmd_lst_task+= 1
#  print( 'a1', millisDelay.cvmd_lst_task, self.cvmd_lst_task, millisDelay.cvmd_wait_time )  # TEST

 #
 # Private method _md_remove_timer removes an expired (?) timer from the list of
 # active timers.
 #
  def _md_remove_timer( self ):
#   print( 'r0', millisDelay.cvmd_lst_task, self.cvmd_lst_task, millisDelay.cvmd_wait_time )  # TEST
    assert millisDelay.cvmd_lst_task>0, "Task timer table empty"
    assert self.TimeEnd in millisDelay.cvmd_wait_time, "Entry to delete is gone"

    millisDelay.cvmd_lst_task-= 1
    for i,t in enumerate(millisDelay.cvmd_wait_time):
      if t == self.TimeEnd:
        for j in range(i,millisDelay.cvmd_lst_task):
          millisDelay.cvmd_wait_time[j]= millisDelay.cvmd_wait_time[j+1]
        millisDelay.cvmd_wait_time[millisDelay.cvmd_lst_task]= None
        break
#   print( 'r1', millisDelay.cvmd_lst_task, self.cvmd_lst_task, millisDelay.cvmd_wait_time )  # TEST

 #
 # Private method _md_try_to_sleep checks the time remaining until the next
 # timer expiration. If this time is 2 [ms] or more, method machine.lightsleep
 # is invoked to wait until 1 [ms] before the timer expiration. (A part of) the
 # last millisecond is spent looping until the timer is really expired. Method
 # lightsleep will reduce the power consumption slightly while waiting. Using
 # method lightsleep seems to reduce the current with about 0.5 [mA] on an
 # ESP8266.
 #
  def _md_try_to_sleep( self ):
    assert millisDelay.cvmd_lst_task>0, "Task timer table empty"

    t= time.ticks_diff( millisDelay.cvmd_wait_time[0], time.ticks_ms() ) - 1
    if t > 0:
      machine.lightsleep( t )
#     time.sleep_ms( t )

 #
 # Define the instance methods.
 # ----------------------------
 #
 # Private method _timer_expired returns a true value if the timer has expired,
 # otherwise it will return a false value.
 #
  def _timer_expired( self ):
    return True if time.ticks_diff(time.ticks_ms(),self.TimeEnd) >= 0 else False

 #
 # Method finish will cause the timer to expire immediatly and thus cause an
 # expiration event in the very near future.
 #
  def finish( self ):
    if self.running:
      self.finishNow= True

 #
 # Method justFinished checks the status of the timer. If the timer is expired,
 # possible forceful due to a call to method finish, a true value is returned.
 # If the timer is not expired, method _md_try_to_sleep is invoked and a false
 # value is returned to the caller. This method will return a true value only
 # once after expiration of the timer.
 #
  def justFinished( self ):
    if self.running  and  ( self.finishNow or self._timer_expired() ):
      self.stop()
      return True
    else:
      self._md_try_to_sleep()
      return False

 #
 # Method repeat schedules the timer again, using the parameters of the last
 # (re)start invocation. This method is intended to schedule periodic actions.
 #
  def repeat( self ):
    assert self.TimePeriod > 2, "Start not invoked yet"
    assert not self.running, "Can't repeat running timer"
  #
    self.TimeStart= time.ticks_add( self.TimeStart, self.TimePeriod )
    self.TimeEnd  = time.ticks_add( self.TimeStart, self.TimePeriod )
    self.running  = True
    self._md_add_timer()

  def restart( self ):
    self.start( self.TimePeriod )

  def start( self, Period ):
    assert Period > 2, "Time period is too small"
  # assert Period < 1000000000, "Time period is too large"
  #
    if self.running:
      self.stop()
  #
    self.TimePeriod= Period
    self.TimeStart = time.ticks_ms()
    self.TimeEnd   = time.ticks_add( self.TimeStart, self.TimePeriod )
    self.running   = True
    self.finishNow = False
    self._md_add_timer()

 #
 # Method stop will stop the timer. The stopped timer will not cause an
 # expiration event.
 #
  def stop( self ):
    if self.running:
      self.running  = False
      self.finishNow= False
      self._md_remove_timer()

