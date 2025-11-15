# AI/ML Module for Reform

This module provides AI-powered health analysis and predictive analytics for the Reform healthcare platform.

## Features

### 1. Health Trend Analysis
- Analyzes trends in health metrics over time
- Tracks changes in key health indicators
- Identifies improving, declining, or stable trends
- Compares values against normal ranges

**Supported Metrics:**
- HbA1c (Diabetes marker)
- Blood Sugar (Fasting)
- Blood Pressure (Systolic/Diastolic)
- Cholesterol (Total, HDL, LDL)
- Triglycerides
- Hemoglobin
- WBC Count
- Platelet Count
- Creatinine
- Liver enzymes (ALT, AST)

### 2. Anomaly Detection
- Detects outliers in health records
- Identifies values outside normal ranges
- Uses statistical methods (z-score) for detection
- Flags potentially concerning values

### 3. Risk Assessment
- **Diabetes Risk**: Based on HbA1c and blood sugar levels
- **Hypertension Risk**: Based on blood pressure readings
- **Heart Disease Risk**: Based on cholesterol and cardiovascular markers

Each risk assessment includes:
- Risk score (0-100)
- Risk level (Low, Moderate, High, Critical)
- Contributing factors
- Recommendations to reduce risk

### 4. Predictive Analytics
- Predicts future health metric values using linear regression
- Provides 30, 60, 90-day projections
- Helps identify potential health issues early

### 5. Health Insights Generation
- Automatically generates comprehensive health insights
- Combines trends, anomalies, and risk assessments
- Provides actionable recommendations
- Confidence scores for each insight

## API Endpoints

### Trends
- `GET /api/v1/ai/trends/` - List all health trends
- `POST /api/v1/ai/trends/analyze/` - Analyze records and generate trends
- `GET /api/v1/ai/trends/{id}/predict/` - Predict future values for a trend

### Risks
- `GET /api/v1/ai/risks/` - List all health risks
- `POST /api/v1/ai/risks/assess/` - Assess health risks

### Insights
- `GET /api/v1/ai/insights/` - List all health insights
- `POST /api/v1/ai/insights/generate/` - Generate comprehensive insights
- `POST /api/v1/ai/insights/detect_anomalies/` - Detect anomalies in records

## Usage Examples

### Generate Insights (Recommended)
```python
# Automatically analyzes all records and generates insights
POST /api/v1/ai/insights/generate/

# Response includes:
# - Trend insights
# - Anomaly detections
# - Risk assessments
# - Recommendations
```

### Analyze Specific Trend
```python
# Analyze a specific metric
POST /api/v1/ai/trends/analyze/
{
    "metric_name": "HbA1c"
}

# Get all trends
GET /api/v1/ai/trends/
```

### Assess Risks
```python
# Assess all health risks
POST /api/v1/ai/risks/assess/

# Get specific risk category
GET /api/v1/ai/risks/?category=DIABETES
```

### Predict Future Values
```python
# Predict future values for a trend
GET /api/v1/ai/trends/{id}/predict/?days_ahead=90

# Returns predictions for 30, 60, 90 days ahead
```

## How It Works

### 1. Data Extraction
The analyzer extracts health metrics from processed health records:
- Reads `extracted_values` JSON field from HealthRecord
- Identifies numeric values for known metrics
- Organizes data by date and metric name

### 2. Trend Calculation
- Uses linear regression to calculate trend direction
- Normalizes trend strength (-1 to 1)
- Calculates statistics (mean, min, max, change %)
- Compares against normal ranges

### 3. Anomaly Detection
- Calculates mean and standard deviation
- Identifies values beyond 2 standard deviations (z-score > 2)
- Checks against clinical normal ranges
- Flags potentially concerning values

### 4. Risk Assessment
Uses clinical guidelines and thresholds:
- **Diabetes**: HbA1c ≥6.5% or FBS ≥126 mg/dL
- **Hypertension**: SBP ≥140 or DBP ≥90 mmHg
- **Heart Disease**: High cholesterol markers

### 5. Prediction
- Uses linear regression on historical data
- Projects future values based on trend
- Provides 30, 60, 90-day predictions

## Dependencies

- `numpy` - Numerical computations
- `pandas` - Data manipulation (optional, for future enhancements)

## Future Enhancements

- Machine learning models for better predictions
- Integration with external health data sources
- Personalized health recommendations
- Medication adherence tracking
- Lifestyle factor analysis
- Integration with wearables

## Notes

- Requires processed health records with `extracted_values` populated
- Normal ranges are based on standard clinical guidelines
- Risk assessments should not replace professional medical advice
- Predictions are based on historical trends and may not account for external factors

