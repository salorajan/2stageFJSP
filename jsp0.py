"""
Stage 2: Job Shop Scheduling for Flexible Job Shop Problem (FJSP)

This module solves the job shop scheduling problem using constraint programming.
It takes the machine assignments from Stage 1 and schedules tasks to minimize makespan.

Author: Salo Rajan
"""

import logging
import sys
from collections import namedtuple
from ortools.sat.python import cp_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Named tuple for task information
TaskType = namedtuple("TaskType", "start end interval")


def validate_stage1_data(num_machines, num_jobs, operations_per_job):
    """
    Validate data received from Stage 1.
    
    Args:
        num_machines (int): Number of machines
        num_jobs (int): Number of jobs
        operations_per_job (list): Operations for each job [(machine, time), ...]
        
    Returns:
        bool: True if data is valid
        
    Raises:
        ValueError: If data is invalid
    """
    errors = []
    
    if num_machines <= 0:
        errors.append("Number of machines must be > 0")
    
    if num_jobs <= 0:
        errors.append("Number of jobs must be > 0")
    
    if len(operations_per_job) != num_jobs:
        errors.append(f"Expected {num_jobs} jobs, got {len(operations_per_job)}")
    
    # Validate each job
    for job_id, job_ops in enumerate(operations_per_job):
        if len(job_ops) == 0:
            errors.append(f"Job {job_id}: No operations")
        
        for op_id, (machine_id, processing_time) in enumerate(job_ops):
            if not isinstance(machine_id, int):
                errors.append(f"Job {job_id}, Op {op_id}: Machine ID must be integer")
            elif machine_id < 0 or machine_id >= num_machines:
                errors.append(f"Job {job_id}, Op {op_id}: Machine {machine_id} out of range [0, {num_machines - 1}]")
            
            if not isinstance(processing_time, int) or processing_time <= 0:
                errors.append(f"Job {job_id}, Op {op_id}: Processing time must be positive integer")
    
    if errors:
        error_msg = "Stage 1 data validation failed:\n" + "\n".join(errors)
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info("Stage 1 data validation passed")
    return True


def solve_fjsp(num_machines, num_jobs, operations_per_job):
    """
    Solve the Flexible Job Shop Problem using constraint programming.
    
    Args:
        num_machines (int): Number of machines
        num_jobs (int): Number of jobs
        operations_per_job (list): Machine assignments from Stage 1
                                   Format: [[(machine, time), ...], ...]
        
    Returns:
        tuple: (status, solver, intervals, makespan) or None if failed
    """
    try:
        logger.info("=" * 60)
        logger.info("STAGE 2: Job Shop Scheduling")
        logger.info("=" * 60)
        
        # Validate input data
        validate_stage1_data(num_machines, num_jobs, operations_per_job)
        
        logger.info(f"Input: {num_jobs} jobs, {num_machines} machines")
        
        # Create model
        model = cp_model.CpModel()
        logger.info("Creating constraint programming model...")
        
        # Calculate horizon (upper bound on makespan)
        try:
            horizon = sum(
                sum(op[1] for op in job_ops) 
                for job_ops in operations_per_job
            )
            if horizon <= 0:
                raise ValueError("Horizon calculation resulted in non-positive value")
        except Exception as e:
            logger.error(f"Error calculating horizon: {e}")
            raise
        
        logger.info(f"Horizon (makespan upper bound): {horizon}")
        
        # Initialize data structures
        intervals = {}
        machines_intervals = {}
        
        logger.info("Creating decision variables...")
        
        # Create variables for each task
        try:
            for job_id in range(num_jobs):
                if job_id >= len(operations_per_job):
                    raise IndexError(f"Job {job_id} out of range")
                
                for op_id, (machine_id, processing_time) in enumerate(operations_per_job[job_id]):
                    if not (0 <= machine_id < num_machines):
                        raise ValueError(f"Job {job_id}, Op {op_id}: Invalid machine {machine_id}")
                    
                    if processing_time <= 0:
                        raise ValueError(f"Job {job_id}, Op {op_id}: Invalid processing time {processing_time}")
                    
                    # Create start time variable
                    start_var = model.NewIntVar(
                        0, horizon, 
                        f'start_{job_id}_{op_id}'
                    )
                    
                    # Create interval variable
                    interval_var = model.NewIntervalVar(
                        start_var,
                        processing_time,
                        start_var + processing_time,
                        f'interval_{job_id}_{op_id}'
                    )
                    
                    # Store interval information
                    intervals[(job_id, op_id)] = TaskType(
                        start=start_var,
                        end=start_var + processing_time,
                        interval=interval_var
                    )
                    
                    # Group intervals by machine
                    if machine_id not in machines_intervals:
                        machines_intervals[machine_id] = []
                    machines_intervals[machine_id].append(interval_var)
        
        except (IndexError, ValueError, TypeError) as e:
            logger.error(f"Error creating variables: {e}")
            raise
        
        logger.info(f"Created {len(intervals)} task variables and {len(machines_intervals)} machine groups")
        
        # Add constraints
        logger.info("Adding constraints...")
        
        try:
            # Precedence constraints: operations within a job must follow order
            precedence_count = 0
            for job_id in range(num_jobs):
                for op_id in range(len(operations_per_job[job_id]) - 1):
                    if (job_id, op_id) not in intervals or (job_id, op_id + 1) not in intervals:
                        raise KeyError(f"Missing interval for job {job_id}, op {op_id}")
                    
                    model.Add(
                        intervals[(job_id, op_id + 1)].start >= intervals[(job_id, op_id)].end
                    )
                    precedence_count += 1
            
            logger.info(f"Added {precedence_count} precedence constraints")
            
            # No-overlap constraints: each machine can process one task at a time
            nooverlap_count = 0
            for machine_id in machines_intervals:
                if len(machines_intervals[machine_id]) > 0:
                    model.AddNoOverlap(machines_intervals[machine_id])
                    nooverlap_count += 1
            
            logger.info(f"Added no-overlap constraints for {nooverlap_count} machines")
        
        except (KeyError, TypeError) as e:
            logger.error(f"Error adding constraints: {e}")
            raise
        
        # Objective: minimize makespan
        logger.info("Setting up objective function...")
        
        try:
            makespan = model.NewIntVar(0, horizon, 'makespan')
            
            # Get end times of last operation in each job
            all_end_times = []
            for job_id in range(num_jobs):
                last_op_id = len(operations_per_job[job_id]) - 1
                if (job_id, last_op_id) not in intervals:
                    raise KeyError(f"Missing final interval for job {job_id}")
                all_end_times.append(intervals[(job_id, last_op_id)].end)
            
            if len(all_end_times) == 0:
                raise ValueError("No end times to minimize")
            
            model.AddMaxEquality(makespan, all_end_times)
            model.Minimize(makespan)
            
            logger.info("Objective: Minimize makespan")
        
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error setting up objective: {e}")
            raise
        
        # Solve
        logger.info("Starting solver...")
        solver = cp_model.CpSolver()
        solution_printer = cp_model.ObjectiveSolutionPrinter()
        solver.parameters.max_time_in_seconds = 30.0
        
        status = solver.Solve(model, solution_printer)
        
        logger.info(f"Solver status: {status}")
        
        if status == cp_model.OPTIMAL:
            logger.info("✓ Optimal solution found")
        elif status == cp_model.FEASIBLE:
            logger.info("✓ Feasible solution found (not optimal)")
        else:
            logger.warning("✗ No feasible solution found")
            return None
        
        return (status, solver, intervals, makespan)
    
    except Exception as e:
        logger.error(f"Stage 2 failed: {e}")
        raise


