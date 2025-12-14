"""
Test Cases for MLFQ (Multi-Level Feedback Queue) Scheduler
"""

from mlfq import Job, MLFQScheduler


def test_priority_demotion():
    """
    Test 1: Job gets demoted after using time allotment
    Long-running jobs should move to lower priority queues
    """
    print("=" * 60)
    print("TEST 1: Priority demotion")
    print("=" * 60)
    
    jobs = [
        Job(1, arrival_time=0, burst_time=15, remaining_time=15),
    ]
    
    print("Jobs:")
    print(f"  Job 1: arrival=0, burst=15")
    print("\nMLFQ Config: 3 queues, quantum=[1,2,4], no boost")
    
    scheduler = MLFQScheduler(num_queues=3, boost_interval=None)
    completed, metrics = scheduler.schedule(jobs)
    
    print("\nTimeline (showing priority changes):")
    prev_priority = -1
    for time, job_id, priority, status in metrics['timeline'][:20]:
        if job_id > 0 and priority != prev_priority:
            print(f"  Time {time}: Job {job_id} at Priority {priority}")
            prev_priority = priority
    
    print(f"\nAvg Turnaround Time: {metrics['avg_turnaround']:.2f}")


def test_new_job_priority():
    """
    Test 2: New jobs start at highest priority
    Short interactive jobs should be favored
    """
    print("\n" + "=" * 60)
    print("TEST 2: New jobs get highest priority")
    print("=" * 60)
    
    jobs = [
        Job(1, arrival_time=0, burst_time=20, remaining_time=20),  # Long job
        Job(2, arrival_time=5, burst_time=3, remaining_time=3),    # Short job arrives later
    ]
    
    print("Jobs:")
    for j in jobs:
        print(f"  Job {j.job_id}: arrival={j.arrival_time}, burst={j.burst_time}")
    
    scheduler = MLFQScheduler(num_queues=3, boost_interval=None)
    completed, metrics = scheduler.schedule(jobs)
    
    print("\nTimeline (first 15 time units):")
    for time, job_id, priority, status in metrics['timeline'][:15]:
        if job_id > 0:
            print(f"  Time {time}: Job {job_id} at Priority {priority} - {status}")
    
    print(f"\nAvg Response Time: {metrics['avg_response']:.2f}")


def test_priority_boost():
    """
    Test 3: Priority boost prevents starvation
    All jobs should be boosted to top priority periodically
    """
    print("\n" + "=" * 60)
    print("TEST 3: Priority boost (prevents starvation)")
    print("=" * 60)
    
    jobs = [
        Job(1, arrival_time=0, burst_time=30, remaining_time=30),
        Job(2, arrival_time=2, burst_time=5, remaining_time=5),
    ]
    
    print("Jobs:")
    for j in jobs:
        print(f"  Job {j.job_id}: arrival={j.arrival_time}, burst={j.burst_time}")
    print("\nMLFQ Config: boost_interval=10 (boost every 10 time units)")
    
    scheduler = MLFQScheduler(num_queues=3, boost_interval=10)
    completed, metrics = scheduler.schedule(jobs)
    
    print("\nTimeline showing boost effect:")
    prev_priority = {}
    for time, job_id, priority, status in metrics['timeline']:
        if job_id > 0:
            if job_id not in prev_priority or prev_priority[job_id] != priority:
                if prev_priority.get(job_id, -1) > priority:
                    print(f"  Time {time}: Job {job_id} BOOSTED to Priority {priority}")
                prev_priority[job_id] = priority
    
    print(f"\nAvg Turnaround Time: {metrics['avg_turnaround']:.2f}")


def test_round_robin_same_priority():
    """
    Test 4: Jobs at same priority use round-robin
    """
    print("\n" + "=" * 60)
    print("TEST 4: Round-robin within same priority")
    print("=" * 60)
    
    jobs = [
        Job(1, arrival_time=0, burst_time=4, remaining_time=4),
        Job(2, arrival_time=0, burst_time=4, remaining_time=4),
    ]
    
    print("Jobs:")
    for j in jobs:
        print(f"  Job {j.job_id}: arrival={j.arrival_time}, burst={j.burst_time}")
    
    scheduler = MLFQScheduler(num_queues=3, boost_interval=None)
    completed, metrics = scheduler.schedule(jobs)
    
    print("\nTimeline (should alternate between jobs):")
    for time, job_id, priority, status in metrics['timeline'][:10]:
        if job_id > 0:
            print(f"  Time {time}: Job {job_id} at Priority {priority}")
    
    print(f"\nAvg Response Time: {metrics['avg_response']:.2f}")


def test_io_behavior():
    """
    Test 5: I/O jobs don't get demoted when they release CPU
    """
    print("\n" + "=" * 60)
    print("TEST 5: I/O behavior (no demotion on voluntary release)")
    print("=" * 60)
    
    jobs = [
        Job(1, arrival_time=0, burst_time=10, remaining_time=10, 
            io_operations=[3, 6], io_duration=2),  # I/O at CPU time 3 and 6
        Job(2, arrival_time=1, burst_time=8, remaining_time=8),  # CPU-bound
    ]
    
    print("Jobs:")
    print(f"  Job 1: arrival=0, burst=10, I/O at CPU times 3,6")
    print(f"  Job 2: arrival=1, burst=8, CPU-bound")
    
    scheduler = MLFQScheduler(num_queues=3, boost_interval=None)
    completed, metrics = scheduler.schedule(jobs)
    
    print("\nTimeline (first 20 time units):")
    for time, job_id, priority, status in metrics['timeline'][:20]:
        if status != "IDLE":
            print(f"  Time {time}: Job {job_id} at Priority {priority} - {status}")
        else:
            print(f"  Time {time}: CPU IDLE (waiting for I/O)")
    
    print(f"\nAvg Turnaround Time: {metrics['avg_turnaround']:.2f}")


def test_multiple_queues():
    """
    Test 6: Verify jobs use different queue levels
    """
    print("\n" + "=" * 60)
    print("TEST 6: Jobs across multiple queue levels")
    print("=" * 60)
    
    jobs = [
        Job(1, arrival_time=0, burst_time=20, remaining_time=20),
    ]
    
    print("Jobs:")
    print(f"  Job 1: arrival=0, burst=20")
    print("\nMLFQ Config: quantum=[2,4,8], allotments=[4,8,16]")
    
    scheduler = MLFQScheduler(
        num_queues=3, 
        time_quantum=[2, 4, 8],
        time_allotments=[4, 8, 16],
        boost_interval=None
    )
    completed, metrics = scheduler.schedule(jobs)
    
    print("\nPriority level at each time:")
    current_priority = -1
    for time, job_id, priority, status in metrics['timeline']:
        if job_id > 0 and priority != current_priority:
            print(f"  Time {time}: Moved to Priority {priority} (quantum={scheduler.time_quantum[priority]})")
            current_priority = priority
    
    print(f"\nTotal time: {completed[0].completion_time}")


if __name__ == "__main__":
    test_priority_demotion()
    test_new_job_priority()
    test_priority_boost()
    test_round_robin_same_priority()
    test_io_behavior()
    test_multiple_queues()
    
    print("\n" + "=" * 60)
    print("All MLFQ tests completed!")
    print("=" * 60)

