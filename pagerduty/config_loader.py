import yaml
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ServiceConfig:
    name: str
    url: str

@dataclass
class PagerDutyConfig:
    token: str
    services: List[ServiceConfig]

def load_config(config_path: str = "PagerDuty.yaml") -> PagerDutyConfig:
    """Load PagerDuty configuration from YAML file"""
    with open(config_path, 'r') as file:
        data = yaml.safe_load(file)
    
    services = [
        ServiceConfig(name=service['name'], url=service['url'])
        for service in data.get('services', [])
    ]
    
    return PagerDutyConfig(
        token=data['token'],
        services=services
    )