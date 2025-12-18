import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from 'react-native';
import Svg, { 
  Defs, LinearGradient, Stop, RadialGradient, Filter, 
  FeGaussianBlur, FeMerge, FeMergeNode, Ellipse, G, 
  Path, Circle, Rect, Line, Polyline 
} from 'react-native-svg';

const MotorcycleVisualization = ({ vehicleData }) => {
  const [selectedComponent, setSelectedComponent] = useState(null);
  const [hoveredComponent, setHoveredComponent] = useState(null);

  const getComponentColor = (componentName) => {
    const component = vehicleData?.components?.[componentName];
    if (!component) return '#64748b';
    if (component.status === 'critical') return '#ef4444';
    if (component.status === 'warning') return '#f59e0b';
    return '#22c55e';
  };

  const getComponentOpacity = (componentName) => {
    if (!hoveredComponent) return 0.6;
    return hoveredComponent === componentName ? 0.9 : 0.3;
  };

  // Component clickable areas mapped to motorcycle parts
  const componentAreas = {
    engine: { x: 210, y: 110, width: 90, height: 80, label: 'Engine' },
    transmission: { x: 250, y: 130, width: 70, height: 60, label: 'Transmission' },
    brakes: { x: 60, y: 110, width: 60, height: 60, label: 'Brakes' },
    battery: { x: 180, y: 70, width: 60, height: 40, label: 'Battery' },
    cooling_system: { x: 290, y: 100, width: 60, height: 50, label: 'Cooling' },
    oil_system: { x: 200, y: 160, width: 70, height: 40, label: 'Oil System' },
    suspension: { x: 80, y: 80, width: 60, height: 50, label: 'Suspension' },
    tires: { x: 270, y: 110, width: 100, height: 70, label: 'Tires' },
    exhaust: { x: 250, y: 180, width: 100, height: 30, label: 'Exhaust' },
    fuel_system: { x: 330, y: 60, width: 60, height: 55, label: 'Fuel System' }
  };

  const getStatusIcon = (status) => {
    if (status === 'critical') return '🔴';
    if (status === 'warning') return '🟡';
    return '🟢';
  };

  return (
    <View style={styles.container}>
      {/* Vehicle Info Header */}
      <View style={styles.header}>
        <Text style={styles.vehicleTitle}>
          {vehicleData?.vehicle?.make} {vehicleData?.vehicle?.model}
        </Text>
        <Text style={styles.vehicleInfo}>
          VIN: {vehicleData?.vehicle?.vin}
        </Text>
        <Text style={styles.vehicleInfo}>
          Year: {vehicleData?.vehicle?.year} | Mileage: {vehicleData?.vehicle?.mileage?.toLocaleString()} km
        </Text>
      </View>

      {/* Health Status Card */}
      <View style={[
        styles.healthCard,
        { backgroundColor: 
          vehicleData?.health?.overall_status === 'critical' ? '#7f1d1d' :
          vehicleData?.health?.overall_status === 'warning' ? '#78350f' :
          '#14532d'
        }
      ]}>
        <View style={styles.healthHeader}>
          <Text style={styles.healthStatus}>
            {getStatusIcon(vehicleData?.health?.overall_status)} {vehicleData?.health?.overall_status?.toUpperCase()} Status
          </Text>
          <Text style={styles.healthScore}>
            {vehicleData?.health?.overall_score}%
          </Text>
        </View>
        <View style={styles.healthStats}>
          <View style={styles.statItem}>
            <Text style={[styles.statValue, { color: '#ef4444' }]}>
              {vehicleData?.health?.critical_components}
            </Text>
            <Text style={styles.statLabel}>Critical</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={[styles.statValue, { color: '#f59e0b' }]}>
              {vehicleData?.health?.warning_components}
            </Text>
            <Text style={styles.statLabel}>Warning</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={[styles.statValue, { color: '#22c55e' }]}>
              {vehicleData?.health?.healthy_components}
            </Text>
            <Text style={styles.statLabel}>Healthy</Text>
          </View>
        </View>
      </View>

      {/* Motorcycle SVG Visualization */}
      <View style={styles.visualizationContainer}>
        <Text style={styles.sectionTitle}>Interactive Component Map</Text>
        <Text style={styles.sectionSubtitle}>Tap on highlighted areas to see details</Text>
        
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.svgScroll}>
          <Svg width={500} height={300} viewBox="0 0 500 300">
            <Defs>
              <LinearGradient id="motoBodyGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <Stop offset="0%" stopColor="#e2e8f0" stopOpacity="1" />
                <Stop offset="50%" stopColor="#f8fafc" stopOpacity="1" />
                <Stop offset="100%" stopColor="#cbd5e1" stopOpacity="1" />
              </LinearGradient>

              <LinearGradient id="motoWindGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <Stop offset="0%" stopColor="#0f172a" stopOpacity="0.8" />
                <Stop offset="100%" stopColor="#334155" stopOpacity="0.6" />
              </LinearGradient>

              <RadialGradient id="motoRimGrad" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
                <Stop offset="0%" stopColor="#94a3b8" stopOpacity="1" />
                <Stop offset="100%" stopColor="#475569" stopOpacity="1" />
              </RadialGradient>
              
              <LinearGradient id="engineGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <Stop offset="0%" stopColor="#475569" stopOpacity="1" />
                <Stop offset="100%" stopColor="#1e293b" stopOpacity="1" />
              </LinearGradient>
            </Defs>

            <Ellipse cx="250" cy="245" rx="180" ry="15" fill="#0f172a" opacity="0.4" />

            <G transform="translate(50, 50)">
              {/* Swing Arm */}
              <Path d="M 200,180 Q 250,200 350,180 L 360,160 L 340,160 Q 250,180 200,160 Z" fill="#64748b" />

              {/* Rear Wheel */}
              <G transform="translate(320, 160)">
                <Circle r="55" fill="#1e293b" />
                <Circle r="35" fill="url(#motoRimGrad)" stroke="#cbd5e1" strokeWidth="2" />
                <Circle r="15" fill="none" stroke="#cbd5e1" strokeWidth="3" strokeDasharray="5,5"/>
                <Circle r="8" fill="#1e293b" />
              </G>

              {/* Engine Block */}
              <Path d="M 160,110 L 280,120 L 260,180 L 180,170 Z" fill="url(#engineGrad)" stroke="#334155" />

              {/* Body/Fuel Tank */}
              <Path d="M 340,110 Q 360,100 380,105 L 320,160 L 260,150 L 180,180 L 110,160 L 130,80 Q 140,60 180,65 L 240,70 Q 280,60 300,100 L 340,110 Z" 
                    fill="url(#motoBodyGrad)" stroke="#94a3b8" strokeWidth="1"/>

              {/* Seat */}
              <Path d="M 290,95 Q 310,105 340,110 L 350,100 Q 320,90 295,90 Z" fill="#334155" />

              {/* Windshield */}
              <Path d="M 135,75 Q 150,30 190,45 L 180,65 Z" fill="url(#motoWindGrad)" stroke="#94a3b8" strokeWidth="1"/>
              
              {/* Handlebars */}
              <Polyline points="170,70 190,60 210,65" fill="none" stroke="#334155" strokeWidth="3" strokeLinecap="round"/>

              {/* Front Wheel and Fork */}
              <G transform="translate(110, 160)">
                <Circle r="55" fill="#1e293b" />
                <Circle r="35" fill="url(#motoRimGrad)" stroke="#cbd5e1" strokeWidth="2" />
                <Circle r="20" fill="none" stroke="#cbd5e1" strokeWidth="3" strokeDasharray="5,5"/>
                <Circle r="8" fill="#1e293b" />
                <Rect x="-5" y="-60" width="10" height="60" fill="#cbd5e1" />
              </G>

              {/* Headlight */}
              <Ellipse cx="145" cy="68" rx="8" ry="5" fill="#38bdf8" transform="rotate(-20 145 68)"/>
              
              {/* Taillight */}
              <Ellipse cx="375" cy="105" rx="5" ry="8" fill="#ef4444" transform="rotate(-30 375 105)"/>

              {/* Interactive Component Areas */}
              {Object.entries(componentAreas).map(([name, area]) => (
                <G key={name}>
                  <Rect
                    x={area.x}
                    y={area.y}
                    width={area.width}
                    height={area.height}
                    fill={getComponentColor(name)}
                    opacity={getComponentOpacity(name)}
                    stroke={hoveredComponent === name ? 'white' : 'transparent'}
                    strokeWidth="3"
                    rx="6"
                    onPress={() => setSelectedComponent(selectedComponent === name ? null : name)}
                  />
                </G>
              ))}
            </G>
          </Svg>
        </ScrollView>

        {/* Legend */}
        <View style={styles.legend}>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#22c55e' }]} />
            <Text style={styles.legendText}>Healthy</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#f59e0b' }]} />
            <Text style={styles.legendText}>Warning</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#ef4444' }]} />
            <Text style={styles.legendText}>Critical</Text>
          </View>
        </View>
      </View>

      {/* Component Details */}
      <ScrollView style={styles.componentList}>
        <Text style={styles.sectionTitle}>Component Health Status</Text>
        {vehicleData?.components && Object.entries(vehicleData.components).map(([name, component]) => (
          <TouchableOpacity
            key={name}
            style={[
              styles.componentCard,
              {
                backgroundColor: 
                  component.status === 'critical' ? '#7f1d1d' :
                  component.status === 'warning' ? '#78350f' :
                  '#14532d',
                borderColor: 
                  component.status === 'critical' ? '#ef4444' :
                  component.status === 'warning' ? '#f59e0b' :
                  '#22c55e'
              }
            ]}
            onPress={() => setSelectedComponent(selectedComponent === name ? null : name)}
          >
            <View style={styles.componentHeader}>
              <Text style={styles.componentName}>
                {getStatusIcon(component.status)} {name.replace(/_/g, ' ').toUpperCase()}
              </Text>
              <Text style={styles.componentHealth}>{component.health}%</Text>
            </View>
            <Text style={styles.componentStatus}>{component.status.toUpperCase()}</Text>
            
            {component.issues && component.issues.length > 0 && (
              <View style={styles.issuesContainer}>
                <Text style={styles.issuesCount}>
                  ⚠️ {component.issues.length} Issue{component.issues.length > 1 ? 's' : ''} Detected
                </Text>
                {selectedComponent === name && component.issues.map((issue, idx) => (
                  <View key={idx} style={styles.issueCard}>
                    <Text style={styles.issueText}>
                      <Text style={styles.issueLabel}>Probability:</Text> {issue.probability}
                    </Text>
                    <Text style={styles.issueText}>
                      <Text style={styles.issueLabel}>Days to Failure:</Text> ~{issue.estimated_days}
                    </Text>
                    <Text style={styles.issueText}>
                      <Text style={styles.issueLabel}>Severity:</Text> {issue.severity}
                    </Text>
                  </View>
                ))}
              </View>
            )}
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  header: {
    backgroundColor: '#1e293b',
    padding: 20,
    borderBottomWidth: 2,
    borderBottomColor: '#dc2626',
  },
  vehicleTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  vehicleInfo: {
    fontSize: 14,
    color: '#94a3b8',
    marginBottom: 4,
  },
  healthCard: {
    margin: 16,
    padding: 20,
    borderRadius: 12,
    borderWidth: 2,
  },
  healthHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  healthStatus: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  healthScore: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
  },
  healthStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  statLabel: {
    fontSize: 12,
    color: '#cbd5e1',
    marginTop: 4,
  },
  visualizationContainer: {
    backgroundColor: '#1e293b',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#334155',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#94a3b8',
    marginBottom: 16,
  },
  svgScroll: {
    marginBottom: 16,
  },
  legend: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 16,
    marginTop: 8,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 8,
  },
  legendColor: {
    width: 20,
    height: 20,
    borderRadius: 3,
    marginRight: 6,
    opacity: 0.7,
  },
  legendText: {
    fontSize: 12,
    color: '#94a3b8',
  },
  componentList: {
    padding: 16,
  },
  componentCard: {
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    marginBottom: 12,
  },
  componentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  componentName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  componentHealth: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  componentStatus: {
    fontSize: 12,
    color: '#cbd5e1',
    marginBottom: 8,
  },
  issuesContainer: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.1)',
  },
  issuesCount: {
    fontSize: 14,
    color: '#fca5a5',
    fontWeight: '600',
    marginBottom: 8,
  },
  issueCard: {
    backgroundColor: 'rgba(0,0,0,0.2)',
    padding: 12,
    borderRadius: 6,
    marginTop: 8,
  },
  issueText: {
    fontSize: 13,
    color: '#e2e8f0',
    marginBottom: 4,
  },
  issueLabel: {
    fontWeight: 'bold',
  },
});

export default MotorcycleVisualization;
