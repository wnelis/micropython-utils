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

# Repeating a task when using asyncio
When using `asyncio`, module millisDelay cannot be used. The same functionality
can be achieved using the code fragments below. Thanks to Peter Hinch for
showing me the `asyncio`-ic way.

The defining features of module MillisDelay are the lack of need for a real time
clock and repeating the task at regular intervals, normally in the range from
about 10 milliseconds to several thousands of seconds. Any delays caused by
scheduling are automatically accounted for.

Two microPython snippets are shown below: (A) the definitions of an event and a
task to generate events at the appropriate times and (B) the use of those
definitions in a typical task.

The definitions are:

```python
import asyncio
from time import ticks_ms, ticks_add, ticks_diff

class pre( asyncio.ThreadSafeFlag ):
  def __init__( self, t ):
    super().__init__()
    self.at= ticks_ms()
    self.ts= t

async def runner( evt ):
  while True:
    now= ticks_ms()
    while ticks_diff( evt.at, now ) <= 0:
      evt.at= ticks_add( evt.at, evt.ts )  # Calculate time stamp of next event
    await asyncio.sleep_ms( ticks_diff(evt.at,now) )  # Wait the remaining time
    evt.set()
```

A timer class `pre` (short for 'periodically recurring events') extends the
existing class with two variables, the time stamp of the last event and the
period between successive events. The latter is expressed in milliseconds.

The helper task `runner` is passed an event object of type `pre`. It is used to
generate events with the specified interval. Note that `asyncio.ThreadSafeFlag`
is used, rather than `asyncio.Event`, as the former will automatically clear the
event upon completion of the `pre.wait`.

The snippet below shows a task using this mechanism, performing one pass each
second.

```python
async def this_job():
  ev= pre( 1000 )
  asyncio.create_task( runner(ev) )
  while True:
    await ev.wait()
    # Do the job
```
