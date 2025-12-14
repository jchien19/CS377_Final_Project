from collections import deque
from dataclasses import dataclass
from typing import List, Dict
import statistics

@dataclass
class Job:
    """Represents a job in the system"""
    job_id: int
    arrival_time: int
    burst_time: int
    remaining_time: int
    priority: int = 0  # Treat 0 as the highest priority
    time_in_queue: int = 0  # Time spent at current priority level
    start_time: int = -1
    completion_time: int = -1
    waiting_for_io: bool = False # Flag to indicate if job is waiting for IO
    io_return_time: int = -1
    io_duration: int = 5  # Default IO duration, can change as desired
    io_operations: deque[int] = None  # store as deque

    def __post_init__(self):
        self.remaining_time = self.burst_time # Initialize remaining_time, set to burst_time to start
        if self.io_operations is None:
            self.io_operations = deque()
        else:
            # Ensure io_operations is sorted, earlier times first
            self.io_operations = deque(sorted(self.io_operations))

    def needs_io(self, cpu_time_used: int) -> bool:
        # Check if job needs to perform I/O at this CPU time
        if self.io_operations and cpu_time_used == self.io_operations[0]:
            self.io_operations.popleft()  # consume the event (ensure its removed from the queue)
            return True
        return False
    
class MetricCalculator:
    """Utility class to calculate scheduling metrics"""
    
    @staticmethod
    def calculate_metrics(completed: List[Job]) -> Dict:
        turnaround_times = [j.completion_time - j.arrival_time for j in completed]
        response_times = [j.start_time - j.arrival_time for j in completed]
        
        return {
            'avg_turnaround': statistics.mean(turnaround_times),
            'avg_response': statistics.mean(response_times),
            'turnaround_times': turnaround_times,
            'response_times': response_times
        }