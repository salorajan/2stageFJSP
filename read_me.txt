In this code the Flexible Job Scheduling Problem (FJSP)  solved by a two stage optimmization method. 
The FJSP is the problem to identify the  best job schedule among the possibilities. The difference between JSP and FJSP is that every task can be carried out in multiple ways.
 The objective of this research is to separate the FJSP   as an two stage optimization problem , 
the first stage is 
1. Identify the best option for every task. This is a binary integer programming problem  of minimizing the max span of each machine. Actually we are dividing the total work almost equally among all the machines.The file dat0.py solves the first stage and exports the resulting task options to the second stage.
2. The second stage is just the same JSP problem.We know that it involves the procedence constraints and no overlap constraints. this is an inspiration fro m google orttols example code. 
I thank the Google and Hexsely optimizer for providing some code and data.
this code has some limitations and I am working on that. any collabrations is welcome. 
.   