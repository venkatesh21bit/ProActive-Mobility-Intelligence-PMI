"""
Diagnosis Agent
Maps ML predictions to specific vehicle components, failure modes, and repair actions
"""

import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import random

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComponentDiagnostic:
    """Diagnostic information for a component"""
    
    def __init__(
        self,
        component_name: str,
        failure_probability: float,
        failure_mode: str,
        symptoms: List[str],
        repair_actions: List[str],
        estimated_downtime_hours: float,
        estimated_cost: float,
        urgency: str
    ):
        self.component_name = component_name
        self.failure_probability = failure_probability
        self.failure_mode = failure_mode
        self.symptoms = symptoms
        self.repair_actions = repair_actions
        self.estimated_downtime_hours = estimated_downtime_hours
        self.estimated_cost = estimated_cost
        self.urgency = urgency
    
    def to_dict(self) -> Dict:
        return {
            'component_name': self.component_name,
            'failure_probability': self.failure_probability,
            'failure_mode': self.failure_mode,
            'symptoms': self.symptoms,
            'repair_actions': self.repair_actions,
            'estimated_downtime_hours': self.estimated_downtime_hours,
            'estimated_cost': self.estimated_cost,
            'urgency': self.urgency
        }


class DiagnosisAgent:
    """
    Agent that maps ML predictions to specific components and repair actions
    """
    
    def __init__(self):
        # Component diagnosis rules based on anomaly patterns
        self.component_rules = self._initialize_component_rules()
        
    def _initialize_component_rules(self) -> Dict:
        """Initialize diagnostic rules for different components"""
        return {
            'engine_overheating': {
                'components': ['Thermostat', 'Water Pump', 'Radiator', 'Cooling Fan'],
                'symptoms': ['High engine temperature', 'Elevated coolant temperature'],
                'failure_modes': {
                    'Thermostat': 'Stuck closed, restricting coolant flow',
                    'Water Pump': 'Impeller damage or bearing failure',
                    'Radiator': 'Clogged cores or external blockage',
                    'Cooling Fan': 'Motor failure or electrical issue'
                },
                'repair_actions': {
                    'Thermostat': ['Replace thermostat', 'Flush cooling system'],
                    'Water Pump': ['Replace water pump', 'Replace timing belt if applicable', 'Refill coolant'],
                    'Radiator': ['Flush and clean radiator', 'Replace if damaged', 'Check hoses'],
                    'Cooling Fan': ['Replace fan motor', 'Check fan relay and fuses', 'Inspect wiring']
                },
                'cost_range': (200, 1500),
                'downtime_hours': (2, 6)
            },
            'low_oil_pressure': {
                'components': ['Oil Pump', 'Engine Bearings', 'Oil Filter', 'PCV Valve'],
                'symptoms': ['Low oil pressure reading', 'Engine noise'],
                'failure_modes': {
                    'Oil Pump': 'Worn gears or pickup screen blockage',
                    'Engine Bearings': 'Wear or damage causing oil leakage',
                    'Oil Filter': 'Clogged filter restricting flow',
                    'PCV Valve': 'Stuck valve affecting crankcase pressure'
                },
                'repair_actions': {
                    'Oil Pump': ['Replace oil pump', 'Clean oil pickup screen', 'Change oil and filter'],
                    'Engine Bearings': ['Engine teardown and bearing replacement', 'Possible engine rebuild'],
                    'Oil Filter': ['Replace oil filter', 'Change engine oil', 'Check for sludge'],
                    'PCV Valve': ['Replace PCV valve', 'Clean breather system']
                },
                'cost_range': (150, 3500),
                'downtime_hours': (3, 24)
            },
            'high_vibration': {
                'components': ['Engine Mounts', 'Wheel Balance', 'Drive Shaft', 'Brake Rotors'],
                'symptoms': ['Excessive vibration', 'Unusual shaking'],
                'failure_modes': {
                    'Engine Mounts': 'Worn or broken mounts allowing excess movement',
                    'Wheel Balance': 'Unbalanced wheels or damaged tires',
                    'Drive Shaft': 'Bent shaft or worn U-joints',
                    'Brake Rotors': 'Warped rotors causing pedal vibration'
                },
                'repair_actions': {
                    'Engine Mounts': ['Replace worn engine mounts', 'Inspect transmission mounts'],
                    'Wheel Balance': ['Balance and rotate tires', 'Check for tire damage', 'Inspect suspension'],
                    'Drive Shaft': ['Replace drive shaft', 'Replace U-joints', 'Check CV joints'],
                    'Brake Rotors': ['Resurface or replace rotors', 'Replace brake pads', 'Inspect calipers']
                },
                'cost_range': (100, 1200),
                'downtime_hours': (1, 4)
            },
            'battery_degradation': {
                'components': ['Battery', 'Alternator', 'Voltage Regulator', 'Battery Cables'],
                'symptoms': ['Low battery voltage', 'Starting difficulties'],
                'failure_modes': {
                    'Battery': 'Cell degradation or sulfation',
                    'Alternator': 'Diode failure or bearing wear',
                    'Voltage Regulator': 'Improper charging voltage',
                    'Battery Cables': 'Corrosion or loose connections'
                },
                'repair_actions': {
                    'Battery': ['Load test battery', 'Replace if failed', 'Check charging system'],
                    'Alternator': ['Test alternator output', 'Replace alternator', 'Replace serpentine belt'],
                    'Voltage Regulator': ['Replace voltage regulator', 'Check wiring harness'],
                    'Battery Cables': ['Clean terminals', 'Replace corroded cables', 'Apply protective coating']
                },
                'cost_range': (100, 800),
                'downtime_hours': (1, 3)
            },
            'fuel_system': {
                'components': ['Fuel Pump', 'Fuel Filter', 'Fuel Injectors', 'Fuel Pressure Regulator'],
                'symptoms': ['Poor fuel economy', 'Engine hesitation', 'Loss of power'],
                'failure_modes': {
                    'Fuel Pump': 'Pump motor failure or clogged strainer',
                    'Fuel Filter': 'Restriction from contamination',
                    'Fuel Injectors': 'Clogging or electrical failure',
                    'Fuel Pressure Regulator': 'Stuck valve or diaphragm leak'
                },
                'repair_actions': {
                    'Fuel Pump': ['Replace fuel pump assembly', 'Clean fuel tank', 'Replace fuel filter'],
                    'Fuel Filter': ['Replace fuel filter', 'Drain fuel tank if contaminated'],
                    'Fuel Injectors': ['Clean injectors', 'Replace failed injectors', 'Check fuel pressure'],
                    'Fuel Pressure Regulator': ['Replace regulator', 'Check vacuum lines']
                },
                'cost_range': (150, 1500),
                'downtime_hours': (2, 6)
            }
        }
    
    def diagnose(self, prediction: Dict) -> Dict:
        """
        Diagnose based on ML prediction and feature importance
        
        Args:
            prediction: Dictionary from ML prediction service
            
        Returns:
            Diagnostic report with component details
        """
        logger.info(f"Diagnosing vehicle {prediction.get('vehicle_id')} with severity {prediction.get('severity')}")
        
        # Extract relevant information
        severity = prediction.get('severity', 'unknown')
        explanation = prediction.get('explanation', '')
        feature_importance = prediction.get('feature_importance', {})
        failure_probability = prediction.get('failure_probability', 0.0)
        
        # Identify issue category
        issue_category = self._identify_issue_category(explanation, feature_importance)
        
        # Get component diagnostics
        components = self._diagnose_components(issue_category, failure_probability, severity)
        
        # Generate overall assessment
        assessment = self._generate_assessment(components, severity)
        
        return {
            'vehicle_id': prediction.get('vehicle_id'),
            'vin': prediction.get('vin'),
            'diagnosis_timestamp': datetime.utcnow().isoformat(),
            'issue_category': issue_category,
            'severity': severity,
            'primary_component': components[0].to_dict() if components else None,
            'related_components': [c.to_dict() for c in components[1:]] if len(components) > 1 else [],
            'total_estimated_cost': sum(c.estimated_cost for c in components),
            'total_estimated_downtime_hours': max((c.estimated_downtime_hours for c in components), default=0),
            'urgency': self._determine_urgency(severity, components),
            'assessment': assessment,
            'recommended_action': self._recommend_action(severity, components)
        }
    
    def _identify_issue_category(self, explanation: str, feature_importance: Dict) -> str:
        """Identify the main issue category from explanation and features"""
        explanation_lower = explanation.lower()
        
        # Check for specific patterns
        if 'temperature' in explanation_lower or 'engine_temperature' in str(feature_importance):
            return 'engine_overheating'
        elif 'oil' in explanation_lower or 'oil_pressure' in str(feature_importance):
            return 'low_oil_pressure'
        elif 'vibration' in explanation_lower or 'vibration_level' in str(feature_importance):
            return 'high_vibration'
        elif 'battery' in explanation_lower or 'battery_voltage' in str(feature_importance):
            return 'battery_degradation'
        elif 'fuel' in explanation_lower:
            return 'fuel_system'
        else:
            # Default to engine overheating if unclear
            return 'engine_overheating'
    
    def _diagnose_components(
        self,
        issue_category: str,
        failure_probability: float,
        severity: str
    ) -> List[ComponentDiagnostic]:
        """Generate component diagnostics for the issue category"""
        
        if issue_category not in self.component_rules:
            return []
        
        rules = self.component_rules[issue_category]
        components = []
        
        # Select 1-3 most likely components based on severity
        num_components = 1 if severity in ['low', 'medium'] else min(3, len(rules['components']))
        
        for i, component_name in enumerate(rules['components'][:num_components]):
            # Probability decreases for secondary components
            component_probability = failure_probability * (1.0 - i * 0.2)
            
            component = ComponentDiagnostic(
                component_name=component_name,
                failure_probability=component_probability,
                failure_mode=rules['failure_modes'][component_name],
                symptoms=rules['symptoms'],
                repair_actions=rules['repair_actions'][component_name],
                estimated_downtime_hours=random.uniform(*rules['downtime_hours']),
                estimated_cost=random.uniform(*rules['cost_range']),
                urgency=severity
            )
            components.append(component)
        
        # Sort by probability
        components.sort(key=lambda x: x.failure_probability, reverse=True)
        
        return components
    
    def _determine_urgency(self, severity: str, components: List[ComponentDiagnostic]) -> str:
        """Determine urgency level"""
        if severity == 'critical':
            return 'immediate'
        elif severity == 'high':
            return 'urgent'
        elif severity == 'medium':
            return 'soon'
        else:
            return 'routine'
    
    def _generate_assessment(self, components: List[ComponentDiagnostic], severity: str) -> str:
        """Generate human-readable assessment"""
        if not components:
            return "Unable to determine specific component failure."
        
        primary = components[0]
        assessment = f"Primary concern: {primary.component_name} - {primary.failure_mode}. "
        
        if len(components) > 1:
            others = ", ".join(c.component_name for c in components[1:])
            assessment += f"Related components that may need attention: {others}. "
        
        if severity in ['critical', 'high']:
            assessment += "Immediate service recommended to prevent further damage."
        else:
            assessment += "Schedule service at earliest convenience."
        
        return assessment
    
    def _recommend_action(self, severity: str, components: List[ComponentDiagnostic]) -> str:
        """Recommend next action"""
        if severity == 'critical':
            return "Stop driving immediately. Arrange for towing to service center."
        elif severity == 'high':
            return "Schedule service within 24-48 hours. Avoid long trips."
        elif severity == 'medium':
            return "Schedule service within the next week."
        else:
            return "Include in next routine maintenance visit."
