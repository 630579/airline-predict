"""
Module for monitoring flight routes and suggesting diversions
"""
import random
from datetime import datetime, timedelta

class RouteMonitor:
    def __init__(self):
        self.airports = {
            'DEL': {'name': 'Delhi', 'alt_runways': ['AMD', 'ATQ']},
            'BOM': {'name': 'Mumbai', 'alt_runways': ['GOI', 'PNQ']},
            'BLR': {'name': 'Bangalore', 'alt_runways': ['MAA', 'HYD']},
            'MAA': {'name': 'Chennai', 'alt_runways': ['BLR', 'HYD']},
            'HYD': {'name': 'Hyderabad', 'alt_runways': ['BLR', 'GOI']},
            'CCU': {'name': 'Kolkata', 'alt_runways': ['GAU', 'PAT']},
            'DXB': {'name': 'Dubai', 'alt_runways': ['AUH', 'DOH']},
            'LHR': {'name': 'London', 'alt_runways': ['LGW', 'MAN']},
            'JFK': {'name': 'New York', 'alt_runways': ['EWR', 'BOS']},
            'SIN': {'name': 'Singapore', 'alt_runways': ['KUL', 'CGK']}
        }
        
        self.weather_risks = {}
    
    def monitor_routes(self, flights_data):
        """Monitor routes for all flights"""
        alerts = []
        
        for flight in flights_data:
            route_alerts = self._monitor_single_route(flight)
            alerts.extend(route_alerts)
        
        return alerts
    
    def _monitor_single_route(self, flight):
        """Monitor route for a single flight"""
        flight_id = flight['flight_id']
        alerts = []
        
        # Get route info
        origin = None
        destination = None
        
        for log in flight['logs']:
            if 'origin' in log and 'destination' in log:
                origin = log['origin']
                destination = log['destination']
                break
        
        if not origin or not destination:
            return alerts
        
        # Check weather enroute
        weather_alerts = self._check_route_weather(flight, origin, destination)
        alerts.extend(weather_alerts)
        
        # Check destination weather
        dest_alerts = self._check_destination_weather(flight, destination)
        alerts.extend(dest_alerts)
        
        # Check for diversion needs
        if weather_alerts or dest_alerts:
            diversion = self._suggest_diversion(origin, destination, flight_id)
            if diversion:
                alerts.append(diversion)
        
        return alerts
    
    def _check_route_weather(self, flight, origin, destination):
        """Check weather along the route"""
        alerts = []
        flight_id = flight['flight_id']
        
        # Get weather logs for this flight
        weather_logs = [log for log in flight['logs'] if log['log_type'] == 'weather_data']
        
        for log in weather_logs:
            metrics = log['metrics']
            
            # Severe turbulence
            if metrics.get('turbulence') == 'severe':
                alert = {
                    'alert_id': f"WX-TURB-{datetime.now().strftime('%H%M%S')}",
                    'flight_id': flight_id,
                    'timestamp': datetime.now().isoformat(),
                    'alert_type': 'SEVERE_TURBULENCE_ENROUTE',
                    'severity': 'HIGH',
                    'location': 'Enroute',
                    'metric': 'turbulence',
                    'value': 'severe',
                    'message': 'Severe turbulence detected along route',
                    'recommendation': 'Consider altitude change or route deviation'
                }
                alerts.append(alert)
            
            # Thunderstorms
            if metrics.get('thunderstorm', False):
                alert = {
                    'alert_id': f"WX-TSTM-{datetime.now().strftime('%H%M%S')}",
                    'flight_id': flight_id,
                    'timestamp': datetime.now().isoformat(),
                    'alert_type': 'THUNDERSTORM_ENROUTE',
                    'severity': 'HIGH',
                    'location': 'Enroute',
                    'metric': 'thunderstorm',
                    'value': True,
                    'message': 'Thunderstorm activity along route',
                    'recommendation': 'Request weather deviation clearance'
                }
                alerts.append(alert)
            
            # High crosswind
            if metrics.get('crosswind', 0) > 40:
                alert = {
                    'alert_id': f"WX-WIND-{datetime.now().strftime('%H%M%S')}",
                    'flight_id': flight_id,
                    'timestamp': datetime.now().isoformat(),
                    'alert_type': 'HIGH_CROSSWIND_ENROUTE',
                    'severity': 'MEDIUM',
                    'location': 'Enroute',
                    'metric': 'crosswind',
                    'value': metrics['crosswind'],
                    'threshold': 40,
                    'message': f'High crosswind ({metrics["crosswind"]:.1f} knots) along route',
                    'recommendation': 'Be prepared for challenging conditions'
                }
                alerts.append(alert)
        
        return alerts
    
    def _check_destination_weather(self, flight, destination):
        """Check destination weather conditions"""
        alerts = []
        flight_id = flight['flight_id']
        
        # Simulate destination weather (in real system, this would be from API)
        dest_weather = self._simulate_destination_weather(destination)
        
        # Low visibility
        if dest_weather['visibility'] < 1500:
            alert = {
                'alert_id': f"WX-VIS-{datetime.now().strftime('%H%M%S')}",
                'flight_id': flight_id,
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'LOW_VISIBILITY_AT_DESTINATION',
                'severity': 'HIGH',
                'location': destination,
                'metric': 'visibility',
                'value': dest_weather['visibility'],
                'threshold': 1500,
                'message': f'Low visibility at {destination}: {dest_weather["visibility"]:.0f} meters',
                'recommendation': 'Consider holding or diversion'
            }
            alerts.append(alert)
        
        # Thunderstorm at destination
        if dest_weather['thunderstorm']:
            alert = {
                'alert_id': f"WX-DEST-TSTM-{datetime.now().strftime('%H%M%S')}",
                'flight_id': flight_id,
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'THUNDERSTORM_AT_DESTINATION',
                'severity': 'HIGH',
                'location': destination,
                'metric': 'thunderstorm',
                'value': True,
                'message': f'Thunderstorm activity at {destination}',
                'recommendation': 'Hold or divert to alternate'
            }
            alerts.append(alert)
        
        # High winds at destination
        if dest_weather['wind_speed'] > 30:
            alert = {
                'alert_id': f"WX-DEST-WIND-{datetime.now().strftime('%H%M%S')}",
                'flight_id': flight_id,
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'HIGH_WINDS_AT_DESTINATION',
                'severity': 'MEDIUM',
                'location': destination,
                'metric': 'wind_speed',
                'value': dest_weather['wind_speed'],
                'threshold': 30,
                'message': f'High winds at {destination}: {dest_weather["wind_speed"]:.1f} knots',
                'recommendation': 'Be prepared for challenging landing'
            }
            alerts.append(alert)
        
        return alerts
    
    def _suggest_diversion(self, origin, destination, flight_id):
        """Suggest diversion airport if needed"""
        if destination not in self.airports:
            return None
        
        # Check if diversion is needed (simulated logic)
        need_diversion = random.random() < 0.2  # 20% chance for demo
        
        if need_diversion and self.airports[destination]['alt_runways']:
            alt_airport = random.choice(self.airports[destination]['alt_runways'])
            
            # Calculate additional time (simplified)
            additional_time = random.randint(30, 120)  # minutes
            
            return {
                'alert_id': f"DIV-{datetime.now().strftime('%H%M%S')}",
                'flight_id': flight_id,
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'DIVERSION_RECOMMENDED',
                'severity': 'HIGH',
                'current_destination': destination,
                'suggested_diversion': alt_airport,
                'additional_flight_time_minutes': additional_time,
                'message': f'Consider diverting to {alt_airport} due to weather at {destination}',
                'recommendation': f'Divert to {alt_airport}, estimated additional time: {additional_time} minutes'
            }
        
        return None
    """
Module for monitoring flight routes and suggesting diversions
"""
import random
from datetime import datetime, timedelta

