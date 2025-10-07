def solve_setup_scheduling(processing_times, setup_costs, first_task):
    # Adjust input arrays to handle 1-based indexing
    p_times = [0] + processing_times
    s_costs = [[0] * len(setup_costs[0])] + setup_costs
    s_costs = [([0] + row) for row in s_costs]
    
    n = len(processing_times)
    remaining_tasks = set(range(1, n + 1))
    sequence = [0] * (n + 1)
    
    # Find the second task with minimal setup cost
    min_cost = float('inf')
    second_task = -1
    
    for j in range(1, n + 1):
        if j != first_task:
            if s_costs[first_task][j] < min_cost:
                min_cost = s_costs[first_task][j]
                second_task = j
        
    # Initialize first two tasks
    sequence[1] = 0  # s_1 = 0
    current_time = p_times[first_task]
    sequence[2] = current_time + s_costs[first_task][second_task]
    current_time = sequence[2] + p_times[second_task]
    
    # Remove scheduled tasks from remaining set
    remaining_tasks.remove(first_task)
    remaining_tasks.remove(second_task)
    
    # Track the sequence of tasks
    task_sequence = [first_task, second_task]
    
    # Step 4-8: Main loop for remaining tasks
    last_task = second_task
    current_pos = 3
    
    while remaining_tasks:
        min_setup = float('inf')
        next_task = -1
        
        for task in remaining_tasks:
            if s_costs[last_task][task] < min_setup:
                min_setup = s_costs[last_task][task]
                next_task = task
        
        sequence[current_pos] = current_time + s_costs[last_task][next_task]
        current_time = sequence[current_pos] + p_times[next_task]
        
        remaining_tasks.remove(next_task)
        last_task = next_task
        task_sequence.append(next_task)
        current_pos += 1
    
    return sequence[1:], current_time, task_sequence








