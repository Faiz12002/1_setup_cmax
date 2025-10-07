import random

def solve_setup_scheduling(processing_times, setup_costs):
    # Adjust input arrays to handle 1-based indexing
    p_times = [0] + processing_times
    s_costs = [[0] * len(setup_costs[0])] + setup_costs
    s_costs = [([0] + row) for row in s_costs]
    
    n = len(processing_times)
    remaining_tasks = set(range(1, n + 1))
    sequence = [0] * (n + 1)
    
    # Step 1-2: Choose initial two tasks with minimal setup cost
    min_cost = float('inf')
    minimal_pairs = []
    
    # First find the minimal setup cost
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i != j:
                if s_costs[i][j] < min_cost:
                    min_cost = s_costs[i][j]
                    minimal_pairs = [(i, j)]
                elif s_costs[i][j] == min_cost:
                    minimal_pairs.append((i, j))
    
    # Randomly select from pairs with minimal setup cost
    first_task, second_task = random.choice(minimal_pairs)
    
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
        candidates = []
        
        # Find minimum setup cost among remaining tasks
        for task in remaining_tasks:
            if s_costs[last_task][task] < min_setup:
                min_setup = s_costs[last_task][task]
                candidates = [task]
            elif s_costs[last_task][task] == min_setup:
                candidates.append(task)
        
        # Randomly select from tasks with minimal setup cost
        next_task = random.choice(candidates)
        
        sequence[current_pos] = current_time + s_costs[last_task][next_task]
        current_time = sequence[current_pos] + p_times[next_task]
        
        remaining_tasks.remove(next_task)
        last_task = next_task
        task_sequence.append(next_task)
        current_pos += 1
    
    return sequence[1:], current_time, task_sequence