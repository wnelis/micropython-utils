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

# delay_ms
Module delay_ms is an extension to a module with the same name, which can be
found at
https://github.com/peterhinch/micropython-async/blob/master/v3/primitives/delay_ms.py

The original module delay_ms implements the software equivalent of a
retriggerable monostable or a watchdog timer. It is extended to allow for scheduling
a task at regular intervals, using method repeat().

The envisioned way to use this functionality is shown in de pseudo code below:
```python
atimer = delay_ms.Delay_ms()  # Timer of 1 [s]

async def atask():
    while True:
        await atimer.wait()
        atimer.repeat()  # Implicit atimer.clear()
        <Do the job>

async def main():
    atimer.trigger()  # Start timer
    t00 = asyncio.create_task(atask())  # Schedule task
    await asyncio.sleep_ms(0)  # Run task
    <Other stuff>

asyncio.run(main())
```
