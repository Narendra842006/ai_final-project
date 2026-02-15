"""
Real-Time Priority Queue using Max-Heap Algorithm
Implements dynamic re-ranking for high-risk patients
"""
import heapq
from typing import List, Tuple, Optional
from datetime import datetime
from .models import RiskLevel, QueueEntry


class PriorityQueueManager:
    """
    Max-Heap based Priority Queue with dynamic re-ranking
    Higher priority scores appear first
    """
    
    def __init__(self):
        self._heap: List[Tuple[float, datetime, QueueEntry]] = []
        self._entry_finder = {}  # patient_id -> entry mapping
        self._counter = 0  # Unique sequence count for tie-breaking
    
    def calculate_priority_score(
        self,
        risk_level: RiskLevel,
        heart_rate: float,
        bp_systolic: float,
        bp_diastolic: float,
        temperature: float,
        age: int,
        symptoms: List[str]
    ) -> float:
        """
        Calculate priority score based on AI risk level and vital severity
        
        Formula:
        - Base score from risk level (High=70, Medium=40, Low=10, Immediate=100)
        - Vital sign severity bonuses (0-20 points)
        - Age factor (elderly +5, children +5)
        - Symptom severity (+0-10)
        
        Returns: Priority score (0-100)
        """
        # Base score from AI risk level
        risk_scores = {
            RiskLevel.IMMEDIATE: 100,
            RiskLevel.HIGH: 70,
            RiskLevel.MEDIUM: 40,
            RiskLevel.LOW: 10
        }
        base_score = risk_scores.get(risk_level, 10)
        
        # Vital sign severity scoring
        vital_score = 0
        
        # Heart rate severity
        if heart_rate > 130 or heart_rate < 50:
            vital_score += 10  # Critical tachycardia/bradycardia
        elif heart_rate > 100 or heart_rate < 60:
            vital_score += 5   # Abnormal but stable
        
        # Blood pressure severity
        if bp_systolic > 180 or bp_systolic < 90:
            vital_score += 10  # Hypertensive crisis or hypotension
        elif bp_systolic > 160 or bp_systolic < 100:
            vital_score += 5   # Stage 2 hypertension
        
        # Temperature severity
        if temperature > 103 or temperature < 95:
            vital_score += 5   # High fever or hypothermia
        elif temperature > 100.4:
            vital_score += 2   # Fever
        
        # Age factor
        age_bonus = 0
        if age > 65:  # Elderly
            age_bonus = 5
        elif age < 5:  # Pediatric
            age_bonus = 5
        elif age < 1:  # Infant
            age_bonus = 10
        
        # Symptom severity
        symptom_score = 0
        critical_symptoms = ['chest pain', 'difficulty breathing', 'unconscious', 'stroke', 'severe bleeding']
        for symptom in symptoms:
            if any(crit in symptom.lower() for crit in critical_symptoms):
                symptom_score += 5
                break
        
        # Final priority score (capped at 100)
        total_score = min(base_score + vital_score + age_bonus + symptom_score, 100)
        return round(total_score, 2)
    
    def add_patient(self, entry: QueueEntry) -> int:
        """
        Add patient to priority queue with dynamic re-ranking
        Returns: Position in queue (1-indexed)
        """
        # Use negative priority for max-heap (Python's heapq is min-heap)
        priority = -entry.priority_score
        
        # Tie-breaker: earlier arrival time gets priority
        arrival_time = entry.arrival_time
        
        # Create heap entry: (priority, arrival_time, counter, entry)
        # Counter ensures FIFO for same priority
        heap_entry = (priority, arrival_time, self._counter, entry)
        heapq.heappush(self._heap, heap_entry)
        
        self._entry_finder[entry.patient_id] = heap_entry
        self._counter += 1
        
        # Calculate position
        position = self._calculate_position(entry.patient_id)
        return position
    
    def remove_patient(self, patient_id: str) -> Optional[QueueEntry]:
        """Remove patient from queue"""
        if patient_id not in self._entry_finder:
            return None
        
        entry = self._entry_finder.pop(patient_id)
        # Mark as removed (lazy deletion)
        self._heap = [e for e in self._heap if e[3].patient_id != patient_id]
        heapq.heapify(self._heap)
        return entry[3]
    
    def get_next_patient(self) -> Optional[QueueEntry]:
        """
        Get highest priority patient (pop from queue)
        Returns: QueueEntry or None if empty
        """
        while self._heap:
            priority, arrival_time, counter, entry = heapq.heappop(self._heap)
            
            # Check if entry still valid (not removed)
            if entry.patient_id in self._entry_finder:
                del self._entry_finder[entry.patient_id]
                return entry
        
        return None
    
    def peek_queue(self, limit: int = 10) -> List[QueueEntry]:
        """
        View top N patients without removing them
        Returns: List of QueueEntry objects
        """
        # Create sorted copy
        sorted_heap = sorted(self._heap, key=lambda x: (x[0], x[1], x[2]))
        return [entry[3] for entry in sorted_heap[:limit]]
    
    def update_priority(self, patient_id: str, new_priority_score: float) -> int:
        """
        Update patient priority (for dynamic re-ranking)
        Returns: New position in queue
        """
        # Remove old entry
        old_entry = self.remove_patient(patient_id)
        if not old_entry:
            raise ValueError(f"Patient {patient_id} not found in queue")
        
        # Create updated entry
        updated_entry = QueueEntry(
            patient_id=old_entry.patient_id,
            email=old_entry.email,
            priority_score=new_priority_score,
            risk_level=old_entry.risk_level,
            department=old_entry.department,
            arrival_time=old_entry.arrival_time,
            vitals_summary=old_entry.vitals_summary,
            immediate=new_priority_score >= 90
        )
        
        # Re-add with new priority
        return self.add_patient(updated_entry)
    
    def _calculate_position(self, patient_id: str) -> int:
        """Calculate patient's current position in queue"""
        if patient_id not in self._entry_finder:
            return -1
        
        sorted_heap = sorted(self._heap, key=lambda x: (x[0], x[1], x[2]))
        for idx, entry in enumerate(sorted_heap, 1):
            if entry[3].patient_id == patient_id:
                return idx
        return -1
    
    def get_position(self, patient_id: str) -> int:
        """Get current position of patient in queue"""
        return self._calculate_position(patient_id)
    
    def get_queue_size(self) -> int:
        """Get total number of patients in queue"""
        return len(self._entry_finder)
    
    def get_immediate_count(self) -> int:
        """Get count of immediate/critical patients"""
        return sum(1 for _, _, _, entry in self._heap if entry.immediate)
    
    def clear_queue(self):
        """Clear entire queue (admin function)"""
        self._heap.clear()
        self._entry_finder.clear()
        self._counter = 0


# Global queue instance
global_queue = PriorityQueueManager()
