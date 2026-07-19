# Two-Stage Flexible Job Shop Problem (FJSP) Solver

## Overview

This project implements a **two-stage optimization approach** to solve the Flexible Job Shop Problem (FJSP). The FJSP is a combinatorial optimization problem where the objective is to schedule jobs across machines while minimizing the makespan (total completion time).

### Problem Definition

- **Job Shop Problem (JSP)**: Schedule jobs with fixed task sequences on machines
- **Flexible Job Shop Problem (FJSP)**: Each task can be processed on multiple machines with different processing times
- **Two-Stage Approach**: 
  - **Stage 1**: Select the best machine for each task (minimizes load balancing)
  - **Stage 2**: Solve the resulting JSP with the selected machine assignments

---

## Key Features

✓ **Stage 1 Optimization**: Uses integer programming to select optimal machine assignments  
✓ **Stage 2 Optimization**: Applies constraint programming for job scheduling  
✓ **Google OR-Tools Integration**: Leverages OR-Tools for high-performance solving  
✓ **Flexible Machine Assignment**: Handles tasks that can run on multiple machines  
✓ **Load Balancing**: Distributes work evenly across available machines  

---

## Algorithm Architecture

### Stage 1: Machine Selection (dat0.py)

```
Input: FJSP instance (jobs, operations, processing times)
Process:
  - For each task: create binary variables for machine selection
  - Constraint: Each task assigned to exactly one machine
  - Objective: Minimize maximum load on any machine
Output: Machine assignment for each task
```

**Optimization Model:**
- Decision variables: `choice[i,j]` = 1 if task i runs on machine j
- Constraint 1: `Σ choice[i,j] = 1` (task assigned to one machine)
- Constraint 2: `Σ (choice[j,i] × processing_time[j,i]) ≤ max_span` (load on each machine)
- Objective: `Minimize max_span`

### Stage 2: Job Shop Scheduling (jsp0.py)

```
Input: Machine assignments from Stage 1
Process:
  - Create interval variables for each task
  - Add precedence constraints (tasks within a job must follow order)
  - Add no-overlap constraints (machine cannot process two tasks simultaneously)
  - Minimize makespan (maximum end time)
Output: Optimal schedule with start/end times for each task
```

---

## Project Structure

```
2stageFJSP/
├── README.md              # This file
├── read_me.txt            # Original notes
├── dat0.py               # Stage 1: Data loading and machine selection
├── jsp0.py               # Stage 2: Job shop scheduling
├── requirements.txt      # Python dependencies (optional)
└── data/
    └── 0_BehnkeGeiger/   # Sample benchmark data
        └── Behnke59.fjs  # FJSP instance file
```

---

## Data Format

FJSP instances should follow this format:

```
<num_jobs> <num_machines>
<num_ops_job1> <num_machines_op1> <machine1> <time1> <machine2> <time2> ... <num_machines_op2> ...
<num_ops_job2> ...
...
```

**Example:**
```
3 2
2 1 1 5 1 2 6
2 1 2 8 1 4 3
1 1 1 6
```

This means:
- 3 jobs, 2 machines
- Job 1: 2 operations (Op1 on 1 machine, Op2 on 2 machines)
- Job 2: 2 operations
- Job 3: 1 operation

---

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup

```bash
# Install required packages
pip install ortools numpy

# Or use requirements file
pip install -r requirements.txt
```

---

## Usage

### Step 1: Prepare Your Data

Place your FJSP instance file in the `data/` directory.

### Step 2: Run Stage 1 (Machine Selection)

```bash
# Edit dat0.py to set your data file path
filename = "./data/0_BehnkeGeiger/Behnke59.fjs"

# Run Stage 1
python dat0.py
```

**Output:**
```
num_job 4 num_machines 4 nb_tasks 10
max end 163
status 4  (OPTIMAL)
```

### Step 3: Run Stage 2 (Job Shop Scheduling)

```bash
# Stage 2 automatically reads output from Stage 1
python jsp0.py
```

**Output:**
```
Solution found:
Makespan: 187
Job 0:
  Operation on machine 0: Start=0, Duration=5, end=5
  Operation on machine 1: Start=5, Duration=6, end=11
...
```

---

## Configuration

### Time Limits

Adjust solver timeout (in seconds):

**dat0.py (Stage 1):**
```python
solver.parameters.max_time_in_seconds = 10.0  # Default: 10 seconds
```

**jsp0.py (Stage 2):**
```python
solver.parameters.max_time_in_seconds = 30.0  # Default: 30 seconds
```

### Solver Parameters

You can fine-tune OR-Tools solver parameters:
```python
solver.parameters.log_search_progress = True   # Show search progress
solver.parameters.num_search_workers = 4      # Parallel threads
```

---

## Performance Notes

### Complexity

- **Stage 1**: Binary integer programming → NP-hard
- **Stage 2**: Job shop scheduling → NP-hard
- **Overall**: Two-stage approach provides decomposition benefit but may sacrifice global optimality

### Expected Behavior

- Small instances (≤10 jobs, ≤5 machines): Optimal solution in seconds
- Medium instances (10-20 jobs): Near-optimal in 10-30 seconds
- Large instances (>20 jobs): Feasible solutions in 1-5 minutes

---

## Limitations & Future Work

### Current Limitations

1. ⚠️ Two-stage approach may not find global optimum (vs. solving full FJSP directly)
2. ⚠️ Sequential data parsing could be optimized for large instances
3. ⚠️ Limited error handling for malformed input files
4. ⚠️ No support for additional constraints (due dates, setup times, etc.)
5. ⚠️ No visualization of solution (Gantt charts)

### Future Improvements

- [ ] Add Gantt chart visualization
- [ ] Implement alternative heuristics (Genetic Algorithm, Simulated Annealing)
- [ ] Support additional FJSP variants (with due dates, setup times)
- [ ] Benchmark against standard datasets (Kacem, Ding-Xie, BRdata)
- [ ] Add result comparison: two-stage vs. direct FJSP solving
- [ ] Implement warm-starting to improve Stage 2 initial bounds
- [ ] Add parallel instance solving for batch processing

---

## References

This implementation was inspired by:
- **Google OR-Tools**: Constraint Programming solver
- **Standard FJSP Benchmarks**: Behnke, Kacem, Ding-Xie instances
- **Flexible Job Shop Scheduling**: Classical combinatorial optimization problem

---

## Troubleshooting

### Issue: "No solution found"

**Cause**: Solver timeout or infeasible problem
- ✓ Increase `max_time_in_seconds` parameter
- ✓ Check data file format
- ✓ Verify all machines are accessible to tasks

### Issue: "FileNotFoundError: data file not found"

**Cause**: Incorrect file path
- ✓ Verify file exists in `./data/` directory
- ✓ Use absolute paths if running from different directory

### Issue: "ImportError: No module named 'ortools'"

**Cause**: OR-Tools not installed
- ✓ Run: `pip install ortools`
- ✓ Verify installation: `python -c "from ortools.sat.python import cp_model"`

---

## Contributing

Contributions are welcome! Areas for collaboration:

- Bug fixes and error handling improvements
- Performance optimization
- New solver strategies
- Benchmark testing and validation
- Documentation enhancements

---

## License

This project is provided as-is for educational and research purposes.

## Author

**Salo Rajan**

## Acknowledgments

Thanks to **Google** for OR-Tools and **Hexsely** optimizer community for insights and code examples.

---

**Last Updated**: July 2025  
**Status**: Active Development
