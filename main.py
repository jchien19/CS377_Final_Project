from typing import List
from mlfq import MLFQScheduler
from baselines import FIFOScheduler, SJFScheduler, STCFScheduler, RoundRobinScheduler
from job import Job
from cfs import CFSScheduler

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
        'SJF': SJFScheduler(),
        'CFS': CFSScheduler()
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
    
    print("\n" + "=" * 80)