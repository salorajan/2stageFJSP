import sys
import numpy as np
# Constant for incompatible machines
INFINITE = 0


def readdata(filename):
    with open(filename) as f:
        lines = f.readlines()

    first_line = lines[0].split()
    # Number of jobs
    nb_jobs = int(first_line[0])
    # Number of machines
    nb_machines = int(first_line[1])

    # Number of operations for each job
    nb_operations = [int(lines[j + 1].split()[0]) for j in range(nb_jobs)]

    # Number of tasks
    nb_tasks = sum(nb_operations[j] for j in range(nb_jobs))

    # Processing time for each task, for each machine
    task_processing_time = [[INFINITE for m in range(nb_machines)] for i in range(nb_tasks)]

    # For each job, for each operation, the corresponding task id
    job_operation_task = [[0 for o in range(nb_operations[j])] for j in range(nb_jobs)]

    id = 0
    for j in range(nb_jobs):
        line = lines[j + 1].split()
        tmp = 0
        for o in range(nb_operations[j]):
            nb_machines_operation = int(line[tmp + o + 1])
            for i in range(nb_machines_operation):
                machine = int(line[tmp + o + 2 * i + 2]) - 1
                time = int(line[tmp + o + 2 * i + 3])
                task_processing_time[id][machine] = time
            job_operation_task[j][o] = id
            id = id + 1
            tmp = tmp + 2 * nb_machines_operation

    # Trivial upper bound for the end times of the tasks
    max_end = sum(
        max(task_processing_time[i][m] for m in range(nb_machines) if task_processing_time[i][m] != INFINITE)
        for i in range(nb_tasks))

    return nb_jobs, nb_machines, nb_tasks, task_processing_time, job_operation_task, nb_operations, max_end

filename = "./data/0_BehnkeGeiger/Behnke59.fjs"
#filename = "C:\\salo\\jbs\\fjsp_data\\data\\0_BehnkeGeiger\\Behnke59.fjs"

#"C:\\salo\\jbs\\hex_fjbs\\instances\\Mk01.fjs"

num_jobs , num_machines, nb_tasks, task_processing_time, job_operation_task, nb_operations, max_end=readdata(filename)

print('num_job',num_jobs , 'num_machines',num_machines, 'nb_tasks',nb_tasks,'\n')
print('max end',max_end)
from ortools.sat.python import cp_model
model = cp_model.CpModel()
choice={}
for i in range(nb_tasks):
    for j in range(num_machines):
        if task_processing_time[i][j] >0 :
            choice[(i,j)] = model.new_bool_var(f'choice_{i}_{j}')
        else:
            choice[(i,j)] = 0

max_span = model.new_int_var(0,max_end,f'max_span')

for i in range(nb_tasks):
    model.add(sum(choice[(i,j)] for j in range(num_machines))==1)
for i in range(num_machines):
    model.add(sum(choice[(j,i)]*task_processing_time[j][i] for j in range(nb_tasks))<=max_span)
model.minimize(max_span)


#=========
#
solver=cp_model.CpSolver()
solution_printer = cp_model.ObjectiveSolutionPrinter()
solver.parameters.max_time_in_seconds = 10.0  # Adjust this time limit

status = solver.solve(model, solution_printer)

print('status',status)
print(max_span,solver.value(max_span))

data2=[(j,task_processing_time[i][j]) for i in range(nb_tasks) for j in range(num_machines) if solver.value(choice[(i,j)])==1]
data=[]
for k in job_operation_task:
    j1=[data2[i] for i in k]
    #print(j1)
    data.append(j1)
'''
'''

    
