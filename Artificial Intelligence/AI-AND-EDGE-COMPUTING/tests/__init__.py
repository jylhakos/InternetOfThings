"""
Tests for Edge Computing AI Agent
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.edge_agent import EdgeAgent
from src.sensor_agent import SensorAgent


def test_edge_agent_initialization():
    """Test Edge Agent initialization"""
    agent = EdgeAgent(agent_id="test-agent-001")
    
    assert agent.agent_id == "test-agent-001"
    assert agent.state == "initialized"
    assert agent.decisions_made == 0
    
    print("✓ Edge Agent initialization test passed")


def test_edge_agent_perceive():
    """Test Edge Agent perception"""
    agent = EdgeAgent(agent_id="test-agent-002")
    
    sensor_data = {
        'temperature': 25.5,
        'humidity': 60.0
    }
    
    observation = agent.perceive(sensor_data)
    
    assert 'timestamp' in observation
    assert observation['sensor_data'] == sensor_data
    assert observation['agent_id'] == "test-agent-002"
    
    print("✓ Edge Agent perception test passed")


def test_edge_agent_decide():
    """Test Edge Agent decision making"""
    agent = EdgeAgent(agent_id="test-agent-003")
    
    # Test high temperature scenario
    observation = {
        'sensor_data': {'temperature': 35}
    }
    
    action = agent.decide(observation)
    assert action == "activate_cooling"
    
    # Test motion detection scenario
    observation = {
        'sensor_data': {'motion_detected': True}
    }
    
    action = agent.decide(observation)
    assert action == "activate_alert"
    
    print("✓ Edge Agent decision test passed")


def test_sensor_agent_initialization():
    """Test Sensor Agent initialization"""
    agent = SensorAgent()
    
    assert len(agent.sensor_types) > 0
    assert 'temperature' in agent.sensor_types
    assert len(agent.readings) == 0
    
    print("✓ Sensor Agent initialization test passed")


def test_sensor_agent_read_sensors():
    """Test Sensor Agent reading"""
    agent = SensorAgent()
    
    readings = agent.read_sensors()
    
    assert 'timestamp' in readings
    assert 'sensors' in readings
    assert len(readings['sensors']) > 0
    
    print("✓ Sensor Agent reading test passed")


def test_sensor_agent_analyze():
    """Test Sensor Agent analysis"""
    agent = SensorAgent()
    
    # Test normal readings
    readings = {
        'timestamp': '2026-03-27T12:00:00',
        'sensors': {
            'temperature': 22.0,
            'humidity': 50.0
        }
    }
    
    issues = agent.analyze_readings(readings)
    assert isinstance(issues, list)
    
    # Test abnormal temperature
    readings['sensors']['temperature'] = 35.0
    issues = agent.analyze_readings(readings)
    assert len(issues) > 0
    assert any('temperature' in issue for issue in issues)
    
    print("✓ Sensor Agent analysis test passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Running Edge Computing AI Agent Tests")
    print("="*60 + "\n")
    
    try:
        test_edge_agent_initialization()
        test_edge_agent_perceive()
        test_edge_agent_decide()
        test_sensor_agent_initialization()
        test_sensor_agent_read_sensors()
        test_sensor_agent_analyze()
        
        print("\n" + "="*60)
        print("All tests passed! ✓")
        print("="*60 + "\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}\n")
        return False
    except Exception as e:
        print(f"\n✗ Error running tests: {e}\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
