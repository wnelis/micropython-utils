# micropython-utils
Micropython modules for microcontrollers

# millisDelay
Module millisDelay.py is a rewrite of the C++ class millisDelay written by the
Forward Computing and Control Pty. Ltd., www.forward.com.au.

I found that often the program in a microcontroller, like an ESP8266, consists
of a few more or less independent 'tasks'. These tasks are repeated at regular
intervals, but each task has it's own time period between successive runs. For
instance, one task performs a measurement every 10 seconds, one task publishes
the results every 300 seconds, and one task performs garbage collection also
every 300 seconds. Class millisDelay maintains a list of times at which timers
will expire. Whenever possible, it will invoke method machine.lightsleep() to
wait until the next timer will expire.