def print_solution(num_machines, num_jobs, operations_per_job, status, solver, intervals, makespan):
    """
    Print the solution in a readable format.
    
    Args:
        num_machines (int): Number of machines
        num_jobs (int): Number of jobs
        operations_per_job (list): Operations from Stage 1
        status: Solver status
        solver: CP solver object
        intervals: Dictionary of task intervals
        makespan: Makespan variable
    """
    try:
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            logger.warning("No valid solution to print")
            return
        
        logger.info("=" * 60)
        logger.info("SOLUTION")
        logger.info("=" * 60)
        
        makespan_value = solver.Value(makespan)
        logger.info(f"Makespan: {makespan_value}")
        logger.info("")
        
        # Print schedule for each job
        for job_id in range(num_jobs):
            logger.info(f"Job {job_id}:")
            total_time = 0
            
            for op_id, (machine_id, processing_time) in enumerate(operations_per_job[job_id]):
                if (job_id, op_id) not in intervals:
                    logger.warning(f"  Operation {op_id}: No interval found")
                    continue
                
                try:
                    start_time = solver.Value(intervals[(job_id, op_id)].start)
                    end_time = start_time + processing_time
                    total_time = max(total_time, end_time)
                    
                    logger.info(
                        f"  Op {op_id}: Machine {machine_id}, "
                        f"Start={start_time}, Duration={processing_time}, End={end_time}"
                    )
                except Exception as e:
                    logger.error(f"  Op {op_id}: Error reading solution - {e}")
            
            logger.info(f"  Job completion time: {total_time}")
            logger.info("")
    
    except Exception as e:
        logger.error(f"Error printing solution: {e}")
        raise


# Main execution
if __name__ == "__main__":
    try:
        # Import Stage 1 results
        logger.info("Importing Stage 1 results...")
        try:
            from dat0 import num_machines, num_jobs, data
            logger.info("✓ Stage 1 data imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import Stage 1 data: {e}")
            logger.error("Make sure dat0.py has been executed first")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error importing Stage 1 data: {e}")
            sys.exit(1)
        
        # Solve Stage 2
        result = solve_fjsp(num_machines, num_jobs, data)
        
        if result is None:
            logger.error("Stage 2 solver failed to find solution")
            sys.exit(2)
        
        status, solver, intervals, makespan = result
        
        # Print solution
        print_solution(num_machines, num_jobs, data, status, solver, intervals, makespan)
        
        logger.info("=" * 60)
        logger.info("Stage 2 completed successfully")
        logger.info("=" * 60)
    
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(2)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(3)
