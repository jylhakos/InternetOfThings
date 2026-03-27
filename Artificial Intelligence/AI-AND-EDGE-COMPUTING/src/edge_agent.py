"""
Edge AI Agent - Autonomous agent for edge computing devices

This module implements an autonomous AI agent that runs on edge devices,
providing real-time decision-making capabilities with low latency.
"""

import time
import logging
from typing import Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EdgeAgent:
    """
    Autonomous AI Agent for Edge Computing
    
    Characteristics:
    - Autonomy: Operates without constant human supervision
    - Reactivity: Responds to environmental changes
    - Proactivity: Anticipates future needs
    - Learning: Improves over time
    """
    
    def __init__(self, agent_id: str, config: Dict[str, Any] = None):
        """
        Initialize the Edge AI Agent
        
        Args:
            agent_id: Unique identifier for this agent
            config: Configuration dictionary
        """
        self.agent_id = agent_id
        self.config = config or {}
        self.state = "initialized"
        self.start_time = datetime.now()
        self.decisions_made = 0
        self.observations = []
        
        logger.info(f"Edge Agent {self.agent_id} initialized")
    
    def perceive(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perceive the environment from sensor data
        
        Args:
            sensor_data: Dictionary containing sensor readings
            
        Returns:
            Processed observations
        """
        observation = {
            'timestamp': datetime.now().isoformat(),
            'sensor_data': sensor_data,
            'agent_id': self.agent_id
        }
        
        self.observations.append(observation)
        logger.info(f"Agent {self.agent_id} perceived: {sensor_data}")
        
        return observation
    
    def decide(self, observation: Dict[str, Any]) -> str:
        """
        Make a decision based on observations
        
        Args:
            observation: Processed observation data
            
        Returns:
            Decision action
        """
        sensor_data = observation.get('sensor_data', {})
        
        # Simple decision logic (can be replaced with ML model)
        if sensor_data.get('temperature', 0) > 30:
            action = "activate_cooling"
        elif sensor_data.get('motion_detected', False):
            action = "activate_alert"
        elif sensor_data.get('light_level', 100) < 20:
            action = "activate_lights"
        else:
            action = "monitor"
        
        self.decisions_made += 1
        logger.info(f"Agent {self.agent_id} decided: {action}")
        
        return action
    
    def act(self, action: str) -> bool:
        """
        Execute the decided action
        
        Args:
            action: Action to execute
            
        Returns:
            Success status
        """
        logger.info(f"Agent {self.agent_id} executing: {action}")
        
        # Simulate action execution
        actions_map = {
            "activate_cooling": self._activate_cooling,
            "activate_alert": self._activate_alert,
            "activate_lights": self._activate_lights,
            "monitor": self._monitor
        }
        
        if action in actions_map:
            return actions_map[action]()
        else:
            logger.warning(f"Unknown action: {action}")
            return False
    
    def learn(self, observation: Dict[str, Any], action: str, reward: float):
        """
        Learn from experience (simplified reinforcement learning)
        
        Args:
            observation: The observation that led to the action
            action: The action taken
            reward: The reward received
        """
        experience = {
            'observation': observation,
            'action': action,
            'reward': reward,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Agent {self.agent_id} learning from experience (reward: {reward})")
        # In a real implementation, this would update a model
    
    def run(self, duration_seconds: int = 60):
        """
        Run the agent for a specified duration
        
        Args:
            duration_seconds: How long to run the agent
        """
        logger.info(f"Agent {self.agent_id} starting operation")
        self.state = "running"
        
        start = time.time()
        iteration = 0
        
        while (time.time() - start) < duration_seconds:
            iteration += 1
            
            # Simulate sensor data
            sensor_data = self._simulate_sensor_data(iteration)
            
            # Agent cycle: Perceive -> Decide -> Act
            observation = self.perceive(sensor_data)
            action = self.decide(observation)
            success = self.act(action)
            
            # Simple reward calculation
            reward = 1.0 if success else -1.0
            self.learn(observation, action, reward)
            
            # Sleep to simulate real-time operation
            time.sleep(2)
        
        self.state = "stopped"
        logger.info(f"Agent {self.agent_id} stopped after {iteration} iterations")
        self.print_stats()
    
    def _simulate_sensor_data(self, iteration: int) -> Dict[str, Any]:
        """Simulate sensor data for testing"""
        import random
        
        return {
            'temperature': 20 + random.uniform(-5, 15),
            'humidity': 50 + random.uniform(-10, 20),
            'light_level': random.randint(0, 100),
            'motion_detected': random.choice([True, False]),
            'iteration': iteration
        }
    
    def _activate_cooling(self) -> bool:
        """Activate cooling system"""
        logger.info("Cooling system activated")
        return True
    
    def _activate_alert(self) -> bool:
        """Activate alert system"""
        logger.info("Alert system activated - Motion detected!")
        return True
    
    def _activate_lights(self) -> bool:
        """Activate lights"""
        logger.info("Lights activated")
        return True
    
    def _monitor(self) -> bool:
        """Continue monitoring"""
        logger.debug("Continuing to monitor...")
        return True
    
    def print_stats(self):
        """Print agent statistics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*50)
        print(f"Edge Agent Statistics - {self.agent_id}")
        print("="*50)
        print(f"State: {self.state}")
        print(f"Uptime: {uptime:.2f} seconds")
        print(f"Decisions Made: {self.decisions_made}")
        print(f"Observations Recorded: {len(self.observations)}")
        print("="*50 + "\n")


def main():
    """Main function to demonstrate the Edge AI Agent"""
    print("Starting Edge AI Agent Demo")
    print("-" * 50)
    
    # Create and configure agent
    config = {
        'mode': 'autonomous',
        'learning_rate': 0.01
    }
    
    agent = EdgeAgent(agent_id="edge-agent-001", config=config)
    
    # Run the agent for 30 seconds
    agent.run(duration_seconds=30)
    
    print("\nDemo completed successfully!")


if __name__ == "__main__":
    main()
