# Rule Engine with AST and Weather Monitoring System

This repository contains two Python scripts: a rule engine using Abstract Syntax Trees (AST) and a weather monitoring system.

## Assessment 1: Rule Engine with AST

File: `assessment1.py`

This script implements a rule engine using Abstract Syntax Trees (AST) for parsing and evaluating complex logical rules.

### Features:
- Tokenization of rule strings
- Parsing tokens into an Abstract Syntax Tree
- Evaluation of rules against provided data
- Combination of multiple rules

### Usage:
python
rule = "((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)"
ast = create_rule(rule)
data = {"age": 35, "department": "Sales", "salary": 60000, "experience": 3}
result = evaluate_rule(ast, data)


## Assessment 2: Weather Monitoring System

File: `assessment2.py`

This script implements a weather monitoring system that collects data from the OpenWeatherMap API, stores it in a SQLite database, and provides analysis and visualization capabilities.

### Features:
- Fetches weather data for multiple cities
- Stores data in a SQLite database
- Calculates daily weather summaries
- Provides temperature alerts
- Visualizes temperature trends

### Configuration:
Replace `'your_openweathermap_api_key'` with your actual OpenWeatherMap API key:
API_KEY = 'def755d9dda5eafb2802baba0f41d1a0'

### Usage:
Run the script to start collecting weather data:

The script will run continuously, fetching data every 5 minutes. To stop, use Ctrl+C.

## Requirements
- Python 3.x
- Required libraries: 
  - For assessment1.py: No external libraries required
  - For assessment2.py: requests, sqlite3, apscheduler, matplotlib

## Installation
1. Clone this repository
2. Install required libraries:
   ```
   pip install requests apscheduler matplotlib
   ```
3. Replace the API key in assessment2.py with your OpenWeatherMap API key
4. Run the desired script

## License
[MIT License](https://opensource.org/licenses/MIT)

