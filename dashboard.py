"""
Module for displaying operations dashboard
"""
from datetime import datetime
from tabulate import tabulate

class Dashboard:
    def __init__(self):
        self.sections = []
        
    def display(self, flights_data, predictions):
        """Display the main dashboard"""
        print("\n" + "="*80)
        print("AIRLINE OPERATIONS DASHBOARD".center(80))
        print("="*80)
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*80)
        
        # Section 1: Flight Summary
        self._display_flight_summary(flights_data)
        
        # Section 2: Delay Predictions
        if predictions.get('delays'):
            self._display_delay_predictions(predictions['delays'])
        
        # Section 3: Health Alerts
        if predictions.get('health_alerts'):
            self._display_health_alerts(predictions['health_alerts'])
        
        # Section 4: Load Predictions
        if predictions.get('load'):
            self._display_load_predictions(predictions['load'])
        
        # Section 5: Crew Status
        if predictions.get('crew_assignments'):
            self._display_crew_status(predictions['crew_assignments'])
        
        # Section 6: Route Alerts
        if predictions.get('route_alerts'):
            self._display_route_alerts(predictions['route_alerts'])
        
        print("="*80)
    
    def _display_flight_summary(self, flights_data):
        """Display flight monitoring summary"""
        print("\n📊 FLIGHT MONITORING SUMMARY")
        print("-"*40)
        
        total_flights = len(flights_data)
        aircraft_types = {}
        routes = {}
        
        for flight in flights_data:
            aircraft_id = flight['aircraft_id']
            aircraft_types[aircraft_id] = aircraft_types.get(aircraft_id, 0) + 1
            
            # Get route
            for log in flight['logs']:
                if 'origin' in log and 'destination' in log:
                    route = f"{log['origin']}-{log['destination']}"
                    routes[route] = routes.get(route, 0) + 1
                    break
        
        print(f"Total Flights Monitored: {total_flights}")
        print(f"Unique Aircraft: {len(aircraft_types)}")
        print(f"Unique Routes: {len(routes)}")
        
        # Display popular routes
        if routes:
            print("\nTop Routes:")
            sorted_routes = sorted(routes.items(), key=lambda x: x[1], reverse=True)[:5]
            for route, count in sorted_routes:
                print(f"  {route}: {count} flights")
    
    def _display_delay_predictions(self, delay_predictions):
        """Display delay predictions"""
        print("\n⏰ DELAY PREDICTIONS")
        print("-"*40)
        
        if not delay_predictions:
            print("No delays predicted")
            return
        
        # Categorize delays
        minor_delays = [d for d in delay_predictions if d['severity'] == 'MINOR']
        moderate_delays = [d for d in delay_predictions if d['severity'] == 'MODERATE']
        significant_delays = [d for d in delay_predictions if d['severity'] == 'SIGNIFICANT']
        severe_delays = [d for d in delay_predictions if d['severity'] == 'SEVERE']
        
        print(f"Total Delays Predicted: {len(delay_predictions)}")
        print(f"Minor (<30 min): {len(minor_delays)}")
        print(f"Moderate (30-60 min): {len(moderate_delays)}")
        print(f"Significant (60-120 min): {len(significant_delays)}")
        print(f"Severe (>120 min): {len(severe_delays)}")
        
        # Display top delays
        if delay_predictions:
            print("\nTop Delays:")
            sorted_delays = sorted(delay_predictions, key=lambda x: x['predicted_delay_minutes'], reverse=True)[:5]
            
            table_data = []
            for delay in sorted_delays:
                table_data.append([
                    delay['flight_id'],
                    f"{delay['predicted_delay_minutes']} min",
                    delay['severity'],
                    ', '.join(delay['reasons'][:2])  # Show first 2 reasons
                ])
            
            headers = ["Flight", "Delay", "Severity", "Reasons"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def _display_health_alerts(self, health_alerts):
        """Display health alerts"""
        print("\n🚨 AIRCRAFT HEALTH ALERTS")
        print("-"*40)
        
        if not health_alerts:
            print("No health alerts")
            return
        
        critical_alerts = [a for a in health_alerts if a['severity'] == 'CRITICAL']
        high_alerts = [a for a in health_alerts if a['severity'] == 'HIGH']
        medium_alerts = [a for a in health_alerts if a['severity'] == 'MEDIUM']
        
        print(f"Total Alerts: {len(health_alerts)}")
        print(f"Critical: {len(critical_alerts)}")
        print(f"High: {len(high_alerts)}")
        print(f"Medium: {len(medium_alerts)}")
        
        # Display critical alerts
        if critical_alerts:
            print("\n🔴 CRITICAL ALERTS:")
            for alert in critical_alerts[:3]:  # Show top 3
                print(f"  Flight {alert['flight_id']}: {alert['message']}")
        
        # Alert types
        alert_types = {}
        for alert in health_alerts:
            alert_type = alert['alert_type']
            alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
        
        if alert_types:
            print("\nAlert Types:")
            for alert_type, count in list(alert_types.items())[:5]:
                print(f"  {alert_type}: {count}")
    
    def _display_load_predictions(self, load_predictions):
        """Display load predictions"""
        print("\n👥 PASSENGER LOAD PREDICTIONS")
        print("-"*40)
        
        if not load_predictions:
            print("No load predictions")
            return
        
        # Calculate statistics
        total_passengers = sum(p['predicted_passengers'] for p in load_predictions)
        avg_load_factor = sum(p['predicted_load_factor'] for p in load_predictions) / len(load_predictions)
        
        # Count scenarios
        overbooking = sum(1 for p in load_predictions 
                         if any(s['type'] == 'OVERBOOKING_RISK' for s in p['scenarios']))
        high_demand = sum(1 for p in load_predictions 
                         if any(s['type'] == 'HIGH_DEMAND' for s in p['scenarios']))
        low_utilization = sum(1 for p in load_predictions 
                            if any(s['type'] == 'LOW_UTILIZATION' for s in p['scenarios']))
        
        print(f"Total Predicted Passengers: {total_passengers:,}")
        print(f"Average Load Factor: {avg_load_factor:.1%}")
        print(f"Flights with Overbooking Risk: {overbooking}")
        print(f"High Demand Flights: {high_demand}")
        print(f"Underutilized Flights: {low_utilization}")
        
        # Display top loaded flights
        if load_predictions:
            print("\nTop Loaded Flights:")
            sorted_loads = sorted(load_predictions, key=lambda x: x['predicted_load_factor'], reverse=True)[:5]
            
            table_data = []
            for load in sorted_loads:
                table_data.append([
                    load['flight_id'],
                    f"{load['predicted_passengers']}/{load['capacity']}",
                    f"{load['predicted_load_factor']:.1%}",
                    load['demand_level']
                ])
            
            headers = ["Flight", "Passengers", "Load Factor", "Demand Level"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def _display_crew_status(self, crew_data):
        """Display crew scheduling status"""
        print("\n👨‍✈️ CREW SCHEDULING STATUS")
        print("-"*40)
        
        assignments = crew_data.get('assignments', [])
        issues = crew_data.get('issues', [])
        summary = crew_data.get('summary', {})
        
        print(f"Flights Scheduled: {summary.get('total_flights_scheduled', 0)}")
        print(f"Crew Members Utilized: {summary.get('total_crew_utilized', 0)}")
        print(f"Average Flights per Crew: {summary.get('avg_flights_per_crew', 0):.1f}")
        
        # Display issues
        if issues:
            critical_issues = [i for i in issues if i['severity'] == 'CRITICAL']
            high_issues = [i for i in issues if i['severity'] == 'HIGH']
            
            print(f"\n⚠️  Scheduling Issues: {len(issues)}")
            print(f"   Critical: {len(critical_issues)}")
            print(f"   High: {len(high_issues)}")
            
            if critical_issues:
                print("\n🔴 Critical Issues:")
                for issue in critical_issues[:3]:
                    print(f"  {issue['type']}: {issue.get('message', 'No message')}")
        else:
            print("\n✓ No scheduling issues detected")
    
    def _display_route_alerts(self, route_alerts):
        """Display route monitoring alerts"""
        print("\n🛣️  ROUTE MONITORING")
        print("-"*40)
        
        if not route_alerts:
            print("No route alerts")
            return
        
        # Categorize alerts
        diversion_alerts = [a for a in route_alerts if a['alert_type'] == 'DIVERSION_RECOMMENDED']
        weather_alerts = [a for a in route_alerts if a['alert_type'] != 'DIVERSION_RECOMMENDED']
        
        critical_weather = [a for a in weather_alerts if a['severity'] == 'CRITICAL']
        high_weather = [a for a in weather_alerts if a['severity'] == 'HIGH']
        
        print(f"Total Route Alerts: {len(route_alerts)}")
        print(f"Diversions Recommended: {len(diversion_alerts)}")
        print(f"Weather Alerts: {len(weather_alerts)}")
        print(f"  Critical: {len(critical_weather)}")
        print(f"  High: {len(high_weather)}")
        
        # Display diversions
        if diversion_alerts:
            print("\n🔄 Diversion Recommendations:")
            for alert in diversion_alerts[:3]:
                print(f"  Flight {alert['flight_id']}: {alert['message']}")