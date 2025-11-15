"""
AI/ML services for health analysis and predictions.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import HealthRecord
from .models import HealthInsight, HealthTrend, HealthRisk

User = get_user_model()


class HealthAnalyzer:
    """Analyze health records and generate insights."""
    
    # Normal ranges for common health metrics
    NORMAL_RANGES = {
        'HbA1c': (4.0, 5.6),  # Percentage
        'Fasting Blood Sugar': (70, 100),  # mg/dL
        'Blood Pressure Systolic': (90, 120),  # mmHg
        'Blood Pressure Diastolic': (60, 80),  # mmHg
        'Total Cholesterol': (0, 200),  # mg/dL
        'HDL Cholesterol': (40, None),  # mg/dL (higher is better)
        'LDL Cholesterol': (0, 100),  # mg/dL
        'Triglycerides': (0, 150),  # mg/dL
        'Hemoglobin': (12, 17.5),  # g/dL (varies by gender)
        'WBC Count': (4000, 11000),  # /cumm
        'Platelet Count': (150000, 450000),  # /cumm
        'Creatinine': (0.6, 1.2),  # mg/dL
        'ALT': (7, 56),  # U/L
        'AST': (10, 40),  # U/L
    }
    
    def __init__(self, patient):
        self.patient = patient
        self.records = HealthRecord.objects.filter(
            patient=patient,
            status=HealthRecord.RecordStatus.PROCESSED
        ).order_by('record_date')
    
    def analyze_trends(self, metric_name=None):
        """Analyze trends for specific metric or all metrics."""
        trends = []
        
        # Extract metrics from records
        metrics_data = self._extract_metrics_from_records()
        
        if metric_name:
            if metric_name in metrics_data:
                trend = self._calculate_trend(metric_name, metrics_data[metric_name])
                if trend:
                    trends.append(trend)
        else:
            # Analyze all metrics
            for metric, data_points in metrics_data.items():
                trend = self._calculate_trend(metric, data_points)
                if trend:
                    trends.append(trend)
        
        return trends
    
    def _extract_metrics_from_records(self):
        """Extract metric values from health records."""
        metrics = {}
        
        for record in self.records:
            if record.extracted_values:
                for metric_name, value in record.extracted_values.items():
                    if isinstance(value, (int, float)):
                        if metric_name not in metrics:
                            metrics[metric_name] = []
                        metrics[metric_name].append({
                            'date': record.record_date,
                            'value': float(value),
                            'record_id': record.id
                        })
        
        return metrics
    
    def _calculate_trend(self, metric_name, data_points):
        """Calculate trend for a metric."""
        if len(data_points) < 2:
            return None
        
        # Sort by date
        data_points = sorted(data_points, key=lambda x: x['date'])
        
        # Extract values and dates
        values = [dp['value'] for dp in data_points]
        dates = [dp['date'] for dp in data_points]
        
        # Calculate statistics
        current_value = values[-1]
        average_value = np.mean(values)
        min_value = np.min(values)
        max_value = np.max(values)
        
        # Calculate trend direction and strength using linear regression
        x = np.arange(len(values))
        if len(values) > 1:
            slope = np.polyfit(x, values, 1)[0]
            trend_strength = slope / (max(values) - min(values) + 1e-10)  # Normalized
            
            if trend_strength > 0.05:
                trend_direction = 'INCREASING'
            elif trend_strength < -0.05:
                trend_direction = 'DECREASING'
            else:
                trend_direction = 'STABLE'
        else:
            trend_direction = 'STABLE'
            trend_strength = 0.0
        
        # Calculate percentage change
        if len(values) >= 2:
            change_percentage = ((values[-1] - values[0]) / values[0]) * 100
        else:
            change_percentage = 0.0
        
        # Get normal range
        normal_range = self.NORMAL_RANGES.get(metric_name, (None, None))
        
        # Update or create trend
        trend, created = HealthTrend.objects.update_or_create(
            patient=self.patient,
            metric_name=metric_name,
            defaults={
                'data_points': data_points,
                'trend_direction': trend_direction,
                'trend_strength': float(trend_strength),
                'current_value': float(current_value),
                'average_value': float(average_value),
                'min_value': float(min_value),
                'max_value': float(max_value),
                'change_percentage': float(change_percentage),
                'normal_range_min': normal_range[0],
                'normal_range_max': normal_range[1],
            }
        )
        
        return trend
    
    def detect_anomalies(self):
        """Detect anomalies in health records."""
        anomalies = []
        metrics_data = self._extract_metrics_from_records()
        
        for metric_name, data_points in metrics_data.items():
            if len(data_points) < 2:
                continue
            
            values = [dp['value'] for dp in data_points]
            mean = np.mean(values)
            std = np.std(values)
            
            # Detect outliers (values beyond 2 standard deviations)
            for dp in data_points:
                z_score = abs((dp['value'] - mean) / (std + 1e-10))
                if z_score > 2:
                    # Check against normal range
                    normal_range = self.NORMAL_RANGES.get(metric_name, (None, None))
                    is_outside_normal = False
                    
                    if normal_range[0] is not None and dp['value'] < normal_range[0]:
                        is_outside_normal = True
                    if normal_range[1] is not None and dp['value'] > normal_range[1]:
                        is_outside_normal = True
                    
                    if is_outside_normal:
                        anomalies.append({
                            'metric': metric_name,
                            'value': dp['value'],
                            'date': dp['date'],
                            'record_id': dp['record_id'],
                            'z_score': z_score,
                            'normal_range': normal_range
                        })
        
        return anomalies
    
    def assess_health_risks(self):
        """Assess health risks based on records."""
        risks = []
        metrics_data = self._extract_metrics_from_records()
        
        # Diabetes risk assessment
        diabetes_risk = self._assess_diabetes_risk(metrics_data)
        if diabetes_risk:
            risks.append(diabetes_risk)
        
        # Hypertension risk assessment
        hypertension_risk = self._assess_hypertension_risk(metrics_data)
        if hypertension_risk:
            risks.append(hypertension_risk)
        
        # Heart disease risk assessment
        heart_risk = self._assess_heart_disease_risk(metrics_data)
        if heart_risk:
            risks.append(heart_risk)
        
        return risks
    
    def _assess_diabetes_risk(self, metrics_data):
        """Assess diabetes risk based on blood sugar and HbA1c."""
        risk_factors = []
        risk_score = 0.0
        
        # Check HbA1c
        if 'HbA1c' in metrics_data:
            hba1c_values = [dp['value'] for dp in metrics_data['HbA1c']]
            latest_hba1c = hba1c_values[-1]
            
            if latest_hba1c >= 6.5:
                risk_score += 80
                risk_factors.append(f'HbA1c level ({latest_hba1c}%) indicates diabetes')
            elif latest_hba1c >= 5.7:
                risk_score += 50
                risk_factors.append(f'HbA1c level ({latest_hba1c}%) indicates pre-diabetes')
        
        # Check fasting blood sugar
        if 'Fasting Blood Sugar' in metrics_data:
            fbs_values = [dp['value'] for dp in metrics_data['Fasting Blood Sugar']]
            latest_fbs = fbs_values[-1]
            
            if latest_fbs >= 126:
                risk_score += 70
                risk_factors.append(f'Fasting blood sugar ({latest_fbs} mg/dL) indicates diabetes')
            elif latest_fbs >= 100:
                risk_score += 40
                risk_factors.append(f'Fasting blood sugar ({latest_fbs} mg/dL) is elevated')
        
        if risk_score > 0:
            risk_level = 'LOW' if risk_score < 30 else ('MODERATE' if risk_score < 60 else ('HIGH' if risk_score < 80 else 'CRITICAL'))
            
            recommendations = []
            if risk_score >= 60:
                recommendations.append('Consult a diabetologist for further evaluation')
                recommendations.append('Monitor blood sugar levels regularly')
            if risk_score >= 40:
                recommendations.append('Follow a diabetic-friendly diet')
                recommendations.append('Maintain regular exercise routine')
            
            risk, created = HealthRisk.objects.update_or_create(
                patient=self.patient,
                category=HealthRisk.RiskCategory.DIABETES,
                defaults={
                    'risk_score': min(risk_score, 100),
                    'risk_level': risk_level,
                    'description': f'Diabetes risk assessment based on blood sugar levels and HbA1c',
                    'contributing_factors': risk_factors,
                    'recommendations': recommendations,
                }
            )
            return risk
        
        return None
    
    def _assess_hypertension_risk(self, metrics_data):
        """Assess hypertension risk based on blood pressure."""
        risk_factors = []
        risk_score = 0.0
        
        systolic_key = 'Blood Pressure Systolic'
        diastolic_key = 'Blood Pressure Diastolic'
        
        if systolic_key in metrics_data or diastolic_key in metrics_data:
            if systolic_key in metrics_data:
                sbp_values = [dp['value'] for dp in metrics_data[systolic_key]]
                latest_sbp = sbp_values[-1]
                
                if latest_sbp >= 180:
                    risk_score += 90
                    risk_factors.append(f'Very high systolic BP ({latest_sbp} mmHg) - Hypertensive Crisis')
                elif latest_sbp >= 140:
                    risk_score += 70
                    risk_factors.append(f'High systolic BP ({latest_sbp} mmHg) - Stage 2 Hypertension')
                elif latest_sbp >= 130:
                    risk_score += 50
                    risk_factors.append(f'Elevated systolic BP ({latest_sbp} mmHg) - Stage 1 Hypertension')
                elif latest_sbp >= 120:
                    risk_score += 30
                    risk_factors.append(f'High-normal systolic BP ({latest_sbp} mmHg)')
            
            if diastolic_key in metrics_data:
                dbp_values = [dp['value'] for dp in metrics_data[diastolic_key]]
                latest_dbp = dbp_values[-1]
                
                if latest_dbp >= 120:
                    risk_score += 90
                    risk_factors.append(f'Very high diastolic BP ({latest_dbp} mmHg) - Hypertensive Crisis')
                elif latest_dbp >= 90:
                    risk_score += 70
                    risk_factors.append(f'High diastolic BP ({latest_dbp} mmHg) - Stage 2 Hypertension')
                elif latest_dbp >= 80:
                    risk_score += 50
                    risk_factors.append(f'Elevated diastolic BP ({latest_dbp} mmHg) - Stage 1 Hypertension')
            
            if risk_score > 0:
                risk_level = 'LOW' if risk_score < 30 else ('MODERATE' if risk_score < 60 else ('HIGH' if risk_score < 80 else 'CRITICAL'))
                
                recommendations = []
                if risk_score >= 60:
                    recommendations.append('Consult a cardiologist for blood pressure management')
                    recommendations.append('Monitor blood pressure daily')
                if risk_score >= 40:
                    recommendations.append('Reduce sodium intake')
                    recommendations.append('Maintain healthy weight')
                    recommendations.append('Regular exercise')
                
                risk, created = HealthRisk.objects.update_or_create(
                    patient=self.patient,
                    category=HealthRisk.RiskCategory.HYPERTENSION,
                    defaults={
                        'risk_score': min(risk_score, 100),
                        'risk_level': risk_level,
                        'description': 'Hypertension risk assessment based on blood pressure readings',
                        'contributing_factors': risk_factors,
                        'recommendations': recommendations,
                    }
                )
                return risk
        
        return None
    
    def _assess_heart_disease_risk(self, metrics_data):
        """Assess heart disease risk based on cholesterol and other factors."""
        risk_factors = []
        risk_score = 0.0
        
        # Check cholesterol levels
        if 'Total Cholesterol' in metrics_data:
            tc_values = [dp['value'] for dp in metrics_data['Total Cholesterol']]
            latest_tc = tc_values[-1]
            
            if latest_tc >= 240:
                risk_score += 60
                risk_factors.append(f'High total cholesterol ({latest_tc} mg/dL)')
            elif latest_tc >= 200:
                risk_score += 40
                risk_factors.append(f'Borderline high total cholesterol ({latest_tc} mg/dL)')
        
        if 'LDL Cholesterol' in metrics_data:
            ldl_values = [dp['value'] for dp in metrics_data['LDL Cholesterol']]
            latest_ldl = ldl_values[-1]
            
            if latest_ldl >= 190:
                risk_score += 70
                risk_factors.append(f'Very high LDL cholesterol ({latest_ldl} mg/dL)')
            elif latest_ldl >= 160:
                risk_score += 50
                risk_factors.append(f'High LDL cholesterol ({latest_ldl} mg/dL)')
            elif latest_ldl >= 130:
                risk_score += 30
                risk_factors.append(f'Borderline high LDL cholesterol ({latest_ldl} mg/dL)')
        
        # Check blood pressure as contributing factor
        if 'Blood Pressure Systolic' in metrics_data:
            sbp_values = [dp['value'] for dp in metrics_data['Blood Pressure Systolic']]
            if sbp_values[-1] >= 140:
                risk_score += 30
                risk_factors.append('High blood pressure increases heart disease risk')
        
        if risk_score > 0:
            risk_level = 'LOW' if risk_score < 30 else ('MODERATE' if risk_score < 60 else ('HIGH' if risk_score < 80 else 'CRITICAL'))
            
            recommendations = []
            if risk_score >= 50:
                recommendations.append('Consult a cardiologist for comprehensive heart health evaluation')
            if risk_score >= 40:
                recommendations.append('Follow heart-healthy diet (low saturated fat)')
                recommendations.append('Maintain healthy weight')
                recommendations.append('Regular physical activity')
            
            risk, created = HealthRisk.objects.update_or_create(
                patient=self.patient,
                category=HealthRisk.RiskCategory.HEART_DISEASE,
                defaults={
                    'risk_score': min(risk_score, 100),
                    'risk_level': risk_level,
                    'description': 'Heart disease risk assessment based on cholesterol and cardiovascular markers',
                    'contributing_factors': risk_factors,
                    'recommendations': recommendations,
                }
            )
            return risk
        
        return None
    
    def generate_insights(self):
        """Generate comprehensive health insights."""
        insights = []
        
        # Analyze trends
        trends = self.analyze_trends()
        
        for trend in trends:
            # Generate trend insights
            insight_data = self._generate_trend_insight(trend)
            if insight_data:
                insight = HealthInsight.objects.create(
                    patient=self.patient,
                    type=HealthInsight.InsightType.TREND,
                    title=insight_data['title'],
                    description=insight_data['description'],
                    severity=insight_data['severity'],
                    metrics={'metric_name': trend.metric_name, 'current_value': trend.current_value},
                    confidence_score=0.8,
                )
                insights.append(insight)
        
        # Detect anomalies
        anomalies = self.detect_anomalies()
        
        for anomaly in anomalies:
            record = HealthRecord.objects.get(id=anomaly['record_id'])
            insight = HealthInsight.objects.create(
                patient=self.patient,
                type=HealthInsight.InsightType.ANOMALY,
                title=f'Anomaly detected in {anomaly["metric"]}',
                description=f'{anomaly["metric"]} value ({anomaly["value"]}) is outside normal range {anomaly["normal_range"]}',
                severity='HIGH' if anomaly['z_score'] > 3 else 'MEDIUM',
                related_records=[record],
                metrics={'metric': anomaly['metric'], 'value': anomaly['value'], 'z_score': anomaly['z_score']},
                confidence_score=min(anomaly['z_score'] / 3, 1.0),
            )
            insights.append(insight)
        
        # Assess risks
        risks = self.assess_health_risks()
        
        for risk in risks:
            insight = HealthInsight.objects.create(
                patient=self.patient,
                type=HealthInsight.InsightType.RISK,
                title=f'{risk.get_category_display()} Risk Assessment',
                description=risk.description,
                severity='CRITICAL' if risk.risk_level == 'CRITICAL' else ('HIGH' if risk.risk_level == 'HIGH' else ('MEDIUM' if risk.risk_level == 'MODERATE' else 'LOW')),
                related_records=list(risk.related_records.all()),
                metrics={'risk_score': risk.risk_score, 'risk_level': risk.risk_level},
                predictions={'risk_category': risk.category},
                recommendations=risk.recommendations,
                confidence_score=risk.risk_score / 100,
            )
            insights.append(insight)
        
        return insights
    
    def _generate_trend_insight(self, trend):
        """Generate insight text for a trend."""
        if trend.trend_direction == 'INCREASING':
            if trend.current_value and trend.normal_range_max and trend.current_value > trend.normal_range_max:
                return {
                    'title': f'{trend.metric_name} is increasing and above normal',
                    'description': f'{trend.metric_name} has been increasing and is currently {trend.current_value}, which is above the normal range ({trend.normal_range_min}-{trend.normal_range_max}). Consider consulting your doctor.',
                    'severity': 'HIGH'
                }
            else:
                return {
                    'title': f'{trend.metric_name} is showing an increasing trend',
                    'description': f'{trend.metric_name} has increased by {trend.change_percentage:.1f}% over the observed period. Current value: {trend.current_value}.',
                    'severity': 'MEDIUM' if trend.change_percentage > 10 else 'LOW'
                }
        elif trend.trend_direction == 'DECREASING':
            if trend.current_value and trend.normal_range_min and trend.current_value < trend.normal_range_min:
                return {
                    'title': f'{trend.metric_name} is decreasing and below normal',
                    'description': f'{trend.metric_name} has been decreasing and is currently {trend.current_value}, which is below the normal range ({trend.normal_range_min}-{trend.normal_range_max}).',
                    'severity': 'HIGH'
                }
            else:
                return {
                    'title': f'{trend.metric_name} is showing a decreasing trend',
                    'description': f'{trend.metric_name} has decreased by {abs(trend.change_percentage):.1f}% over the observed period. Current value: {trend.current_value}.',
                    'severity': 'MEDIUM' if abs(trend.change_percentage) > 10 else 'LOW'
                }
        else:
            return {
                'title': f'{trend.metric_name} is stable',
                'description': f'{trend.metric_name} has remained relatively stable. Current value: {trend.current_value}.',
                'severity': 'LOW'
            }


class PredictiveModel:
    """Predictive model for future health outcomes."""
    
    @staticmethod
    def predict_future_values(patient, metric_name, days_ahead=90):
        """Predict future values for a metric using linear regression."""
        trends = HealthTrend.objects.filter(patient=patient, metric_name=metric_name).first()
        
        if not trends or len(trends.data_points) < 3:
            return None
        
        # Extract data
        data_points = sorted(trends.data_points, key=lambda x: x['date'])
        dates = [dp['date'] for dp in data_points]
        values = [dp['value'] for dp in data_points]
        
        # Convert dates to numeric (days from first date)
        first_date = dates[0]
        x = [(date - first_date).days for date in dates]
        
        # Fit linear regression
        coeffs = np.polyfit(x, values, 1)
        slope = coeffs[0]
        intercept = coeffs[1]
        
        # Predict future values
        last_date = dates[-1]
        predictions = []
        
        for i in range(30, days_ahead + 1, 30):  # Predict every 30 days
            future_date = last_date + timedelta(days=i)
            future_x = (future_date - first_date).days
            predicted_value = slope * future_x + intercept
            
            predictions.append({
                'date': future_date.isoformat(),
                'value': float(predicted_value),
                'days_ahead': i
            })
        
        return predictions

