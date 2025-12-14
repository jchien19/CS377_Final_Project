"""
Completely Fair Scheduler (CFS) Implementation

CFS is the default Linux process scheduler.
The key idea: give every process a "fair" share of the CPU.

How it works:
1. Each process tracks "virtual runtime" (vruntime) - how much CPU time it has used
2. The scheduler always picks the process with the LOWEST vruntime
3. As a process runs, its vruntime increases
4. This naturally balances CPU time across all processes

Example with 2 jobs (A and B):
- Time 0: A(vruntime=0), B(vruntime=0) -> pick A (tie-breaker)
- Time 1: A(vruntime=1), B(vruntime=0) -> pick B (lower vruntime)
- Time 2: A(vruntime=1), B(vruntime=1) -> pick A (tie-breaker)
- Time 3: A(vruntime=2), B(vruntime=1) -> pick B
- ... and so on, alternating fairly

Ours is simpler than real Linux CFS which uses:
- Red-black trees for O(log n) selection
- Nice values/weights for priority
- Target latency and minimum granularity
"""

import copy
from typing import List, Dict, Tuple
from job import Job, MetricCalculator


class CFSScheduler:
    """
    Completely Fair Scheduler
    
    Ensures fair CPU distribution by always running the process
    that has received the least CPU time so far.
    """
    
    def __init__(self, min_granularity=1):
        """
        Args:
            min_granularity: Minimum time slice before switching (default is 1)
            In real CFS, this prevents excessive context switches
        """
        self.min_granularity = min_granularity
    
    def schedule(self, jobs: List[Job]) -> Tuple[List[Job], Dict]:
        """
        Run CFS scheduling simulation.
        
        Args:
            jobs: List of jobs to schedule
            
        Returns:
            Tuple of (completed_jobs, metrics_dict)
        """
        # Deep copy jobs so we don't modify the originals
        jobs = [copy.deepcopy(job) for job in jobs]
        current_time = 0
        completed = []
        
        # Jobs that haven't arrived yet, sorted by arrival time
        waiting_jobs = sorted(jobs, key=lambda x: x.arrival_time)
        
        
        # vruntime tracks how much CPU time each job has "fairly" received
        # Lower vruntime = job deserves more CPU time
        # Dictionary: job_id -> vruntime value
        vruntime = {}
        
        # Jobs that are ready to run (have arrived)
        ready_jobs = []
        
        
        #  MAIN SCHEDULING LOOP
        
        while waiting_jobs or ready_jobs:
            # Add newly arrived jobs to ready queue
            
            # When a new job arrives, give it the minimum vruntime of all
            # currently ready jobs. This ensures new jobs get scheduled
            # soon (they're not stuck behind jobs with high vruntime).
            while waiting_jobs and waiting_jobs[0].arrival_time <= current_time:
                job = waiting_jobs.pop(0)
                
                # New job gets min vruntime so it gets a fair chance
                # If no jobs exist yet, start at 0
                min_vruntime = min(vruntime.values()) if vruntime else 0
                vruntime[job.job_id] = min_vruntime
                ready_jobs.append(job)
            
        
            #  Handle idle CPU (no ready jobs)
        
            if not ready_jobs:
                # Fast-forward time to next job arrival
                current_time = waiting_jobs[0].arrival_time
                continue
            
            
            # Pick the job with LOWEST vruntime
            # the least CPU time so far

            job = min(ready_jobs, key=lambda j: vruntime[j.job_id])
            
            # Record first time this job runs (for response time calculation)
            if job.start_time == -1:
                job.start_time = current_time
            
            
            # Execute the job for 1 time unit
            
            job.remaining_time -= 1
            current_time += 1
            
            # Increase vruntime as the job uses CPU
            # This makes other jobs more likely to be picked next
            vruntime[job.job_id] += 1
            
            
            # Check for new arrivals during execution
           
            while waiting_jobs and waiting_jobs[0].arrival_time <= current_time:
                new_job = waiting_jobs.pop(0)
                min_vruntime = min(vruntime.values()) if vruntime else 0
                vruntime[new_job.job_id] = min_vruntime
                ready_jobs.append(new_job)
            
            
            # Check if job completed

            if job.remaining_time == 0:
                job.completion_time = current_time
                completed.append(job)
                ready_jobs.remove(job)
                del vruntime[job.job_id]  # Clean up vruntime tracking
        
        # Calculate and return metrics
        return completed, MetricCalculator.calculate_metrics(completed)
