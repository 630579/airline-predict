"""
Module for optimizing crew scheduling
"""
from datetime import datetime, timedelta
import random

class CrewOptimizer:
    def __init__(self):
        self.crew_members = self._initialize_crew()
        self.schedule = {}
        
    def _initialize_crew(self):
        """Initialize crew database"""
        crew = []
        
        # Pilots
        for i in range(1, 11):
            crew.append({
                'crew_id': f"P{i:03d}",
                'name': f"Captain Pilot {i}",
                'role': 'pilot',
                'license_type': 'ATPL',
                'flight_hours': random.randint(500, 5000),
                'base': random.choice(['DEL', 'BOM', 'BLR']),
                'rest_hours': 0,
                'next_available': datetime.now(),
                'assigned_flights': []
            })
        
        # Flight Attendants
        for i in range(1, 21):
            crew.append({
                'crew_id': f"FA{i:03d}",
                'name': f"Flight Attendant {i}",
                'role': 'attendant',
                'type_ratings': ['A320', 'B737'] if i % 2 == 0 else ['B787', 'A350'],
                'base': random.choice(['DEL', 'BOM', 'BLR']),
                'rest_hours': 0,
                'next_available': datetime.now(),
                'assigned_flights': []
            })
        
        return crew
    
    def optimize_schedule(self, flights_data):
        """Optimize crew scheduling for all flights"""
        assignments = []
        
        for flight in flights_data:
            assignment = self._assign_crew_to_flight(flight)
            assignments.append(assignment)
        
        # Check for issues
        issues = self._check_schedule_issues(assignments)
        
        return {
            'assignments': assignments,
            'issues': issues,
            'summary': self._generate_summary(assignments)
        }
    
    def _assign_crew_to_flight(self, flight):
        """Assign crew to a specific flight"""
        flight_id = flight['flight_id']
        aircraft_id = flight['aircraft_id']
        
        # Get available crew
        available_pilots = [
            c for c in self.crew_members 
            if c['role'] == 'pilot' 
            and c['next_available'] <= datetime.now()
            and c['rest_hours'] <= 8  # Maximum duty time
        ]
        
        available_attendants = [
            c for c in self.crew_members 
            if c['role'] == 'attendant'
            and c['next_available'] <= datetime.now()
        ]
        
        # Select crew
        captain = random.choice(available_pilots[:5]) if available_pilots else None
        first_officer = random.choice(available_pilots[5:]) if len(available_pilots) > 5 else None
        attendants = random.sample(available_attendants, min(4, len(available_attendants)))
        
        # Update crew availability
        flight_duration = random.randint(1, 6)  # hours
        rest_period = timedelta(hours=flight_duration + 10)  # 10 hours rest minimum
        
        if captain:
            captain['next_available'] = datetime.now() + rest_period
            captain['assigned_flights'].append(flight_id)
        
        if first_officer:
            first_officer['next_available'] = datetime.now() + rest_period
            first_officer['assigned_flights'].append(flight_id)
        
        for attendant in attendants:
            attendant['next_available'] = datetime.now() + rest_period
            attendant['assigned_flights'].append(flight_id)
        
        return {
            'flight_id': flight_id,
            'aircraft_id': aircraft_id,
            'captain': captain['crew_id'] if captain else None,
            'first_officer': first_officer['crew_id'] if first_officer else None,
            'attendants': [a['crew_id'] for a in attendants],
            'crew_count': len(attendants) + (1 if captain else 0) + (1 if first_officer else 0),
            'assignment_time': datetime.now().isoformat()
        }
    
    def _check_schedule_issues(self, assignments):
        """Check for scheduling issues"""
        issues = []
        
        # Check for double booking
        crew_assignments = {}
        for assignment in assignments:
            flight_id = assignment['flight_id']
            
            for crew_role in ['captain', 'first_officer']:
                crew_id = assignment.get(crew_role)
                if crew_id:
                    if crew_id in crew_assignments:
                        issues.append({
                            'type': 'DOUBLE_BOOKING',
                            'crew_id': crew_id,
                            'flights': [crew_assignments[crew_id], flight_id],
                            'severity': 'HIGH'
                        })
                    crew_assignments[crew_id] = flight_id
            
            for attendant_id in assignment.get('attendants', []):
                if attendant_id in crew_assignments:
                    issues.append({
                        'type': 'DOUBLE_BOOKING',
                        'crew_id': attendant_id,
                        'flights': [crew_assignments[attendant_id], flight_id],
                        'severity': 'MEDIUM'
                    })
                crew_assignments[attendant_id] = flight_id
        
        # Check for crew shortages
        for assignment in assignments:
            if not assignment.get('captain') or not assignment.get('first_officer'):
                issues.append({
                    'type': 'CREW_SHORTAGE',
                    'flight_id': assignment['flight_id'],
                    'missing_role': 'captain' if not assignment.get('captain') else 'first_officer',
                    'severity': 'CRITICAL'
                })
        
        return issues
    
    def _generate_summary(self, assignments):
        """Generate crew scheduling summary"""
        total_assignments = len(assignments)
        crew_utilization = {}
        
        for assignment in assignments:
            for crew_role in ['captain', 'first_officer']:
                crew_id = assignment.get(crew_role)
                if crew_id:
                    crew_utilization[crew_id] = crew_utilization.get(crew_id, 0) + 1
            
            for attendant_id in assignment.get('attendants', []):
                crew_utilization[attendant_id] = crew_utilization.get(attendant_id, 0) + 1
        
        return {
            'total_flights_scheduled': total_assignments,
            'total_crew_utilized': len(crew_utilization),
            'avg_flights_per_crew': sum(crew_utilization.values()) / len(crew_utilization) if crew_utilization else 0,
            'max_flights_per_crew': max(crew_utilization.values()) if crew_utilization else 0
        }