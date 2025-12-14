import copy
from collections import deque
from typing import List, Dict, Tuple
from job import Job, MetricCalculator

class FIFOScheduler:
    """First In First Out Scheduler"""
    
    def schedule(self, jobs: List[Job]) -> Tuple[List[Job], Dict]:
        jobs = [copy.deepcopy(job) for job in jobs]
        jobs.sort(key=lambda x: x.arrival_time)
        
        current_time = 0
        completed = []
        
        for job in jobs:
            if current_time < job.arrival_time:
                current_time = job.arrival_time
            
            job.start_time = current_time
            current_time += job.burst_time
            job.completion_time = current_time
            completed.append(job)
 
        return completed, MetricCalculator.calculate_metrics(completed)


class SJFScheduler:
    """Shortest Job First Scheduler"""
    
    def schedule(self, jobs: List[Job]) -> Tuple[List[Job], Dict]:
        jobs = [copy.deepcopy(job) for job in jobs]
        current_time = 0
        completed = []
        remaining = jobs[:]
        
        while remaining:
            # Get available jobs
            available = [j for j in remaining if j.arrival_time <= current_time]
            
            if not available:
                current_time = min(j.arrival_time for j in remaining)
                continue
            
            # Pick shortest job
            job = min(available, key=lambda x: x.burst_time)
            remaining.remove(job)
            
            job.start_time = current_time
            current_time += job.burst_time
            job.completion_time = current_time
            completed.append(job)
        
        return completed, MetricCalculator.calculate_metrics(completed)


class STCFScheduler:
    """Shortest Time-to-Completion First Scheduler"""
    
    def schedule(self, jobs: List[Job]) -> Tuple[List[Job], Dict]:
        jobs = [copy.deepcopy(job) for job in jobs]
        current_time = 0
        completed = []
        remaining = jobs[:]
        
        while remaining:
            # Get available jobs
            available = [j for j in remaining if j.arrival_time <= current_time]
            
            if not available:
                current_time = min(j.arrival_time for j in remaining)
                continue
            
            # Pick job with shortest remaining time
            job = min(available, key=lambda x: x.remaining_time)
            
            if job.start_time == -1:
                job.start_time = current_time
            
            # Execute for 1 time unit
            job.remaining_time -= 1
            current_time += 1
            
            if job.remaining_time == 0:
                job.completion_time = current_time
                completed.append(job)
                remaining.remove(job)
        
        return completed, MetricCalculator.calculate_metrics(completed)

class RoundRobinScheduler:
    """Round Robin Scheduler"""
    
    def __init__(self, time_quantum=2):
        self.time_quantum = time_quantum
    
    def schedule(self, jobs: List[Job]) -> Tuple[List[Job], Dict]:
        jobs = [copy.deepcopy(job) for job in jobs]
        current_time = 0
        completed = []
        ready_queue = deque()
        waiting_jobs = sorted(jobs, key=lambda x: x.arrival_time)
        
        while waiting_jobs or ready_queue:
            # Add newly arrived jobs
            while waiting_jobs and waiting_jobs[0].arrival_time <= current_time:
                ready_queue.append(waiting_jobs.pop(0))
            
            if not ready_queue:
                current_time = waiting_jobs[0].arrival_time
                continue
            
            job = ready_queue.popleft()
            
            if job.start_time == -1:
                job.start_time = current_time
            
            # Execute for quantum or remaining time
            exec_time = min(self.time_quantum, job.remaining_time)
            job.remaining_time -= exec_time
            current_time += exec_time
            
            # Add jobs that arrived during execution
            while waiting_jobs and waiting_jobs[0].arrival_time <= current_time:
                ready_queue.append(waiting_jobs.pop(0))
            
            if job.remaining_time > 0:
                ready_queue.append(job)
            else:
                job.completion_time = current_time
                completed.append(job)
        
        return completed, MetricCalculator.calculate_metrics(completed)