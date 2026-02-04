"""
Module for predicting flight delays
"""
import json
from datetime import datetime, timedelta

class DelayPredictor:
    def __init__(self):
        self.thresholds = {
            'crosswind_limit': 40,  # knots
            'visibility_limit': 1500,  # meters
            'engine_thrust_deviation': 20,  # percentage
            'runway_queue_limit': 25,  # minutes
            'turbulence_threshold': 'moderate'
        }
    
    def predict_delays(self, flights_data):
        """Predict delays for all flights"""
        predictions = []
        
        for flight in flights_data:
            prediction = self._predict_single_flight_delay(flight)
            if prediction['predicted_delay_minutes'] > 0:
                predictions.append(prediction)
        
        return predictions
    
    def _predict_single_flight_delay(self, flight):
        """Predict delay for a single flight"""
        flight_id = flight['flight_id']
        logs = flight['logs']
        
        delay_minutes = 0
        reasons = []
        
        # Analyze logs for delay indicators
        for log in logs:
            # Weather issues
            if log['log_type'] == 'weather_data':
                metrics = log['metrics']
                
                if metrics.get('crosswind', 0) > self.thresholds['crosswind_limit']:
                    delay = min(60, metrics['crosswind'] - self.thresholds['crosswind_limit'])
                    delay_minutes += delay
                    reasons.append(f"High crosswind ({metrics['crosswind']:.1f} knots)")
                
                if metrics.get('visibility', float('inf')) < self.thresholds['visibility_limit']:
                    delay_minutes += 30
                    reasons.append(f"Low visibility ({metrics['visibility']:.0f} meters)")
                
                if metrics.get('thunderstorm', False):
                    delay_minutes += 45
                    reasons.append("Thunderstorm detected")
                
                if metrics.get('turbulence', '') in ['severe', 'extreme']:
                    delay_minutes += 20
                    reasons.append(f"{metrics['turbulence'].title()} turbulence")
            
            # Maintenance issues
            elif log['log_type'] == 'engine_performance':
                metrics = log['metrics']
                
                if 'engine_thrust' in metrics:
                    thrust = metrics['engine_thrust']
                    if abs(thrust - 100) > self.thresholds['engine_thrust_deviation']:
                        delay_minutes += 60
                        reasons.append(f"Engine thrust deviation ({thrust:.1f}%)")
                
                if metrics.get('engine_vibration', 0) > 3.0:
                    delay_minutes += 90
                    reasons.append(f"High engine vibration ({metrics['engine_vibration']:.2f})")
            
            # Operational issues
            elif log['log_type'] == 'passenger_load':
                metrics = log['metrics']
                
                # Simulate boarding delays for high load
                load_factor = metrics.get('load_factor', 0)
                if load_factor > 0.9:
                    delay_minutes += 15
                    reasons.append(f"High passenger load ({load_factor:.1%})")
        
        # Add random operational delay
        import random
        operational_delay = random.randint(0, 20)
        if operational_delay > 10:
            delay_minutes += operational_delay
            reasons.append("Operational congestion")
        
        # Calculate estimated departure time
        estimated_departure = datetime.now() + timedelta(minutes=delay_minutes)
        
        return {
            'flight_id': flight_id,
            'aircraft_id': flight['aircraft_id'],
            'predicted_delay_minutes': delay_minutes,
            'reasons': list(set(reasons)),  # Remove duplicates
            'estimated_departure': estimated_departure.isoformat(),
            'prediction_time': datetime.now().isoformat(),
            'severity': self._get_delay_severity(delay_minutes)
        }
    
    def _get_delay_severity(self, delay_minutes):
        """Categorize delay severity"""
        if delay_minutes == 0:
            return "NONE"
        elif delay_minutes <= 30:
            return "MINOR"
        elif delay_minutes <= 60:
            return "MODERATE"
        elif delay_minutes <= 120:
            return "SIGNIFICANT"
        else:
            return "SEVERE"