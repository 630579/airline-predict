"""
Module for predicting passenger load and ticket demand
"""
import statistics
from datetime import datetime, timedelta

class LoadPredictor:
    def __init__(self):
        self.historical_data = {}
        
    def predict_load(self, flights_data):
        """Predict passenger load for all flights"""
        predictions = []
        
        for flight in flights_data:
            prediction = self._predict_single_flight_load(flight)
            predictions.append(prediction)
        
        return predictions
    
    def _predict_single_flight_load(self, flight):
        """Predict load for a single flight"""
        flight_id = flight['flight_id']
        
        # Extract passenger data from logs
        passenger_logs = [log for log in flight['logs'] if log['log_type'] == 'passenger_load']
        
        if not passenger_logs:
            # Use default prediction
            return self._default_prediction(flight_id)
        
        # Analyze historical patterns
        passenger_counts = [log['metrics'].get('passenger_count', 0) for log in passenger_logs]
        load_factors = [log['metrics'].get('load_factor', 0) for log in passenger_logs]
        
        # Calculate predictions
        avg_passengers = statistics.mean(passenger_counts) if passenger_counts else 0
        avg_load_factor = statistics.mean(load_factors) if load_factors else 0
        
        # Adjust for trends
        trend = self._calculate_trend(passenger_logs)
        
        # Consider special factors
        adjustment = self._get_demand_adjustment()
        
        # Final prediction
        predicted_passengers = avg_passengers * (1 + trend) * (1 + adjustment)
        predicted_load_factor = avg_load_factor * (1 + trend) * (1 + adjustment)
        
        # Check for scenarios
        capacity = 180  # Default capacity
        scenarios = self._analyze_scenarios(predicted_passengers, capacity)
        
        return {
            'flight_id': flight_id,
            'aircraft_id': flight['aircraft_id'],
            'predicted_passengers': int(predicted_passengers),
            'predicted_load_factor': min(1.0, predicted_load_factor),  # Cap at 100%
            'capacity': capacity,
            'available_seats': max(0, capacity - int(predicted_passengers)),
            'scenarios': scenarios,
            'trend': 'increasing' if trend > 0.05 else 'decreasing' if trend < -0.05 else 'stable',
            'demand_level': self._get_demand_level(predicted_load_factor),
            'prediction_time': datetime.now().isoformat()
        }
    
    def _calculate_trend(self, passenger_logs):
        """Calculate passenger trend"""
        if len(passenger_logs) < 2:
            return 0
        
        # Simple trend calculation based on recent data
        recent_counts = [log['metrics'].get('passenger_count', 0) for log in passenger_logs[-5:]]
        if len(recent_counts) < 2:
            return 0
        
        # Calculate percentage change
        first = recent_counts[0]
        last = recent_counts[-1]
        
        if first == 0:
            return 0
        
        return (last - first) / first
    
    def _get_demand_adjustment(self):
        """Adjust prediction based on external factors"""
        adjustment = 0
        
        # Check for holidays
        today = datetime.now()
        holidays = [
            datetime(today.year, 1, 1),   # New Year
            datetime(today.year, 12, 25), # Christmas
            datetime(today.year, 10, 2),  # Gandhi Jayanti
            datetime(today.year, 8, 15),  # Independence Day
        ]
        
        for holiday in holidays:
            days_diff = abs((today - holiday).days)
            if days_diff <= 7:  # Week before/after holiday
                adjustment += 0.15  # 15% increase
        
        # Weekend adjustment
        if today.weekday() >= 5:  # Saturday or Sunday
            adjustment += 0.10
        
        # Seasonal adjustment (summer months)
        if 5 <= today.month <= 7:  # May-July
            adjustment += 0.20
        
        return adjustment
    
    def _analyze_scenarios(self, predicted_passengers, capacity):
        """Analyze booking scenarios"""
        scenarios = []
        
        # Overbooking scenario
        overbooking_threshold = capacity * 1.1  # 10% overbooking
        if predicted_passengers > overbooking_threshold:
            scenarios.append({
                'type': 'OVERBOOKING_RISK',
                'severity': 'HIGH',
                'message': f'Predicted passengers ({predicted_passengers:.0f}) exceed capacity by {(predicted_passengers/capacity - 1)*100:.1f}%'
            })
        
        # High demand scenario
        elif predicted_passengers > capacity * 0.9:
            scenarios.append({
                'type': 'HIGH_DEMAND',
                'severity': 'MEDIUM',
                'message': 'Flight expected to be nearly full'
            })
        
        # Low utilization scenario
        elif predicted_passengers < capacity * 0.4:
            scenarios.append({
                'type': 'LOW_UTILIZATION',
                'severity': 'LOW',
                'message': 'Flight may be underutilized'
            })
        
        # Normal scenario
        else:
            scenarios.append({
                'type': 'NORMAL_DEMAND',
                'severity': 'LOW',
                'message': 'Normal booking pattern expected'
            })
        
        return scenarios
    
    def _get_demand_level(self, load_factor):
        """Categorize demand level"""
        if load_factor > 0.9:
            return "VERY_HIGH"
        elif load_factor > 0.7:
            return "HIGH"
        elif load_factor > 0.5:
            return "MODERATE"
        elif load_factor > 0.3:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def _default_prediction(self, flight_id):
        """Default prediction when no data is available"""
        import random
        
        predicted_passengers = random.randint(80, 150)
        capacity = 180
        
        return {
            'flight_id': flight_id,
            'predicted_passengers': predicted_passengers,
            'predicted_load_factor': predicted_passengers / capacity,
            'capacity': capacity,
            'available_seats': capacity - predicted_passengers,
            'scenarios': [],
            'trend': 'stable',
            'demand_level': self._get_demand_level(predicted_passengers / capacity),
            'prediction_time': datetime.now().isoformat()
        }