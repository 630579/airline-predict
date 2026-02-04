"""
Module for monitoring aircraft health
"""
import json
import logging
from datetime import datetime

class HealthMonitor:
    def __init__(self):
        # Setup logging
        self.health_logger = self._setup_logger('health_alerts', 'logs/aircraft_health_alerts.log')
        self.critical_logger = self._setup_logger('critical_alerts', 'logs/critical_flight_alerts.log')
        
        self.thresholds = {
            'engine_vibration': 3.0,  # mm/s
            'altitude_fluctuation': 1000,  # feet per minute
            'fuel_burn_deviation': 25,  # percentage
            'cabin_temperature': 30,  # degrees Celsius
            'cabin_pressure_drop': 0.1,  # PSI per minute
        }
    
    def _setup_logger(self, name, log_file):
        """Setup logger for alerts"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        
        return logger
    
    def monitor_health(self, flights_data):
        """Monitor health for all flights"""
        alerts = []
        
        for flight in flights_data:
            flight_alerts = self._monitor_single_flight(flight)
            alerts.extend(flight_alerts)
        
        return alerts
    
    def _monitor_single_flight(self, flight):
        """Monitor health for a single flight"""
        flight_id = flight['flight_id']
        aircraft_id = flight['aircraft_id']
        alerts = []
        
        # Check all logs for health issues
        for log in flight['logs']:
            if log['log_type'] == 'engine_performance':
                engine_alerts = self._check_engine_health(log, flight_id, aircraft_id)
                alerts.extend(engine_alerts)
            
            elif log['log_type'] == 'cabin_pressure':
                cabin_alerts = self._check_cabin_health(log, flight_id, aircraft_id)
                alerts.extend(cabin_alerts)
        
        return alerts
    
    def _check_engine_health(self, log, flight_id, aircraft_id):
        """Check engine health metrics"""
        alerts = []
        metrics = log['metrics']
        
        # Engine vibration
        vibration = metrics.get('engine_vibration', 0)
        if vibration > self.thresholds['engine_vibration']:
            alert = {
                'alert_id': f"ENG-VIB-{datetime.now().strftime('%H%M%S')}",
                'flight_id': flight_id,
                'aircraft_id': aircraft_id,
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'ENGINE_VIBRATION_HIGH',
                'metric': 'engine_vibration',
                'value': vibration,
                'threshold': self.thresholds['engine_vibration'],
                'severity': 'HIGH' if vibration > 5.0 else 'MEDIUM',
                'message': f'Engine vibration {vibration:.2f} mm/s exceeds threshold {self.thresholds["engine_vibration"]} mm/s'
            }
            alerts.append(alert)
            self._log_alert(alert)
        
        # Fuel burn
        fuel_flow = metrics.get('fuel_flow', 0)
        if fuel_flow > 4500:  # Abnormal high fuel burn
            alert = {
                'alert_id': f"FUEL-HIGH-{datetime.now().strftime('%H%M%S')}",
                'flight_id': flight_id,
                'aircraft_id': aircraft_id,
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'HIGH_FUEL_BURN',
                'metric': 'fuel_flow',
                'value': fuel_flow,
                'threshold': 4500,
                'severity': 'MEDIUM',
                'message': f'High fuel burn detected: {fuel_flow:.0f} kg/hr'
            }
            alerts.append(alert)
            self._log_alert(alert)
        
        # Oil temperature
        oil_temp = metrics.get('oil_temperature', 0)
        if oil_temp > 110:  # Degrees Celsius
            alert = {
                'alert_id': f"OIL-TEMP-{datetime.now().strftime('%H%M%S')}",
                'flight_id': flight_id,
                'aircraft_id': aircraft_id,
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'HIGH_OIL_TEMPERATURE',
                'metric': 'oil_temperature',
                'value': oil_temp,
                'threshold': 110,
                'severity': 'HIGH',
                'message': f'High oil temperature: {oil_temp:.1f}°C'
            }
            alerts.append(alert)
            self._log_alert(alert, critical=True)
        
        return alerts
    
    def _check_cabin_health(self, log, flight_id, aircraft_id):
        """Check cabin health metrics"""
        alerts = []
        metrics = log['metrics']
        
        # Cabin pressure
        pressure_drop = metrics.get('pressure_drop_rate', 0)
        if pressure_drop > self.thresholds['cabin_pressure_drop']:
            alert = {
                'alert_id': f"CAB-PRES-{datetime.now().strftime('%H%M%S')}",
                'flight_id': flight_id,
                'aircraft_id': aircraft_id,
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'RAPID_CABIN_DEPRESSURIZATION',
                'metric': 'pressure_drop_rate',
                'value': pressure_drop,
                'threshold': self.thresholds['cabin_pressure_drop'],
                'severity': 'CRITICAL',
                'message': f'Rapid cabin depressurization: {pressure_drop:.3f} PSI/min'
            }
            alerts.append(alert)
            self._log_alert(alert, critical=True)
        
        # Cabin temperature
        cabin_temp = metrics.get('cabin_temperature', 0)
        if cabin_temp > self.thresholds['cabin_temperature']:
            alert = {
                'alert_id': f"CAB-TEMP-{datetime.now().strftime('%H%M%S')}",
                'flight_id': flight_id,
                'aircraft_id': aircraft_id,
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'HIGH_CABIN_TEMPERATURE',
                'metric': 'cabin_temperature',
                'value': cabin_temp,
                'threshold': self.thresholds['cabin_temperature'],
                'severity': 'MEDIUM',
                'message': f'High cabin temperature: {cabin_temp:.1f}°C'
            }
            alerts.append(alert)
            self._log_alert(alert)
        
        return alerts
    
    def _log_alert(self, alert, critical=False):
        """Log alert to appropriate log file"""
        log_message = json.dumps(alert)
        
        if critical:
            self.critical_logger.critical(log_message)
            print(f"🚨 CRITICAL ALERT: {alert['message']}")
        else:
            self.health_logger.warning(log_message)
            print(f"⚠️  WARNING: {alert['message']}")