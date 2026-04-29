"""
Sensor Agent - Real-time sensor data processing on edge devices

This module implements an agent that processes sensor data in real-time
on edge devices, demonstrating low-latency decision-making.
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any, List
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SensorAgent:
    """
    Agent for processing sensor data on edge devices
    """
    
    def __init__(self, sensor_types: List[str] = None):
        """
        Initialize Sensor Agent
        
        Args:
            sensor_types: List of sensor types to monitor
        """
        self.sensor_types = sensor_types or [
            'temperature',
            'humidity',
            'pressure',
            'motion',
            'light'
        ]
        
        self.readings = []
        self.alerts = []
        self.start_time = datetime.now()
        
        # Thresholds for alerting
        self.thresholds = {
            'temperature': {'min': 15, 'max': 30},
            'humidity': {'min': 30, 'max': 70},
            'pressure': {'min': 980, 'max': 1040},
            'light': {'min': 10, 'max': 90}
        }
        
        logger.info(f"Sensor Agent initialized with sensors: {self.sensor_types}")
    
    def read_sensors(self) -> Dict[str, Any]:
        """
        Simulate reading from multiple sensors
        
        Returns:
            Dictionary of sensor readings
        """
        # In a real implementation, this would read from actual sensors
        # For now, we simulate sensor data
        
        readings = {
            'timestamp': datetime.now().isoformat(),
            'sensors': {}
        }
        
        for sensor in self.sensor_types:
            if sensor == 'temperature':
                readings['sensors'][sensor] = round(random.uniform(10, 35), 2)
            elif sensor == 'humidity':
                readings['sensors'][sensor] = round(random.uniform(20, 80), 2)
            elif sensor == 'pressure':
                readings['sensors'][sensor] = round(random.uniform(970, 1050), 2)
            elif sensor == 'motion':
                readings['sensors'][sensor] = random.choice([True, False])
            elif sensor == 'light':
                readings['sensors'][sensor] = round(random.uniform(0, 100), 2)
        
        self.readings.append(readings)
        
        return readings
    
    def analyze_readings(self, readings: Dict[str, Any]) -> List[str]:
        """
        Analyze sensor readings and detect anomalies
        
        Args:
            readings: Sensor readings dictionary
            
        Returns:
            List of detected issues
        """
        issues = []
        sensors = readings.get('sensors', {})
        
        for sensor_name, value in sensors.items():
            if sensor_name in self.thresholds:
                threshold = self.thresholds[sensor_name]
                
                if isinstance(value, (int, float)):
                    if value < threshold['min']:
                        issues.append(f"{sensor_name} too low: {value}")
                    elif value > threshold['max']:
                        issues.append(f"{sensor_name} too high: {value}")
            
            # Special case for motion sensor
            if sensor_name == 'motion' and value is True:
                issues.append("Motion detected")
        
        return issues
    
    def process_data(self, readings: Dict[str, Any]):
        """
        Process sensor data and take actions
        
        Args:
            readings: Sensor readings dictionary
        """
        issues = self.analyze_readings(readings)
        
        if issues:
            alert = {
                'timestamp': readings['timestamp'],
                'issues': issues,
                'readings': readings['sensors']
            }
            self.alerts.append(alert)
            
            logger.warning(f"ALERT: {', '.join(issues)}")
            
            # Take corrective actions
            for issue in issues:
                self.take_action(issue, readings)
        else:
            logger.info(f"All sensors within normal range")
    
    def take_action(self, issue: str, readings: Dict[str, Any]):
        """
        Take corrective action based on detected issue
        
        Args:
            issue: Description of the issue
            readings: Current sensor readings
        """
        if "temperature too high" in issue:
            logger.info("ACTION: Activating cooling system")
        elif "temperature too low" in issue:
            logger.info("ACTION: Activating heating system")
        elif "humidity too high" in issue:
            logger.info("ACTION: Activating dehumidifier")
        elif "humidity too low" in issue:
            logger.info("ACTION: Activating humidifier")
        elif "Motion detected" in issue:
            logger.info("ACTION: Recording motion event, activating security camera")
        elif "light" in issue:
            logger.info("ACTION: Adjusting lighting levels")
    
    def run_monitoring(self, duration_seconds: int = 60, interval: float = 2.0):
        """
        Run continuous sensor monitoring
        
        Args:
            duration_seconds: How long to monitor
            interval: Time between readings in seconds
        """
        logger.info(f"Starting sensor monitoring for {duration_seconds} seconds")
        logger.info(f"Reading interval: {interval} seconds")
        
        start = time.time()
        iteration = 0
        
        while (time.time() - start) < duration_seconds:
            iteration += 1
            
            # Read sensors
            readings = self.read_sensors()
            
            # Display readings
            print(f"\n>>> Iteration {iteration} - {readings['timestamp']}")
            for sensor, value in readings['sensors'].items():
                print(f"  {sensor}: {value}")
            
            # Process and analyze
            self.process_data(readings)
            
            # Wait before next reading
            time.sleep(interval)
        
        logger.info("Monitoring completed")
        self.print_summary()
    
    def print_summary(self):
        """
        Print monitoring summary
        """
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*60)
        print("Sensor Monitoring Summary")
        print("="*60)
        print(f"Monitoring Duration: {uptime:.2f} seconds")
        print(f"Total Readings: {len(self.readings)}")
        print(f"Total Alerts: {len(self.alerts)}")
        
        if self.alerts:
            print("\nRecent Alerts:")
            for alert in self.alerts[-5:]:  # Show last 5 alerts
                print(f"  - {alert['timestamp']}: {', '.join(alert['issues'])}")
        
        print("="*60 + "\n")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Calculate statistics from sensor readings
        
        Returns:
            Dictionary of statistics
        """
        if not self.readings:
            return {}
        
        stats = {}
        
        for sensor in self.sensor_types:
            values = []
            for reading in self.readings:
                sensor_data = reading['sensors'].get(sensor)
                if isinstance(sensor_data, (int, float)):
                    values.append(sensor_data)
            
            if values:
                stats[sensor] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'count': len(values)
                }
        
        return stats


def main():
    """Main function to demonstrate Sensor Agent"""
    print("\n" + "="*60)
    print("Edge Sensor Agent Demo")
    print("="*60)
    
    # Create sensor agent
    agent = SensorAgent()
    
    print("\nMonitoring sensors: temperature, humidity, pressure, motion, light")
    print("\nPress Ctrl+C to stop monitoring early...")
    
    try:
        # Run monitoring for 30 seconds
        agent.run_monitoring(duration_seconds=30, interval=3.0)
        
        # Print statistics
        stats = agent.get_statistics()
        print("\nSensor Statistics:")
        for sensor, data in stats.items():
            print(f"\n{sensor.upper()}:")
            print(f"  Min: {data['min']:.2f}")
            print(f"  Max: {data['max']:.2f}")
            print(f"  Avg: {data['avg']:.2f}")
        
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
        agent.print_summary()
    
    print("\nDemo completed!")


if __name__ == "__main__":
    main()
