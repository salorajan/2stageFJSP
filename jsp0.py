from ortools.sat.python import cp_model
from dat0 import num_machines,num_jobs ,data 

import collections

def solve_fjps(num_machines=num_machines, num_jobs=num_jobs , operations_per_job=data ):
    """Solves a Flexible Job Shop Problem using Constraint Programming."""

    model = cp_model.CpModel()

    # Variables
    horizon = sum(sum(op[1] for op in job_ops) for job_ops in operations_per_job)  #Upper bound on makespan
    intervals = {}
    machines_intervals = {}
    task_type = collections.namedtuple("task_type", "start end interval")
    

    for job_id in range(num_jobs):
        for op_id, (machine_id, processing_time) in enumerate(operations_per_job[job_id]):
            start_var = model.NewIntVar(0, horizon, f'start_{job_id}_{op_id}')
            interval_var = model.NewIntervalVar(start_var, processing_time, start_var +processing_time , f'interval_{job_id}_{op_id}')
            intervals[job_id, op_id] =task_type(start =start_var, end =start_var +processing_time ,interval=interval_var)  
            if machine_id not in machines_intervals:
              machines_intervals[machine_id] = []
            machines_intervals[machine_id].append(interval_var)


    # Constraints

    #Precedence constraints within a job
    for job_id in range(num_jobs):
        for i in range(len(operations_per_job[job_id]) - 1):
            model.Add(intervals[(job_id, i+1)][0] >= intervals[(job_id, i)][1])


    #No overlap on machines
    for machine_id in machines_intervals:
        model.AddNoOverlap(machines_intervals[machine_id])

    #Objective: Minimize makespan
    #all_end_times = [intervals[job_id, len(operations_per_job[job_id]-1)].End() for job_id in range(num_jobs)]
    makespan = model.NewIntVar(0, horizon, 'makespan')
    #model.AddMaxEquality(makespan, all_end_times)
    model.add_max_equality(makespan,
        [intervals[job_id, len(job) - 1].end for job_id, job in enumerate(operations_per_job)],)
    
    model.Minimize(makespan)

    #Solve
    solver = cp_model.CpSolver()
    solution_printer = cp_model.ObjectiveSolutionPrinter()
    solver.parameters.max_time_in_seconds = 30.0  # Adjust this time limit
    status = solver.solve(model, solution_printer)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print('Solution found:')
        print(f'Makespan: {solver.Value(makespan)}')
        for job_id in range(num_jobs):
            print(f'Job {job_id}:')
            for op_id, (machine_id, processing_time) in enumerate(operations_per_job[job_id]):
                start_time = solver.Value(intervals[job_id, op_id].start)
                print(f'  Operation on machine {machine_id}: Start={start_time}, Duration={processing_time} end={start_time+processing_time}')
    else:
        print('No solution found.')


# Example usage:
try:
    solve_fjps(num_machines=num_machines, num_jobs=num_jobs , operations_per_job=data)
except :
    print('Error ! verify your data !') 

