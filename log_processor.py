"""
Module for processing airline operations logs
"""
import json
from datetime import datetime
import statistics

class LogProcessor:
    def __init__(self):
        self.processed_logs = []
        
    def process_logs(self, log_entries):
        """Process raw log entries"""
        processed_data = []
        
        for log in log_entries:
            processed_log = self._process_single_log(log)
            if processed_log:
                processed_data.append(processed_log)
        
        # Group by flight
        flights_by_id = {}
        for log in processed_data:
            flight_id = log['flight_id']
            if flight_id not in flights_by_id:
                flights_by_id[flight_id] = {
                    'flight_id': flight_id,
                    'aircraft_id': log['aircraft_id'],
                    'logs': [],
                    'metrics_summary': {}
                }
            flights_by_id[flight_id]['logs'].append(log)
        
        # Calculate metrics summary for each flight
        for flight_id, flight_data in flights_by_id.items():
            flight_data['metrics_summary'] = self._calculate_metrics_summary(flight_data['logs'])
        
        self.processed_logs = list(flights_by_id.values())
        return self.processed_logs
    
    def _process_single_log(self, log_entry):
        """Process a single log entry"""
        try:
            processed = {
                'log_id': log_entry.get('log_id', ''),
                'flight_id': log_entry.get('flight_id', ''),
                'aircraft_id': log_entry.get('aircraft_id', ''),
                'timestamp': datetime.fromisoformat(log_entry['timestamp'].replace('Z', '')),
                'log_type': log_entry.get('log_type', ''),
                'metrics': log_entry.get('metrics', {}),
                'status': log_entry.get('status', 'UNKNOWN'),
                'origin': log_entry.get('origin', ''),
                'destination': log_entry.get('destination', '')
            }
            return processed
        except Exception as e:
            print(f"Error processing log {log_entry.get('log_id', 'unknown')}: {e}")
            return None
    
    def _calculate_metrics_summary(self, logs):
        """Calculate summary statistics for flight logs"""
        summary = {
            'engine_metrics': {},
            'weather_metrics': {},
            'passenger_metrics': {},
            'alert_count': 0
        }
        
        engine_thrust_values = []
        vibration_values = []
        crosswind_values = []
        visibility_values = []
        passenger_counts = []
        
        for log in logs:
            if log['status'] != 'NORMAL':
                summary['alert_count'] += 1
            
            metrics = log['metrics']
            
            if log['log_type'] == 'engine_performance':
                engine_thrust_values.append(metrics.get('engine_thrust', 0))
                vibration_values.append(metrics.get('engine_vibration', 0))
                
            elif log['log_type'] == 'weather_data':
                crosswind_values.append(metrics.get('crosswind', 0))
                visibility_values.append(metrics.get('visibility', 0))
                
            elif log['log_type'] == 'passenger_load':
                passenger_counts.append(metrics.get('passenger_count', 0))
        
        # Calculate statistics
        if engine_thrust_values:
            summary['engine_metrics'] = {
                'avg_thrust': statistics.mean(engine_thrust_values),
                'max_vibration': max(vibration_values) if vibration_values else 0
            }
        
        if crosswind_values:
            summary['weather_metrics'] = {
                'avg_crosswind': statistics.mean(crosswind_values),
                'min_visibility': min(visibility_values) if visibility_values else 0
            }
        
        if passenger_counts:
            summary['passenger_metrics'] = {
                'avg_passengers': statistics.mean(passenger_counts),
                'total_passengers': sum(passenger_counts)
            }
        
        return summary