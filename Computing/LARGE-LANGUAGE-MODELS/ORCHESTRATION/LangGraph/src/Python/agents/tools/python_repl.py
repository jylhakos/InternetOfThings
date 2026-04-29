from langchain_community.tools.python.tool import PythonREPLTool
from langchain_core.tools import BaseTool
from typing import Dict, Any, Optional
import json
import asyncio

class CustomPythonREPLTool(PythonREPLTool):
    """Enhanced Python REPL tool for bike rental calculations"""
    
    name = "python_repl"
    description = """
    Execute Python code for calculations, data processing, and analysis.
    Useful for:
    - Calculating distances between coordinates
    - Processing bike station data
    - Computing rental costs and pricing
    - Analyzing bike availability patterns
    - Converting units and currencies
    
    Input should be valid Python code.
    """
    
    def _run(self, query: str) -> str:
        """Execute Python code with enhanced error handling"""
        try:
            # Add common imports for bike rental calculations
            enhanced_query = f"""
import math
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Helper functions for bike rental
def calculate_distance(lat1, lon1, lat2, lon2):
    '''Calculate distance between two coordinates in km'''
    R = 6371  # Earth's radius in kilometers
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def calculate_rental_cost(hours, base_rate=2.0, hourly_rate=1.5):
    '''Calculate bike rental cost'''
    if hours <= 0:
        return 0
    return base_rate + (hours - 1) * hourly_rate if hours > 1 else base_rate

def format_currency(amount, currency='EUR'):
    '''Format currency amount'''
    return f"{amount:.2f} {currency}"

# Execute user query
{query}
"""
            
            result = super()._run(enhanced_query)
            return result
            
        except Exception as e:
            return f"Error executing Python code: {str(e)}"

# Create the Python REPL tool instance
python_repl_tool = CustomPythonREPLTool()