class RouteMonitor:
    def __init__(self):
        self.airports = {
            'DEL': {'name': 'Delhi', 'alt_runways': ['AMD', 'ATQ']},
            'BOM': {'name': 'Mumbai', 'alt_runways': ['GOI', 'PNQ']},
            'BLR': {'name': 'Bangalore', 'alt_runways': ['MAA', 'HYD']},
            'MAA': {'name': 'Chennai', 'alt_runways': ['BLR', 'HYD']},
            'HYD': {'name': 'Hyderabad', 'alt_runways': ['BLR', 'GOI']},
            'CCU': {'name': 'Kolkata', 'alt_runways': ['GAU', 'PAT']},
            'DXB': {'name': 'Dubai', 'alt_runways': ['AUH', 'DOH']},
            'LHR': {'name': 'London', 'alt_runways': ['LGW', 'MAN']},
            'JFK': {'name': 'New York', 'alt_runways': ['EWR', 'BOS']},
            'SIN': {'name': 'Singapore', 'alt_runways': ['KUL', 'CGK']}
        }
        
        self.weather_risks = {}
    
    def monitor_routes(self, flights_data):
        """Monitor routes for all flights"""
        alerts = []
        
        for flight in flights_data:
            route_alerts = self._monitor_single_route(flight)
            alerts.extend(route_alerts)
        
        return alerts
    
    def _monitor_single_route(self, flight):
        """Monitor route for a single flight"""
        flight_id = flight['flight_id']
        alerts = []
        
        # Get route info
        origin = None
        destination = None
        
        for log in flight['logs']:
            if 'origin' in log and 'destination' in log:
                origin = log['origin']
                destination = log['destination']
                break
        
        if not origin or not destination:
            return alerts
        
        # Check weather enroute
        weather_alerts = self._check_route_weather(flight, origin, destination)
        alerts.extend(weather_alerts)
        
        # Check destination weather
        dest_alerts = self._check_destination_weather(flight, destination)
        alerts.extend(dest_alerts)
        
        # Check for diversion needs
        if weather_alerts or dest_alerts:
            diversion = self._suggest_diversion(origin, destination, flight_id)
            if diversion:
                alerts.append(diversion)
        
        return alerts
    
    def _check_route_weather(self, flight, origin, destination):
        """Check weather along the route"""
        alerts = []
        flight_id = flight['flight_id']
        
        # Get weather logs for this flight
        weather_logs = [log for log in flight['logs'] if log['log_type'] == 'weather_data']
        
        for log in weather_logs:
            metrics = log['metrics']
            
            # Severe turbulence
            if metrics.get('turbulence') == 'severe':
                alert = {
                    'alert_id': f"WX-TURB-{datetime.now().strftime('%H%M%S')}",
                    'flight_id': flight_id,
                    'timestamp': datetime.now().isoformat(),
                    'alert_type': 'SEVERE_TURBULENCE_ENROUTE',
                    'severity': 'HIGH',
                    'location': 'Enroute',
                    'metric': 'turbulence',
                    'value': 'severe',
                    'message': 'Severe turbulence detected along route',
                    'recommendation': 'Consider altitude change or route deviation'
                }
                alerts.append(alert)
            
            # Thunderstorms
            if metrics.get('thunderstorm', False):
                alert = {
                    'alert_id': f"WX-TSTM-{datetime.now().strftime('%H%M%S')}",
                    'flight_id': flight_id,
                    'timestamp': datetime.now().isoformat(),
                    'alert_type': 'THUNDERSTORM_ENROUTE',
                    'severity': 'HIGH',
                    'location': 'Enroute',
                    'metric': 'thunderstorm',
                    'value': True,
                    'message': 'Thunderstorm activity along route',
                    'recommendation': 'Request weather deviation clearance'
                }
                alerts.append(alert)
            
            # High crosswind
            if metrics.get('crosswind', 0) > 40:
                alert = {
                    'alert_id': f"WX-WIND-{datetime.now().strftime('%H%M%S')}",
                    'flight_id': flight_id,
                    'timestamp': datetime.now().isoformat(),
                    'alert_type': 'HIGH_CROSSWIND_ENROUTE',
                    'severity': 'MEDIUM',
                    'location': 'Enroute',
                    'metric': 'crosswind',
                    'value': metrics['crosswind'],
                    'threshold': 40,
                    'message': f'High crosswind ({metrics["crosswind"]:.1f} knots) along route',
                    'recommendation': 'Be prepared for challenging conditions'
                }
                alerts.append(alert)
        
        return alerts
    
    def _check_destination_weather(self, flight, destination):
        """Check destination weather conditions"""
        alerts = []
        flight_id = flight['flight_id']
        
        # Simulate destination weather (in real system, this would be from API)
        dest_weather = self._simulate_destination_weather(destination)
        
        # Low visibility
        if dest_weather['visibility'] < 1500:
            alert = {
                'alert_id': f"WX-VIS-{datetime.now().strftime('%H%M%S')}",
                'flight_id': flight_id,
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'LOW_VISIBILITY_AT_DESTINATION',
                'severity': 'HIGH',
                'location': destination,
                'metric': 'visibility',
                'value': dest_weather['visibility'],
                'threshold': 1500,
                'message': f'Low visibility at {destination}: {dest_weather["visibility"]:.0f} meters',
                'recommendation': 'Consider holding or diversion'
            }
            alerts.append(alert)
        
        # Thunderstorm at destination
        if dest_weather['thunderstorm']:
            alert = {
                'alert_id': f"WX-DEST-TSTM-{datetime.now().strftime('%H%M%S')}",
                'flight_id': flight_id,
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'THUNDERSTORM_AT_DESTINATION',
                'severity': 'HIGH',
                'location': destination,
                'metric': 'thunderstorm',
                'value': True,
                'message': f'Thunderstorm activity at {destination}',
                'recommendation': 'Hold or divert to alternate'
            }
            alerts.append(alert)
        
        # High winds at destination
        if dest_weather['wind_speed'] > 30:
            alert = {
                'alert_id': f"WX-DEST-WIND-{datetime.now().strftime('%H%M%S')}",
                'flight_id': flight_id,
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'HIGH_WINDS_AT_DESTINATION',
                'severity': 'MEDIUM',
                'location': destination,
                'metric': 'wind_speed',
                'value': dest_weather['wind_speed'],
                'threshold': 30,
                'message': f'High winds at {destination}: {dest_weather["wind_speed"]:.1f} knots',
                'recommendation': 'Be prepared for challenging landing'
            }
            alerts.append(alert)
        
        return alerts
    
    def _suggest_diversion(self, origin, destination, flight_id):
        """Suggest diversion airport if needed"""
        if destination not in self.airports:
            return None
        
        # Check if diversion is needed (simulated logic)
        need_diversion = random.random() < 0.2  # 20% chance for demo
        
        if need_diversion and self.airports[destination]['alt_runways']:
            alt_airport = random.choice(self.airports[destination]['alt_runways'])
            
            # Calculate additional time (simplified)
            additional_time = random.randint(30, 120)  # minutes
            
            return {
                'alert_id': f"DIV-{datetime.now().strftime('%H%M%S')}",
                'flight_id': flight_id,
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'DIVERSION_RECOMMENDED',
                'severity': 'HIGH',
                'current_destination': destination,
                'suggested_diversion': alt_airport,
                'additional_flight_time_minutes': additional_time,
                'message': f'Consider diverting to {alt_airport} due to weather at {destination}',
                'recommendation': f'Divert to {alt_airport}, estimated additional time: {additional_time} minutes'
            }
        
        return None
    
    def _simulate_destination_weather(self, airport_code):
        """Simulate destination weather conditions"""
        # In real system, this would fetch from weather API
        return {
            'visibility': random.uniform(800, 5000),
            'wind_speed': random.uniform(10, 50),
            'thunderstorm': random.random() < 0.3,  # 30% chance
            'ceiling': random.uniform(1000, 10000),
            'temperature': random.uniform(15, 35)
        }
    def _simulate_destination_weather(self, airport_code):
        """Simulate destination weather conditions"""
        # In real system, this would fetch from weather API
        return {
            'visibility': random.uniform(800, 5000),
            'wind_speed': random.uniform(10, 50),
            'thunderstorm': random.random() < 0.3,  # 30% chance
            'ceiling': random.uniform(1000, 10000),
            'temperature': random.uniform(15, 35)
        }