class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.waiting_time = 0
        self.turnaround_time = 0

def get_int_input(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print("Please enter a non-negative integer")
                continue
            return value
        except ValueError:
            print("Invalid input! Please enter an integer")

def get_processes(include_priority=False):
    processes = []
    n = get_int_input("Enter number of processes: ")
    for i in range(n):
        print(f"\nProcess {i+1}:")
        arrival = get_int_input("  Arrival Time: ")
        burst = get_int_input("  Burst Time: ")
        if include_priority:
            priority = get_int_input("  Priority (lower number = higher priority): ")
            processes.append(Process(pid=i+1, arrival_time=arrival, burst_time=burst, priority=priority))
        else:
            processes.append(Process(pid=i+1, arrival_time=arrival, burst_time=burst))
    return processes

def fcfs_scheduling(processes):
    processes.sort(key=lambda p: p.arrival_time)
    current_time = 0
    for p in processes:
        if current_time < p.arrival_time:
            current_time = p.arrival_time
        p.waiting_time = current_time - p.arrival_time
        current_time += p.burst_time
        p.turnaround_time = p.waiting_time + p.burst_time

def priority_scheduling(processes):
    n = len(processes)
    completed = 0
    current_time = 0
    is_completed = [False] * n

    while completed < n:
        eligible = [p for i,p in enumerate(processes) if p.arrival_time <= current_time and not is_completed[i]]
        if not eligible:
            current_time +=1  
            continue
        highest_priority_process = min(eligible, key=lambda x: x.priority)
        i = processes.index(highest_priority_process)

        processes[i].waiting_time = current_time - processes[i].arrival_time
        current_time += processes[i].burst_time
        processes[i].turnaround_time = processes[i].waiting_time + processes[i].burst_time
        is_completed[i] = True
        completed += 1

def print_results(processes, algorithm_name):
    print(f"\nScheduling Algorithm: {algorithm_name}")
    print("Process\tArrival\tBurst\tPriority\tWaiting\tTurnaround")
    total_waiting = 0
    total_turnaround = 0
    idle_time = 0

    for p in processes:
        total_waiting += p.waiting_time
        total_turnaround += p.turnaround_time
        prio_str = str(p.priority) if hasattr(p, 'priority') else '-'
        print(f"P{p.pid}\t{p.arrival_time}\t{p.burst_time}\t{prio_str}\t\t{p.waiting_time}\t{p.turnaround_time}")

    n = len(processes)
    avg_waiting = total_waiting / n
    avg_turnaround = total_turnaround / n
    print(f"\nAverage Waiting Time: {avg_waiting:.2f}")
    print(f"Average Turnaround Time: {avg_turnaround:.2f}")

    print("\nGantt Chart:")
    timeline = 0
    if algorithm_name == "FCFS":
        processes.sort(key=lambda p: p.arrival_time)
        for p in processes:
            if timeline < p.arrival_time:
                print(f"| Idle ({timeline} to {p.arrival_time}) ", end="")
                timeline = p.arrival_time
            print(f"| P{p.pid} ({timeline} to {timeline + p.burst_time}) ", end="")
            timeline += p.burst_time
    else: 
        n = len(processes)
        completed = 0
        current_time = 0
        is_completed = [False]*n

        while completed < n:
            eligible = [p for i,p in enumerate(processes) if p.arrival_time <= current_time and not is_completed[i]]
            if not eligible:
                next_arrival = min([p.arrival_time for i,p in enumerate(processes) if not is_completed[i]])
                print(f"| Idle ({current_time} to {next_arrival}) ", end="")
                current_time = next_arrival
                continue
            highest_priority_process = min(eligible, key=lambda x: x.priority)
            i = processes.index(highest_priority_process)
            print(f"| P{processes[i].pid} ({current_time} to {current_time + processes[i].burst_time}) ", end="")
            current_time += processes[i].burst_time
            is_completed[i] = True
            completed += 1
        timeline = current_time

    print("|")

def main():
    while True:
        print("\nSelect Scheduling Algorithm:")
        print("1. First-Come, First-Served (FCFS)")
        print("2. Priority Scheduling (Non-preemptive)")
        print("3. Exit")
        choice = input("Enter choice (1-3): ")

        if choice == '1':
            processes = get_processes()
            fcfs_scheduling(processes)
            print_results(processes, "FCFS")
        elif choice == '2':
            processes = get_processes(include_priority=True)
            priority_scheduling(processes)
            print_results(processes, "Priority Scheduling")
        elif choice == '3':
            print("Exiting... Bye-Bye!!")
            break
        else:
            print("Invalid choice! Please select 1, 2 or 3")

if __name__ == "__main__":
    main()
