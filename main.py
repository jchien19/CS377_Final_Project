from typing import List
from mlfq import MLFQScheduler, STCFScheduler, RoundRobinScheduler, FIFOScheduler, SJFScheduler, Job

def calculate_jains_fairness(values: List[float]) -> float:
    """
    Calculate Jain's Fairness Index
    """
    if not values:
        return 0.0
    denom = sum(v * v for v in values)
    if denom == 0:
        return 0.0
    total = sum(values)
    return (total * total) / (len(values) * denom)


def compare_schedulers(jobs: List[Job]):
    """Compare all scheduling algorithms"""
    
    schedulers = {
        'MLFQ': MLFQScheduler(num_queues=3, boost_interval=50),
        'STCF': STCFScheduler(),
        'Round Robin': RoundRobinScheduler(time_quantum=2),
        'FIFO': FIFOScheduler(),
        'SJF': SJFScheduler()
    }
    
    print("=" * 80)
    print("SCHEDULER COMPARISON")
    print("=" * 80)
    
    for name, scheduler in schedulers.items():
        completed, metrics = scheduler.schedule(jobs)
        
        print(f"\n{name}:")
        print(f"  Average Turnaround Time: {metrics['avg_turnaround']:.2f}")
        print(f"  Average Response Time: {metrics['avg_response']:.2f}")
        print(f"  Jain's Fairness Index (turnaround): {calculate_jains_fairness(metrics['turnaround_times']):.4f}")
        print(f"  Jain's Fairness Index (response): {calculate_jains_fairness(metrics['response_times']):.4f}")


if __name__ == "__main__":
    # Test 1: Simple jobs with same arrival time
    print("\nTest 1: Jobs arriving at same time")
    jobs1 = [
        Job(1, 0, 10, 10),
        Job(2, 0, 5, 5),
        Job(3, 0, 8, 8)
    ]
    compare_schedulers(jobs1)
    
    # Test 2: Staggered arrivals
    print("\n" + "=" * 80)
    print("\nTest 2: Staggered arrivals")
    jobs2 = [
        Job(1, 0, 15, 15),
        Job(2, 5, 3, 3),
        Job(3, 7, 4, 4),
        Job(4, 10, 2, 2)
    ]
    compare_schedulers(jobs2)
    
    # Test 3: One long job with many short jobs
    print("\n" + "=" * 80)
    print("\nTest 3: One long job with many short jobs")
    jobs3 = [Job(1, 0, 100, 100)]
    for i in range(5):
        jobs3.append(Job(i+2, 10 + i*5, 5, 5))
    compare_schedulers(jobs3)
    
    # Test 4: MLFQ Priority behavior
    print("\n" + "=" * 80)
    print("\nTest 4: MLFQ Priority Behavior")
    jobs4 = [
        Job(1, 0, 20, 20),
        Job(2, 5, 5, 5),
        Job(3, 10, 5, 5)
    ]
    
    mlfq = MLFQScheduler(num_queues=3, boost_interval=None)
    completed, metrics = mlfq.schedule(jobs4)
    
    print("\nMLFQ Execution Timeline (time, job_id, priority_level, status):")
    for i in range(0, min(30, len(metrics['timeline'])), 1):
        time, job_id, priority, status = metrics['timeline'][i]
        if job_id >= 0:
            print(f"  Time {time:3d}: Job {job_id} at Priority {priority} - {status}")
    
    print(f"\n  Average Turnaround Time: {metrics['avg_turnaround']:.2f}")
    print(f"  Average Response Time: {metrics['avg_response']:.2f}")
    print(f"  Jain's Fairness Index (turnaround): {calculate_jains_fairness(metrics['turnaround_times']):.4f}")
    print(f"  Jain's Fairness Index (response): {calculate_jains_fairness(metrics['response_times']):.4f}")
    
    # Test 5: MLFQ with I/O operations (job relinquishes CPU but stays at same priority)
    print("\n" + "=" * 80)
    print("\nTest 5: MLFQ with I/O Operations (No demotion on I/O)")
    jobs5 = [
        Job(1, 0, 20, 20, io_operations=[5, 10, 15], io_duration=3),  # Job with I/O
        Job(2, 2, 10, 10),  # CPU-bound job
        Job(3, 5, 8, 8)     # CPU-bound job
    ]
    
    mlfq_io = MLFQScheduler(num_queues=3, time_quantum=[2, 4, 8], boost_interval=None)
    completed_io, metrics_io = mlfq_io.schedule(jobs5)
    
    print("\nMLFQ with I/O Timeline (first 40 time units):")
    print("Note: Job 1 performs I/O at CPU times 5, 10, 15 but stays at same priority")
    for i in range(0, min(40, len(metrics_io['timeline'])), 1):
        time, job_id, priority, status = metrics_io['timeline'][i]
        if job_id >= 0 or status == "IDLE":
            if status == "IO":
                print(f"  Time {time:3d}: Job {job_id} at Priority {priority} - {status} (relinquished CPU)")
            elif status == "IDLE":
                print(f"  Time {time:3d}: IDLE (waiting for I/O)")
            else:
                print(f"  Time {time:3d}: Job {job_id} at Priority {priority} - {status}")
    
    print(f"\n  Average Turnaround Time: {metrics_io['avg_turnaround']:.2f}")
    print(f"  Average Response Time: {metrics_io['avg_response']:.2f}")
    print(f"  Jain's Fairness Index (turnaround): {calculate_jains_fairness(metrics_io['turnaround_times']):.4f}")
    print(f"  Jain's Fairness Index (response): {calculate_jains_fairness(metrics_io['response_times']):.4f}")
    
    
    print("\n" + "=" * 80)