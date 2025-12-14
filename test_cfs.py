"""
Test Cases for CFS (Completely Fair Scheduler)
"""

from mlfq import Job
from cfs import CFSScheduler


def test_same_arrival_time():
    """
    Test 1: All jobs arrive at the same time
    CFS should fairly alternate between them
    """
    print("=" * 60)
    print("TEST 1: Jobs arriving at same time")
    print("=" * 60)
    
    jobs = [
        Job(1, arrival_time=0, burst_time=6, remaining_time=6),
        Job(2, arrival_time=0, burst_time=4, remaining_time=4),
        Job(3, arrival_time=0, burst_time=2, remaining_time=2),
    ]
    
    print("Jobs:")
    for j in jobs:
        print(f"  Job {j.job_id}: arrival={j.arrival_time}, burst={j.burst_time}")
    
    scheduler = CFSScheduler()
    completed, metrics = scheduler.schedule(jobs)
    
    print("\nResults:")
    print(f"  Avg Turnaround Time: {metrics['avg_turnaround']:.2f}")
    print(f"  Avg Response Time: {metrics['avg_response']:.2f}")
    
    print("\nCompleted Jobs:")
    for job in completed:
        print(f"  Job {job.job_id}: start={job.start_time}, completion={job.completion_time}")


def test_staggered_arrivals():
    """
    Test 2: Jobs arrive at different times
    New arrivals get min vruntime so they're scheduled fairly
    """
    print("\n" + "=" * 60)
    print("TEST 2: Staggered arrivals")
    print("=" * 60)
    
    jobs = [
        Job(1, arrival_time=0, burst_time=10, remaining_time=10),
        Job(2, arrival_time=3, burst_time=4, remaining_time=4),
        Job(3, arrival_time=6, burst_time=2, remaining_time=2),
    ]
    
    print("Jobs:")
    for j in jobs:
        print(f"  Job {j.job_id}: arrival={j.arrival_time}, burst={j.burst_time}")
    
    scheduler = CFSScheduler()
    completed, metrics = scheduler.schedule(jobs)
    
    print("\nResults:")
    print(f"  Avg Turnaround Time: {metrics['avg_turnaround']:.2f}")
    print(f"  Avg Response Time: {metrics['avg_response']:.2f}")
    
    print("\nCompleted Jobs:")
    for job in completed:
        print(f"  Job {job.job_id}: start={job.start_time}, completion={job.completion_time}")


def test_single_job():
    """
    Test 3: Single job - simplest case
    """
    print("\n" + "=" * 60)
    print("TEST 3: Single job")
    print("=" * 60)
    
    jobs = [
        Job(1, arrival_time=0, burst_time=5, remaining_time=5),
    ]
    
    print("Jobs:")
    print(f"  Job 1: arrival=0, burst=5")
    
    scheduler = CFSScheduler()
    completed, metrics = scheduler.schedule(jobs)
    
    print("\nResults:")
    print(f"  Avg Turnaround Time: {metrics['avg_turnaround']:.2f}")
    print(f"  Avg Response Time: {metrics['avg_response']:.2f}")
    
    print("\nCompleted Jobs:")
    for job in completed:
        print(f"  Job {job.job_id}: start={job.start_time}, completion={job.completion_time}")


def test_long_vs_short():
    """
    Test 4: One long job vs many short jobs
    CFS ensures short jobs aren't starved
    """
    print("\n" + "=" * 60)
    print("TEST 4: One long job vs short jobs")
    print("=" * 60)
    
    jobs = [
        Job(1, arrival_time=0, burst_time=20, remaining_time=20),  # Long job
        Job(2, arrival_time=2, burst_time=2, remaining_time=2),    # Short
        Job(3, arrival_time=4, burst_time=2, remaining_time=2),    # Short
    ]
    
    print("Jobs:")
    for j in jobs:
        print(f"  Job {j.job_id}: arrival={j.arrival_time}, burst={j.burst_time}")
    
    scheduler = CFSScheduler()
    completed, metrics = scheduler.schedule(jobs)
    
    print("\nResults:")
    print(f"  Avg Turnaround Time: {metrics['avg_turnaround']:.2f}")
    print(f"  Avg Response Time: {metrics['avg_response']:.2f}")
    
    print("\nCompleted Jobs (order shows fairness):")
    for job in completed:
        print(f"  Job {job.job_id}: start={job.start_time}, completion={job.completion_time}")


def test_equal_jobs():
    """
    Test 5: All jobs have equal burst time
    CFS should give perfectly fair scheduling
    """
    print("\n" + "=" * 60)
    print("TEST 5: Equal burst times (perfect fairness test)")
    print("=" * 60)
    
    jobs = [
        Job(1, arrival_time=0, burst_time=4, remaining_time=4),
        Job(2, arrival_time=0, burst_time=4, remaining_time=4),
        Job(3, arrival_time=0, burst_time=4, remaining_time=4),
    ]
    
    print("Jobs:")
    for j in jobs:
        print(f"  Job {j.job_id}: arrival={j.arrival_time}, burst={j.burst_time}")
    
    scheduler = CFSScheduler()
    completed, metrics = scheduler.schedule(jobs)
    
    print("\nResults:")
    print(f"  Avg Turnaround Time: {metrics['avg_turnaround']:.2f}")
    print(f"  Avg Response Time: {metrics['avg_response']:.2f}")
    
    print("\nCompleted Jobs:")
    for job in completed:
        turnaround = job.completion_time - job.arrival_time
        print(f"  Job {job.job_id}: turnaround={turnaround}")


if __name__ == "__main__":
    test_same_arrival_time()
    test_staggered_arrivals()
    test_single_job()
    test_long_vs_short()
    test_equal_jobs()
    
    print("\n" + "=" * 60)
    print("All CFS tests completed!")
    print("=" * 60)

