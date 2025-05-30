# 🤖 GridSight ML Orchestrator

## Overview

The ML Orchestrator is an Azure Function that automatically trains machine learning models on your IESO energy data and generates predictions. It runs daily and saves results to Azure blob storage for consumption by dashboards and applications.

## 🏗️ Architecture

```
Azure Blob Storage (cleaned-data)
        ↓
Azure Function (ML Orchestrator)
   ├── Demand Forecasting Model (XGBoost)
   ├── Grid Stress Detection Model (Random Forest)
   └── 24-hour Predictions Generator
        ↓
Azure Blob Storage (ml-outputs)
        ↓
Streamlit Dashboard (Git-deployed)
```

## 🤖 Models Implemented

### 1. Demand Forecasting Model
- **Algorithm**: XGBoost Regressor
- **Features**: Time-based (hour, day of week, month) + lag features (1h, 24h, 7d)
- **Target**: Ontario electricity demand 24 hours ahead
- **Output**: 288 predictions (5-minute intervals for 24 hours)
- **Performance Metric**: Mean Absolute Error (MAE)

### 2. Grid Stress Detection Model  
- **Algorithm**: Random Forest Classifier
- **Features**: Generation/demand ratio, reserve margin, time features
- **Target**: Binary classification of grid stress (reserve margin < 10%)
- **Output**: Real-time grid reliability status
- **Performance Metric**: Classification accuracy

## 📁 File Structure

```
data_orchestrator/
├── function_app.py          # Main Azure Function with ML pipeline
├── requirements.txt         # Pinned dependencies
├── host.json               # Azure Functions configuration
├── local_test.py           # Local testing script
├── deploy.py               # Automated deployment script
└── README.md               # This file
```

## 🔧 Key Features

### ✅ Bulletproof Design
- **No config.py imports**: Uses environment variables only
- **Proper package structure**: All modules in same directory
- **Pinned dependencies**: Explicit version requirements
- **Error handling**: Comprehensive logging and fallbacks
- **Local testing**: Validate before Azure deployment

### ✅ Production Ready
- **Timer trigger**: Runs daily at 2 PM EST
- **Health endpoint**: `/api/health` for monitoring
- **Manual trigger**: `/api/trigger_ml` for testing
- **Blob integration**: Reads from cleaned-data, writes to ml-outputs
- **Performance tracking**: Model metrics saved with predictions

## 🚀 Quick Start

### Prerequisites
1. **Azure CLI**: [Install](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Azure Functions Core Tools**: `npm install -g azure-functions-core-tools@4 --unsafe-perm true`
3. **Python 3.11**: With pandas, scikit-learn, xgboost

### Local Testing
```bash
cd data_orchestrator
pip install -r requirements.txt
python local_test.py
```

Expected output:
```
✅ Azure Connection test PASSED
✅ Data Loading test PASSED  
✅ Model Training test PASSED
✅ Blob Save test PASSED
🎉 ALL TESTS PASSED - Ready for Azure deployment!
```

### Deploy to Azure
```bash
python deploy.py
```

The script will:
1. Check prerequisites
2. Login to Azure
3. Create Function App
4. Configure environment variables
5. Deploy code
6. Test health endpoint

## 📊 Model Output

### Predictions JSON Structure
```json
{
  "forecast_24h": [
    {
      "timestamp": "2025-05-30T15:05:00",
      "predicted_demand": 18456.23
    },
    // ... 287 more 5-minute predictions
  ],
  "model_performance": {
    "demand_mae": 234.56,
    "stress_accuracy": 0.934
  },
  "generated_at": "2025-05-30T14:00:00"
}
```

### Blob Storage Output
- `ml-outputs/demand_forecaster.pkl`: Trained demand model
- `ml-outputs/stress_detector.pkl`: Trained stress detection model  
- `ml-outputs/latest_predictions.json`: 24-hour forecasts
- `ml-outputs/model_summary.json`: Training metrics and metadata

## 🔍 Monitoring

### Azure Portal
1. Navigate to Function App: `ml-orchestrator-gridsight`
2. Check **Functions** → **ml_orchestrator_timer**
3. View **Monitor** tab for execution history
4. Check **Application Insights** for detailed logs

### Health Check
```bash
curl https://ml-orchestrator-gridsight.azurewebsites.net/api/health
# Expected: "ML Orchestrator is healthy"
```

### Manual Trigger
```bash
# Get function key from Azure Portal
curl -X POST "https://ml-orchestrator-gridsight.azurewebsites.net/api/trigger_ml?code=YOUR_FUNCTION_KEY"
```

## 🧪 Testing Strategy

### Local Testing (`local_test.py`)
- **Azure Connection**: Verify blob storage access
- **Data Loading**: Test reading cleaned datasets
- **Model Training**: Full ML pipeline execution
- **Blob Save**: Test saving results

### Deployment Testing (`deploy.py`)
- **Prerequisites**: Check required tools
- **Azure Resources**: Create/configure Function App
- **Code Deployment**: Upload and validate
- **Health Check**: Verify endpoints

## 🛡️ Security

### Environment Variables
- `AZURE_STORAGE_ACCOUNT_NAME`: Your storage account name
- `AZURE_STORAGE_ACCOUNT_KEY`: Storage account access key

### Access Control
- Health endpoint: Public (anonymous)
- Manual trigger: Function-level auth required
- Timer trigger: Automatic, no external access

## 📈 Performance

### Resource Usage
- **Memory**: ~500MB during model training
- **CPU**: 1-2 minutes execution time
- **Storage**: <1MB model files, <100KB predictions

### Scaling
- **Consumption Plan**: Auto-scales based on demand
- **Timeout**: 10 minutes (configurable in host.json)
- **Concurrency**: Single instance (timer-triggered)

## 🔧 Troubleshooting

### Common Issues

**"Module not found" errors**
- Solution: All dependencies in requirements.txt, no relative imports

**"Blob not found" errors**  
- Check: Container names and file paths in Azure Storage
- Verify: cleaned-data container has latest CSV files

**"Model training failed"**
- Check: Data quality and column names
- Verify: Sufficient data (5 months for good results)

**"Deployment failed"**
- Ensure: Azure CLI logged in
- Check: Function App name is globally unique
- Verify: Resource group exists

### Debug Mode
Add to function_app.py for more verbose logging:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 🚀 Next Steps

1. **Dashboard Integration**: Build Streamlit app to consume predictions
2. **Alert System**: Email notifications for grid stress events
3. **Model Improvements**: Add weather data, more sophisticated features
4. **API Layer**: REST endpoints for external consumption
5. **Data Validation**: Automated data quality checks

## 📄 License

Part of the GridSight project - Educational use for Ontario energy market analysis.

---

**Built with ❤️ for Ontario's Energy Future** 