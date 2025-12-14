import copy
from collections import deque
from typing import List, Dict, Tuple
from job import Job, MetricCalculator

class MLFQScheduler:
    """Multi-Level Feedback Queue Scheduler"""
    
    def __init__(self, num_queues=3, time_quantum=None, time_allotments=None, boost_interval=None):
        """
        Args:
            num_queues: Number of priority queues
            time_quantum: List of time slices for each queue (defaults to [1, 2, 4, ...])
            time_allotments: Time allotment before demotion (defaults to 2x quantum)
            boost_interval: Period S for priority boost (Rule 5)
        """
        self.num_queues = num_queues
        self.queues = [deque() for _ in range(num_queues)]
        
        # Default quantum: exponentially increasing
        self.time_quantum = [2**i for i in range(num_queues)] if time_quantum is None else time_quantum
            
        # Default allotment: 2x the quantum for each level
        self.time_allotments = [2*q for q in self.time_quantum] if time_allotments is None else time_allotments
            
        self.boost_interval = boost_interval
        self.time_since_boost = 0
        
    def schedule(self, jobs: List[Job]) -> Tuple[List[Job], Dict]:
        """Run MLFQ scheduling simulation"""
        jobs = [copy.deepcopy(job) for job in jobs]
        current_time = 0
        completed = []
        waiting_jobs = sorted(jobs, key=lambda x: x.arrival_time)
        io_jobs = []  # Jobs waiting for IO to complete
        current_job = None
        quantum_remaining = 0
        cpu_time_used = 0  # Track how much CPU time current job has used
        
        timeline = []  # For visualization
        
        while waiting_jobs or any(self.queues) or current_job or io_jobs:
            # Rule 5: Priority boost
            if self.boost_interval and self.time_since_boost >= self.boost_interval:
                self._boost_all_jobs(current_job)
                self.time_since_boost = 0
            
            # Check for IO completions and add back to ready queue, put back at same priority
            jobs_returned = []
            for job in io_jobs:
                if current_time >= job.io_return_time:
                    job.waiting_for_io = False
                    self.queues[job.priority].append(job)
                    jobs_returned.append(job)
            
            for job in jobs_returned:
                io_jobs.remove(job)
            
            # Add newly arrived jobs to highest priority queue
            while waiting_jobs and waiting_jobs[0].arrival_time <= current_time:
                job = waiting_jobs.pop(0)
                job.priority = 0
                job.time_in_queue = 0
                self.queues[0].append(job)
            
            # If current job finished its quantum, completed, or went to IO
            if current_job and (quantum_remaining <= 0 or current_job.remaining_time <= 0 or current_job.waiting_for_io):
                if current_job.remaining_time <= 0:
                    current_job.completion_time = current_time
                    completed.append(current_job)
                    current_job = None
                    cpu_time_used = 0
                elif current_job.waiting_for_io:
                    # Job had IO, does not get demoted yet
                    io_jobs.append(current_job)
                    current_job = None
                    cpu_time_used = 0
                else:
                    # Check if job exhausted time allotment at current level
                    if current_job.time_in_queue >= self.time_allotments[current_job.priority]:
                        # If so, demote to lower priority
                        current_job.priority = min(current_job.priority + 1, self.num_queues - 1)
                        current_job.time_in_queue = 0
                    
                    # Put back in appropriate queue
                    self.queues[current_job.priority].append(current_job)
                    current_job = None
                    cpu_time_used = 0
            
            # Select next job, search for highest job in queues, otherwise round robin within same priority
            # If there are no more jobs, current_job remains None
            if not current_job:
                for priority in range(self.num_queues):
                    if self.queues[priority]:
                        current_job = self.queues[priority].popleft()
                        quantum_remaining = self.time_quantum[priority]
                        cpu_time_used = 0
                        if current_job.start_time == -1:
                            current_job.start_time = current_time
                        break
            
            # Execute current job
            if current_job:
                # Check if job needs IO before executing this time unit
                total_cpu_time = current_job.burst_time - current_job.remaining_time # how much time job has used so far
                if current_job.needs_io(total_cpu_time):
                    # Job relinquishes CPU for IO
                    current_job.waiting_for_io = True
                    current_job.io_return_time = current_time + current_job.io_duration # set when job will return from IO
                    timeline.append((current_time, current_job.job_id, current_job.priority, "IO"))
                else:
                    # Otherwise, execute for 1 time unit
                    current_job.remaining_time -= 1
                    current_job.time_in_queue += 1
                    quantum_remaining -= 1
                    cpu_time_used += 1
                    timeline.append((current_time, current_job.job_id, current_job.priority, "RUNNING"))
            else:
                # CPU is idle, no job to run
                timeline.append((current_time, -1, -1, "IDLE"))
            
            # Update time counters
            current_time += 1
            self.time_since_boost += 1
        
        # Calculate metrics
        metrics = MetricCalculator.calculate_metrics(completed)
        metrics['timeline'] = timeline # For visualization
        return completed, metrics
    
    def _boost_all_jobs(self, current_job):
        """Move all jobs to highest priority queue"""
        all_jobs = []
        
        # Boost jobs from all queues
        for q in self.queues:
            while q:
                job = q.popleft()
                # Reset priority and time in queue
                job.priority = 0
                job.time_in_queue = 0
                all_jobs.append(job)
        
        # Boost current job too
        if current_job:
            current_job.priority = 0
            current_job.time_in_queue = 0
        
        # Put all jobs back in with highest priority
        for job in all_jobs:
            self.queues[0].append(job)
    