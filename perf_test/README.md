# Performance Testing different Multi-Threading Techniques

The code is currently very slow, mainly because it makes a lot of http requests and synchronously waits for each one to be finished. Thus, multithreading shold significantly increase performance. To test different strategies against each other, each of the files in this directory runs the exact same search with different multithreading strategies and prints how long it took to run.

Further, each file also prints the number of nodes, edges and visited user accounts, to make sure it actually ran the search correctly. If the number is as expected, the output will be green and red otherwise.

## Note on Threading in Python

Python has a Global Interpreter Lock, which prevents actual multithreading from existing in python. Python's threading model can still be useful when most of the execution time is spent waiting for I/O (as is the case with this application).

To achieve any further improvements in performance though, one must use python's subprocessing module. By subprocessing, a whole other python process is created, which can run truly parallel to the first python process.

So far I have not been able to use the subprocessing via the Executor Pools correctly.