# main.py
"""
AI-Driven Airline Operations & Predictive Flight Management Automation System
Main Application Entry Point
"""
import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
from queue import Queue

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.log_processor import LogProcessor
from modules.delay_predictor import DelayPredictor
from modules.crew_optimizer import CrewOptimizer
from modules.load_predictor import LoadPredictor
from modules.health_monitor import HealthMonitor
from modules.route_monitor import RouteMonitor
from modules.dashboard import Dashboard
from modules.reporter import ReportGenerator as Reporter

class AirlineOperationsSystem:
    """Main class for Airline Operations Automation System"""
    
    def __init__(self, config_path: str = None):
        """Initialize the airline operations system"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'airline_config.json')
        print("=" * 80)
        print(" " * 20 + "AIRLINE OPERATIONS AUTOMATION SYSTEM")
        print("=" * 80)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize directories
        self._setup_directories()
        
        # Initialize components
        self.components = self._initialize_components()
        
        # Data storage
        self.flights_data = {}
        self.alerts_queue = Queue()
        self.is_running = False
        
        print(f"\n✓ System initialized for {self.config['airline_name']}")
        print(f"✓ Hub Airport: {self.config['hub_airport']}")
        print(f"✓ Fleet Size: {len(self.config['aircraft_fleet'])} aircraft types")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        if not os.path.exists(config_path):
            # Create default configuration
            default_config = {
                "airline_name": "Global Airways",
                "hub_airport": "DEL",
                "thresholds": {
                    "weather": {"crosswind_max_knots": 40},
                    "maintenance": {"engine_vibration_threshold": 7.5}
                }
            }
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"⚠ Created default configuration at {config_path}")
            return default_config
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _setup_directories(self):
        """Create necessary directories"""
        directories = [
            'logs',
            'data',
            'output/reports',
            'output/dashboards',
            'output/alerts',
            'output/backups'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        # Create empty log files if they don't exist
        log_files = [
            'logs/aircraft_health_alerts.log',
            'logs/critical_flight_alerts.log',
            'logs/system.log'
        ]
        
        for log_file in log_files:
            if not os.path.exists(log_file):
                with open(log_file, 'w') as f:
                    f.write(f"Log file created: {datetime.now().isoformat()}\n")
    
    def _initialize_components(self):
        """Initialize all system components"""
        print("\n" + "-" * 80)
        print("INITIALIZING SYSTEM COMPONENTS")
        print("-" * 80)
        
        components = {}
        
        # Initialize each component
        component_configs = [
            ("Log Processor", LogProcessor, self.config),
            ("Delay Predictor", DelayPredictor, self.config),
            ("Crew Optimizer", CrewOptimizer, self.config),
            ("Load Predictor", LoadPredictor, self.config),
            ("Health Monitor", HealthMonitor, self.config),
            ("Route Monitor", RouteMonitor, self.config),

            ("Dashboard", Dashboard, self.config),
            ("Reporter", Reporter, self.config)
        ]
        
        for name, component_class, config in component_configs:
            try:
                components[name.lower().replace(' ', '_')] = component_class(config)
                print(f"  ✓ {name}")
            except Exception as e:
                print(f"  ✗ {name}: {str(e)}")
                components[name.lower().replace(' ', '_')] = None
        
        return components
    
    def load_sample_data(self):
        """Load sample flight data for demonstration"""
        print("\n" + "-" * 80)
        print("LOADING SAMPLE DATA")
        print("-" * 80)
        
        sample_data = self._generate_sample_data()
        
        # Process through log processor
        if self.components['log_processor']:
            self.components['log_processor'].ingest_logs(sample_data)
            self.flights_data = self.components['log_processor'].get_all_logs()
            print(f"✓ Loaded {len(self.flights_data.get('flights', []))} sample flights")
            print(f"✓ Generated {len(self.flights_data.get('passengers', []))} passenger records")
            print(f"✓ Created {len(self.flights_data.get('crew', []))} crew assignments")
        else:
            print("✗ Log processor not available")
    
    def _generate_sample_data(self) -> Dict:
        """Generate comprehensive sample data"""
        import random
        from datetime import datetime, timedelta
        
        base_time = datetime.now()
        aircraft_types = list(self.config['aircraft_fleet'].keys())
        routes = self.config['routes']['domestic'] + self.config['routes']['international']
        
        data = {
            "flights": [],
            "passengers": [],
            "crew": [],
            "weather": [],
            "maintenance": []
        }
        
        # Generate 50 sample flights
        for i in range(50):
            flight_id = f"{self.config['airline_code']}{1000 + i}"
            aircraft_type = random.choice(aircraft_types)
            route = random.choice(routes)
            departure, arrival = route.split('-')
            
            # Flight data
            flight = {
                "flight_id": flight_id,
                "aircraft_id": f"VT-{random.choice(['AXB', 'BXC', 'CXD', 'EXF', 'GXH'])}",
                "aircraft_type": aircraft_type,
                "route": route,
                "departure_airport": departure,
                "arrival_airport": arrival,
                "scheduled_departure": (base_time + timedelta(hours=i)).isoformat(),
                "scheduled_arrival": (base_time + timedelta(hours=i + random.randint(2, 8))).isoformat(),
                "actual_departure": None,
                "actual_arrival": None,
                "status": random.choice(["SCHEDULED", "BOARDING", "DEPARTED", "IN_AIR", "LANDED"]),
                "gate": f"Gate {random.randint(1, 50)}",
                "runway_queue_minutes": random.randint(0, 45),
                "boarding_time_minutes": random.randint(20, 60)
            }
            data["flights"].append(flight)
            
            # Passenger data
            capacity = self.config['aircraft_fleet'][aircraft_type]["capacity"]
            passenger_count = random.randint(int(capacity * 0.6), int(capacity * 1.1))
            data["passengers"].append({
                "flight_id": flight_id,
                "passenger_count": passenger_count,
                "capacity": capacity,
                "load_factor": (passenger_count / capacity) * 100,
                "business_class": random.randint(10, min(40, passenger_count)),
                "economy_class": passenger_count - random.randint(10, min(40, passenger_count)),
                "check_in_complete": random.random() > 0.2,
                "special_assistance": random.randint(0, 5)
            })
            
            # Crew data
            crew_required = self.config['aircraft_fleet'][aircraft_type]["crew_required"]
            for j in range(crew_required):
                role = "PILOT" if j < 2 else "CABIN_CREW"
                data["crew"].append({
                    "crew_id": f"C{1000 + i * 10 + j}",
                    "name": f"Crew Member {i}-{j}",
                    "role": role,
                    "flight_id": flight_id,
                    "duty_start": (base_time + timedelta(hours=i - 1)).isoformat(),
                    "duty_end": (base_time + timedelta(hours=i + random.randint(3, 10))).isoformat(),
                    "total_duty_hours": random.randint(4, 12),
                    "rest_hours": random.randint(8, 24),
                    "base_airport": random.choice(self.config["base_airports"]),
                    "status": random.choice(["ACTIVE", "RESTING", "STANDBY"])
                })
            
            # Weather data
            data["weather"].append({
                "flight_id": flight_id,
                "airport": departure,
                "timestamp": (base_time + timedelta(hours=i)).isoformat(),
                "temperature_c": random.randint(15, 35),
                "wind_speed_knots": random.randint(5, 50),
                "crosswind_knots": random.randint(5, 45),
                "visibility_meters": random.randint(500, 5000),
                "turbulence_level": random.randint(1, 10),
                "thunderstorm": random.random() < 0.1,
                "precipitation_mm": random.randint(0, 50),
                "cloud_cover_percent": random.randint(0, 100)
            })
            
            # Maintenance data
            data["maintenance"].append({
                "flight_id": flight_id,
                "aircraft_id": flight["aircraft_id"],
                "timestamp": (base_time + timedelta(hours=i)).isoformat(),
                "engine_thrust_percent": random.uniform(75, 95),
                "engine_vibration": random.uniform(2.0, 9.0),
                "cabin_pressure": random.uniform(800, 1013),
                "cabin_temperature": random.uniform(18, 32),
                "fuel_flow_rate": random.randint(1000, 3000),
                "oil_temperature": random.uniform(85, 115),
                "altitude_ft": random.randint(10000, 40000),
                "airspeed_knots": random.randint(400, 550),
                "turbulence_experienced": random.randint(0, 8)
            })
        
        return data
    
    def run_real_time_monitoring(self):
        """Run real-time monitoring of flights"""
        print("\n" + "-" * 80)
        print("STARTING REAL-TIME MONITORING")
        print("-" * 80)
        
        self.is_running = True
        
        # Start monitoring threads
        threads = []
        
        # Health monitoring thread
        health_thread = threading.Thread(target=self._monitor_health, daemon=True)
        threads.append(health_thread)
        
        # Delay prediction thread
        delay_thread = threading.Thread(target=self._predict_delays, daemon=True)
        threads.append(delay_thread)
        
        # Crew optimization thread
        crew_thread = threading.Thread(target=self._optimize_crew, daemon=True)
        threads.append(crew_thread)
        
        # Dashboard update thread
        dashboard_thread = threading.Thread(target=self._update_dashboard, daemon=True)
        threads.append(dashboard_thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        print("✓ Real-time monitoring started")
        print("✓ Press Ctrl+C to stop\n")
        
        # Keep main thread alive
        try:
            while self.is_running:
                time.sleep(1)
                
                # Process alerts
                self._process_alerts()
                
        except KeyboardInterrupt:
            print("\n\nStopping monitoring...")
            self.is_running = False
    
    def _monitor_health(self):
        """Monitor aircraft health in real-time"""
        while self.is_running:
            try:
                if self.components['health_monitor'] and self.flights_data:
                    alerts = self.components['health_monitor'].monitor(self.flights_data)
                    for alert in alerts:
                        self.alerts_queue.put(alert)
            except Exception as e:
                print(f"Health monitoring error: {str(e)}")
            
            time.sleep(30)  # Check every 30 seconds
    
    def _predict_delays(self):
        """Predict flight delays in real-time"""
        while self.is_running:
            try:
                if self.components['delay_predictor'] and self.flights_data:
                    predictions = self.components['delay_predictor'].predict(self.flights_data)
                    
                    # Check for significant delays
                    for prediction in predictions:
                        if prediction.get('delay_minutes', 0) > 30:
                            alert = {
                                "type": "DELAY_PREDICTION",
                                "severity": "WARNING",
                                "flight_id": prediction['flight_id'],
                                "message": f"Predicted delay: {prediction['delay_minutes']} minutes",
                                "details": prediction['reasons'],
                                "timestamp": datetime.now().isoformat()
                            }
                            self.alerts_queue.put(alert)
            except Exception as e:
                print(f"Delay prediction error: {str(e)}")
            
            time.sleep(60)  # Predict every minute
    
    def _optimize_crew(self):
        """Optimize crew scheduling in real-time"""
        while self.is_running:
            try:
                if self.components['crew_optimizer'] and self.flights_data:
                    optimizations = self.components['crew_optimizer'].optimize(self.flights_data)
                    
                    # Check for crew shortages
                    for issue in optimizations.get('issues', []):
                        if 'shortage' in issue.lower() or 'unavailable' in issue.lower():
                            alert = {
                                "type": "CREW_SHORTAGE",
                                "severity": "CRITICAL",
                                "message": issue,
                                "timestamp": datetime.now().isoformat()
                            }
                            self.alerts_queue.put(alert)
            except Exception as e:
                print(f"Crew optimization error: {str(e)}")
            
            time.sleep(300)  # Optimize every 5 minutes
    
    def _update_dashboard(self):
        """Update operations dashboard in real-time"""
        while self.is_running:
            try:
                if self.components['dashboard'] and self.flights_data:
                    # Get current system status
                    status = {
                        'flights': self.flights_data.get('flights', []),
                        'alerts': list(self.alerts_queue.queue)[-10:],  # Last 10 alerts
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Update dashboard
                    self.components['dashboard'].update(status)
            except Exception as e:
                print(f"Dashboard update error: {str(e)}")
            
            time.sleep(60)  # Update every minute
    
    def _process_alerts(self):
        """Process queued alerts"""
        while not self.alerts_queue.empty():
            alert = self.alerts_queue.get()
            
            # Send to alert system
            if self.components['alert_system']:
                self.components['alert_system'].send_alert(alert)
            
            # Log critical alerts
            if alert.get('severity') in ['CRITICAL', 'EMERGENCY']:
                with open('logs/critical_flight_alerts.log', 'a') as f:
                    f.write(f"{datetime.now().isoformat()} - {alert}\n")
    
    def generate_daily_report(self):
        """Generate daily operations report"""
        print("\n" + "-" * 80)
        print("GENERATING DAILY OPERATIONS REPORT")
        print("-" * 80)
        
        if self.components['reporter']:
            report_data = {
                'flights': self.flights_data.get('flights', []),
                'passengers': self.flights_data.get('passengers', []),
                'crew': self.flights_data.get('crew', []),
                'weather': self.flights_data.get('weather', []),
                'maintenance': self.flights_data.get('maintenance', []),
                'alerts': list(self.alerts_queue.queue),
                'timestamp': datetime.now().isoformat()
            }
            
            report_path = self.components['reporter'].generate_daily_report(report_data)
            print(f"✓ Daily report generated: {report_path}")
            
            # Optional: Generate PDF
            try:
                pdf_path = self.components['reporter'].generate_pdf_report(report_data)
                print(f"✓ PDF report generated: {pdf_path}")
            except:
                print("✗ PDF generation not available")
    
    def show_dashboard(self):
        """Display real-time operations dashboard"""
        if self.components['dashboard']:
            self.components['dashboard'].display_full()
    
    def run_single_analysis(self):
        """Run a single comprehensive analysis"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE ANALYSIS MODE")
        print("=" * 80)
        
        # 1. Load data
        self.load_sample_data()
        
        # 2. Health Monitoring
        print("\n1. AIRCRAFT HEALTH MONITORING")
        print("-" * 40)
        if self.components['health_monitor']:
            health_results = self.components['health_monitor'].monitor(self.flights_data)
            print(f"✓ Health checks completed: {len(health_results)} alerts generated")
        
        # 3. Delay Prediction
        print("\n2. FLIGHT DELAY PREDICTION")
        print("-" * 40)
        if self.components['delay_predictor']:
            delays = self.components['delay_predictor'].predict(self.flights_data)
            delayed_flights = [d for d in delays if d.get('delay_minutes', 0) > 0]
            print(f"✓ Delay prediction completed: {len(delayed_flights)} flights with delays")
        
        # 4. Crew Optimization
        print("\n3. CREW SCHEDULING OPTIMIZATION")
        print("-" * 40)
        if self.components['crew_optimizer']:
            crew_results = self.components['crew_optimizer'].optimize(self.flights_data)
            print(f"✓ Crew optimization completed: {len(crew_results.get('issues', []))} issues found")
        
        # 5. Load Prediction
        print("\n4. PASSENGER LOAD PREDICTION")
        print("-" * 40)
        if self.components['load_predictor']:
            load_predictions = self.components['load_predictor'].predict(self.flights_data)
            print(f"✓ Load prediction completed: {len(load_predictions)} predictions generated")
        
        # 6. Route Monitoring
        print("\n5. FLIGHT ROUTE MONITORING")
        print("-" * 40)
        if self.components['route_monitor']:
            route_results = self.components['route_monitor'].monitor(self.flights_data)
            diversions = route_results.get('diversion_suggestions', [])
            print(f"✓ Route monitoring completed: {len(diversions)} diversion suggestions")
        
        # 7. Generate Report
        self.generate_daily_report()
        
        # 8. Show Dashboard
        self.show_dashboard()
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
    
    def interactive_menu(self):
        """Display interactive menu"""
        while True:
            print("\n" + "=" * 80)
            print("AIRLINE OPERATIONS SYSTEM - MAIN MENU")
            print("=" * 80)
            print("1. Run Complete Analysis")
            print("2. Start Real-time Monitoring")
            print("3. Search Flight/Aircraft")
            print("4. Generate Custom Report")
            print("5. View Current Dashboard")
            print("6. System Configuration")
            print("7. Exit")
            print("-" * 80)
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                self.run_single_analysis()
            elif choice == '2':
                self.run_real_time_monitoring()
            elif choice == '3':
                self._search_menu()
            elif choice == '4':
                self.generate_daily_report()
            elif choice == '5':
                self.show_dashboard()
            elif choice == '6':
                self._configuration_menu()
            elif choice == '7':
                print("\nExiting Airline Operations System. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _search_menu(self):
        """Search menu for flights and aircraft"""
        print("\n" + "-" * 80)
        print("SEARCH MENU")
        print("-" * 80)
        print("1. Search Flight by ID")
        print("2. Search Aircraft by ID")
        print("3. Search Crew by ID")
        print("4. Search by Route")
        print("5. Return to Main Menu")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            flight_id = input("Enter Flight ID (e.g., GA1001): ").strip().upper()
            self._search_flight(flight_id)
        elif choice == '2':
            aircraft_id = input("Enter Aircraft ID (e.g., VT-AXB): ").strip().upper()
            self._search_aircraft(aircraft_id)
        elif choice == '3':
            crew_id = input("Enter Crew ID (e.g., C1001): ").strip().upper()
            self._search_crew(crew_id)
        elif choice == '4':
            route = input("Enter Route (e.g., DEL-BOM): ").strip().upper()
            self._search_route(route)
        elif choice == '5':
            return
        else:
            print("Invalid choice")
    
    def _search_flight(self, flight_id: str):
        """Search for a specific flight"""
        flights = self.flights_data.get('flights', [])
        found_flights = [f for f in flights if f.get('flight_id') == flight_id]
        
        if found_flights:
            flight = found_flights[0]
            print(f"\nFlight: {flight_id}")
            print(f"  Route: {flight.get('route')}")
            print(f"  Status: {flight.get('status')}")
            print(f"  Aircraft: {flight.get('aircraft_id')}")
            print(f"  Scheduled Departure: {flight.get('scheduled_departure')}")
            
            # Get delay prediction
            if self.components['delay_predictor']:
                prediction = self.components['delay_predictor'].predict_for_flight(flight_id, self.flights_data)
                if prediction:
                    print(f"  Predicted Delay: {prediction.get('delay_minutes', 0)} minutes")
        else:
            print(f"Flight {flight_id} not found")
    
    def _search_aircraft(self, aircraft_id: str):
        """Search for a specific aircraft"""
        flights = self.flights_data.get('flights', [])
        aircraft_flights = [f for f in flights if f.get('aircraft_id') == aircraft_id]
        
        if aircraft_flights:
            print(f"\nAircraft: {aircraft_id}")
            print(f"  Total Flights: {len(aircraft_flights)}")
            print(f"  Current Status: {aircraft_flights[0].get('status')}")
            print(f"  Type: {aircraft_flights[0].get('aircraft_type')}")
            
            # Get maintenance data
            maintenance = self.flights_data.get('maintenance', [])
            aircraft_maintenance = [m for m in maintenance if m.get('aircraft_id') == aircraft_id]
            
            if aircraft_maintenance:
                latest = max(aircraft_maintenance, key=lambda x: x.get('timestamp', ''))
                print(f"  Latest Engine Vibration: {latest.get('engine_vibration', 0):.2f}")
                print(f"  Latest Cabin Pressure: {latest.get('cabin_pressure', 0):.0f} hPa")
        else:
            print(f"Aircraft {aircraft_id} not found")
    
    def _search_crew(self, crew_id: str):
        """Search for specific crew member"""
        crew = self.flights_data.get('crew', [])
        found_crew = [c for c in crew if c.get('crew_id') == crew_id]
        
        if found_crew:
            member = found_crew[0]
            print(f"\nCrew Member: {crew_id}")
            print(f"  Name: {member.get('name')}")
            print(f"  Role: {member.get('role')}")
            print(f"  Status: {member.get('status')}")
            print(f"  Current Flight: {member.get('flight_id', 'None')}")
            print(f"  Duty Hours: {member.get('total_duty_hours', 0)}")
            print(f"  Rest Hours: {member.get('rest_hours', 0)}")
        else:
            print(f"Crew member {crew_id} not found")
    
    def _search_route(self, route: str):
        """Search flights by route"""
        flights = self.flights_data.get('flights', [])
        route_flights = [f for f in flights if f.get('route') == route]
        
        if route_flights:
            print(f"\nRoute: {route}")
            print(f"  Total Flights: {len(route_flights)}")
            
            # Categorize by status
            status_counts = {}
            for flight in route_flights:
                status = flight.get('status')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print("  Status Breakdown:")
            for status, count in status_counts.items():
                print(f"    {status}: {count}")
        else:
            print(f"No flights found for route {route}")
    
    def _configuration_menu(self):
        """System configuration menu"""
        print("\n" + "-" * 80)
        print("SYSTEM CONFIGURATION")
        print("-" * 80)
        print("1. View Current Configuration")
        print("2. Update Thresholds")
        print("3. Backup System Data")
        print("4. Restore from Backup")
        print("5. System Status")
        print("6. Return to Main Menu")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            print("\nCurrent Configuration:")
            print(json.dumps(self.config, indent=2))
        elif choice == '2':
            self._update_thresholds()
        elif choice == '3':
            self._backup_data()
        elif choice == '4':
            self._restore_backup()
        elif choice == '5':
            self._system_status()
        elif choice == '6':
            return
        else:
            print("Invalid choice")
    
    def _update_thresholds(self):
        """Update system thresholds"""
        print("\nUpdate Thresholds:")
        print("1. Weather Thresholds")
        print("2. Maintenance Thresholds")
        print("3. Operations Thresholds")
        print("4. Crew Thresholds")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            self._update_weather_thresholds()
        elif choice == '2':
            self._update_maintenance_thresholds()
        elif choice == '3':
            self._update_operations_thresholds()
        elif choice == '4':
            self._update_crew_thresholds()
        else:
            print("Invalid choice")
    
    def _update_weather_thresholds(self):
        """Update weather thresholds"""
        print("\nWeather Thresholds:")
        current = self.config['thresholds']['weather']
        
        crosswind = input(f"Crosswind Max (knots) [{current['crosswind_max_knots']}]: ").strip()
        if crosswind:
            self.config['thresholds']['weather']['crosswind_max_knots'] = int(crosswind)
        
        visibility = input(f"Visibility Min (meters) [{current['visibility_min_meters']}]: ").strip()
        if visibility:
            self.config['thresholds']['weather']['visibility_min_meters'] = int(visibility)
        
        # Save configuration
        with open('airline_config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print("✓ Weather thresholds updated")
    
    def _update_maintenance_thresholds(self):
        """Update maintenance thresholds"""
        print("\nMaintenance Thresholds:")
        current = self.config['thresholds']['maintenance']
        
        vibration = input(f"Engine Vibration Threshold [{current['engine_vibration_threshold']}]: ").strip()
        if vibration:
            self.config['thresholds']['maintenance']['engine_vibration_threshold'] = float(vibration)
        
        cabin_temp = input(f"Cabin Temp Max (C) [{current['cabin_temp_max_celsius']}]: ").strip()
        if cabin_temp:
            self.config['thresholds']['maintenance']['cabin_temp_max_celsius'] = int(cabin_temp)
        
        # Save configuration
        with open('airline_config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print("✓ Maintenance thresholds updated")
    
    def _update_operations_thresholds(self):
        """Update operations thresholds"""
        print("\nOperations Thresholds:")
        current = self.config['thresholds']['operations']
        
        runway = input(f"Runway Queue Max (minutes) [{current['runway_queue_max_minutes']}]: ").strip()
        if runway:
            self.config['thresholds']['operations']['runway_queue_max_minutes'] = int(runway)
        
        boarding = input(f"Boarding Max (minutes) [{current['boarding_max_minutes']}]: ").strip()
        if boarding:
            self.config['thresholds']['operations']['boarding_max_minutes'] = int(boarding)
        
        # Save configuration
        with open('airline_config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print("✓ Operations thresholds updated")
    
    def _update_crew_thresholds(self):
        """Update crew thresholds"""
        print("\nCrew Thresholds:")
        current = self.config['thresholds']['crew']
        
        duty = input(f"Max Duty Hours [{current['max_duty_hours']}]: ").strip()
        if duty:
            self.config['thresholds']['crew']['max_duty_hours'] = int(duty)
        
        rest = input(f"Min Rest Hours [{current['min_rest_hours']}]: ").strip()
        if rest:
            self.config['thresholds']['crew']['min_rest_hours'] = int(rest)
        
        # Save configuration
        with open('airline_config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print("✓ Crew thresholds updated")
    
    def _backup_data(self):
        """Backup system data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"output/backups/backup_{timestamp}.json"
        
        backup_data = {
            "config": self.config,
            "flights_data": self.flights_data,
            "timestamp": timestamp
        }
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"✓ Backup created: {backup_file}")
    
    def _restore_backup(self):
        """Restore system from backup"""
        import glob
        
        backups = glob.glob("output/backups/backup_*.json")
        if not backups:
            print("No backups found")
            return
        
        print("\nAvailable Backups:")
        for i, backup in enumerate(sorted(backups, reverse=True), 1):
            print(f"{i}. {os.path.basename(backup)}")
        
        choice = input("\nSelect backup to restore (number): ").strip()
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(backups):
                with open(backups[index], 'r') as f:
                    backup_data = json.load(f)
                
                # Restore configuration
                self.config = backup_data['config']
                with open('airline_config.json', 'w') as f:
                    json.dump(self.config, f, indent=2)
                
                # Restore flight data
                self.flights_data = backup_data['flights_data']
                
                print("✓ Backup restored successfully")
            else:
                print("Invalid selection")
        except (ValueError, IndexError):
            print("Invalid input")
    
    def _system_status(self):
        """Display system status"""
        print("\n" + "-" * 80)
        print("SYSTEM STATUS")
        print("-" * 80)
        
        print(f"Airline: {self.config['airline_name']}")
        print(f"System Uptime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Flights in System: {len(self.flights_data.get('flights', []))}")
        print(f"Aircraft in Fleet: {len(set(f.get('aircraft_id') for f in self.flights_data.get('flights', [])))}")
        print(f"Crew Members: {len(self.flights_data.get('crew', []))}")
        print(f"Pending Alerts: {self.alerts_queue.qsize()}")
        
        # Component status
        print("\nComponent Status:")
        for name, component in self.components.items():
            status = "ACTIVE" if component else "INACTIVE"
            print(f"  {name.replace('_', ' ').title()}: {status}")

def main():
    """Main entry point"""
    try:
        # Initialize system
        system = AirlineOperationsSystem()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == '--monitor':
                system.load_sample_data()
                system.run_real_time_monitoring()
            elif sys.argv[1] == '--analyze':
                system.run_single_analysis()
            elif sys.argv[1] == '--report':
                system.load_sample_data()
                system.generate_daily_report()
            else:
                print(f"Unknown argument: {sys.argv[1]}")
                print("Usage: python main.py [--monitor | --analyze | --report]")
                sys.exit(1)
        else:
            # Interactive mode
            system.interactive_menu()
    
    except KeyboardInterrupt:
        print("\n\nSystem stopped by user")
    except Exception as e:
        print(f"\nSystem error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()