# Why Multiprocessing instead of Threads?

I used Multiprocessing (multiprocess to be exact - fork of standard library) module instead of Threads because it's the only real way to achieve true parallelism in Python. Multithreading cannot achieve this because the GIL (Global Interpreter Lock) prevents threads from running in parallel.

## To even proof that, the [stackoverflow](https://stackoverflow.com/a/55319297/10686785) user has taken an experiment.

![image](https://i.stack.imgur.com/2x04m.png)

## Conclusions were that:

- For CPU bound work, Multiprocessing is always faster, presumably due to the GIL.
- Threads are fully serialized by the GIL
- Processes can run in parallel

Also the key advantage is isolation. A crashing process won't bring down other processes, whereas a crashing thread may wreak havoc with other threads.

## Simple graph:


                 Active threads / processes           
    +-----------+--------------------------------------+
    |Thread   1 |********     ************             |
    |         2 |        *****            *************|
    +-----------+--------------------------------------+
    |Process  1 |******     ******   ************      |
    |         2 |********  ****     *******    ********|
    +-----------+--------------------------------------+
                 Time -->                             

