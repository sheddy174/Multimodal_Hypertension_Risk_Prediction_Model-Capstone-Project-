# Hypertension Multimodal Risk Prediction Model

**GitHub Repository**: https://github.com/sheddy174/Multimodal_Hypertension_Risk_Prediction_Model-Capstone-Project-

A FastAPI-based web service that predicts hypertension risk using clinical data and retinal fundus images through multimodal AI. This system implements a state-of-the-art machine learning solution that combines clinical parameters with retinal fundus image analysis to provide accurate hypertension risk predictions.

## Features

- **Clinical Prediction**: Uses Framingham Risk Score with additional clinical features
- **Retinal Analysis**: Deep learning model (ResNet-50) analyzes fundus images for hypertension indicators
- **Late Fusion**: Combines both modalities for improved prediction accuracy
- **Web API**: RESTful API built with FastAPI
- **Docker Support**: Containerized deployment

## API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health check
- `POST /predict` - Make prediction with clinical data and fundus image

### Prediction Request Format

```bash
POST /predict
Content-Type: multipart/form-data

Form Data:
- age: float (required)
- bmi: float (required)
- systolic_bp: float (required)
- diastolic_bp: float (required)
- glucose: float (required)
- fundus_image: file (required, PNG/JPG fundus image)

Optional fields (with defaults):
- sex: int (0=Female, 1=Male, default=0)
- currentSmoker: int (0=No, 1=Yes, default=0)
- cigsPerDay: int (default=0)
- diabetes: int (0=No, 1=Yes, default=0)
- totChol: float (default=200.0)
- heartRate: int (default=75)
- BPMeds: int (0=No, 1=Yes, default=0)
```

### Response Format

```json
{
  "clinical_probability": 0.2345,
  "retinal_probability": 0.6789,
  "fused_probability": 0.4567,
  "risk_level": "Medium"
}
```

## System Requirements

- **Python**: 3.10 or higher
- **RAM**: Minimum 4GB (8GB recommended for model inference)
- **Storage**: At least 2GB for models and dependencies
- **GPU**: Optional (CUDA 11.8+ for faster inference)
- **OS**: Windows, macOS, or Linux

## Installation & Setup

### Prerequisites
- Python 3.10+
- pip or conda package manager
- Git

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sheddy174/Multimodal_Hypertension_Risk_Prediction_Model-Capstone-Project-
   cd hypertension_multimodal
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure model files are in place**:
   ```bash
   # Place your trained model files in:
   models/best_fundus_htr_model.pth
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Access the application**:
   - API Documentation: `http://localhost:8000/docs`
   - Web Interface: `http://localhost:8000`
   - Health Check: `http://localhost:8000/health`

## Deployment

### Docker Deployment (Local)

1. **Build Docker image**:
   ```bash
   docker build -t hypertension-multimodal:latest .
   ```

2. **Run Docker container**:
   ```bash
   docker run -p 8000:8000 hypertension-multimodal:latest
   ```

3. **Access the application**:
   - API: `http://localhost:8000`
   - Swagger docs: `http://localhost:8000/docs`

### Deployment to Render (Production)

#### Prerequisites

1. **GitHub Repository**: Your code should be pushed to GitHub
2. **Model Files**: Upload your trained model files to a cloud storage service (AWS S3, Google Cloud Storage, etc.) or include them in your deployment

#### Step-by-Step Deployment

1. **Sign up/Login to Render**: Go to [render.com](https://render.com) and create an account

2. **Connect GitHub Repository**:
   - Click "New" → "Web Service"
   - Connect your GitHub account
   - Select your repository: `Multimodal_Hypertension_Risk_Prediction_Model-Capstone-Project-`

3. **Configure Deployment**:
   - **Name**: `hypertension-multimodal-api`
   - **Runtime**: `Docker`
   - **Build Command**: Leave default (will use Dockerfile)
   - **Start Command**: `python app.py`

4. **Environment Variables**:
   - The app automatically uses Render's `PORT` environment variable
   - No additional environment variables needed for basic deployment

5. **Upload Model Files**:
   Since model files are excluded from Git, you have two options:

   **Option A: Use Render Disk (Recommended for small models)**
   - In Render dashboard, go to your service → "Settings" → "Disk"
   - Create a disk with path `/app/models` and sufficient size
   - Upload your `best_fundus_htr_model.pth` file to the disk

   **Option B: Use Cloud Storage**
   - Upload model to AWS S3, Google Cloud Storage, or similar
   - Add environment variables for credentials
   - Modify the code to download models at startup

6. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment to complete (may take 10-15 minutes for first build)

#### Troubleshooting Deployment

**Build Failures**:
- Check the build logs in Render dashboard
- Ensure all dependencies are listed in `requirements.txt`
- Verify Dockerfile is correct

**Model Loading Errors**:
- Ensure model files are accessible at runtime
- Check file paths in the code
- Verify model file format and compatibility

**Port Issues**:
- The app automatically uses Render's PORT environment variable
- Default port is 10000 as configured in Dockerfile

## Project Structure

```
hypertension_multimodal/
├── app.py                    # Main FastAPI application
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── render.yaml             # Render deployment config
├── .gitignore              # Git ignore rules
├── models/                 # Model files (excluded from git)
│   └── best_fundus_htr_model.pth
├── model_architectures/    # Model definitions
├── services/               # Prediction services
├── utils/                  # Utility functions
└── frontend/               # Static web interface
```

## Project Structure

```
hypertension_multimodal/
├── app.py                          # Main FastAPI application
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── render.yaml                     # Render deployment config
├── README.md                       # This file (documentation)
├── .gitignore                      # Git ignore rules
│
├── models/                         # Pre-trained model files
│   ├── best_fundus_htr_model.pth  # Trained fundus model
│   ├── fusion_model.py             # Fusion model implementation
│   └── __pycache__/
│
├── model_architectures/            # Model definitions and architectures
│   ├── __init__.py
│   ├── fundus_model.py             # Fundus/retinal image model
│   └── __pycache__/
│
├── services/                       # Prediction service modules
│   ├── __init__.py
│   ├── clinical_predict.py         # Clinical risk prediction
│   ├── retinal_predict.py          # Retinal image analysis
│   ├── fusion_predict.py           # Multimodal fusion logic
│   ├── risk_breakdown.py           # Risk factor breakdown
│   ├── model_downloader.py         # Model downloading utilities
│   └── __pycache__/
│
├── utils/                          # Utility functions
│   ├── __init__.py
│   ├── clinical_predict.py         # Clinical utilities
│   ├── retinal_predict.py          # Retinal image utilities
│   ├── fusion.py                   # Fusion utilities
│   └── __pycache__/
│
└── frontend/                       # Web interface
    ├── index.html                  # Home page
    ├── predict.html                # Prediction interface
    ├── risk-breakdown.html         # Risk breakdown visualization
    ├── about.html                  # Project information
    ├── contact.html                # Contact information
    ├── css/
    │   ├── index.css
    │   ├── predict.css
    │   ├── about.css
    │   ├── contact.css
    │   └── breakdown.css
    └── js/
        ├── config.js               # JavaScript configuration
        ├── app.js                  # Main app logic
        ├── predict.js              # Prediction logic
        └── breakdown.js            # Risk breakdown logic
```

## Technologies Used

- **Backend**: FastAPI, Python 3.10+
- **AI/ML**: PyTorch, scikit-learn, OpenCV
- **Image Processing**: PIL, torchvision
- **Deployment**: Docker, Render
- **Data Processing**: pandas, numpy
- **Frontend**: HTML5, CSS3, JavaScript
- **APIs**: RESTful API with FastAPI

## Model Information

### Clinical Model
- **Type**: Logistic Regression / Gradient Boosting
- **Features**: Age, BMI, systolic/diastolic BP, glucose, cholesterol, smoking status, diabetes status, heart rate, BP medication use
- **Training Data**: Framingham Heart Study dataset

### Retinal Model
- **Type**: ResNet-50 (Fine-tuned Deep Neural Network)
- **Input**: Fundus images (2D retinal photographs)
- **Output**: Probability of hypertension-related retinal damage
- **Architecture**: Transfer learning from ImageNet pre-training

### Fusion Model
- **Type**: Weighted averaging / Neural network fusion
- **Input**: Clinical probability + Retinal probability
- **Output**: Final risk prediction and risk level classification
- **Risk Levels**: Low, Medium, High, Very High

## Common Issues & Troubleshooting

| Issue | Solution |
|-------|----------|
| Model file not found | Ensure `models/best_fundus_htr_model.pth` exists in the correct location |
| Image upload fails | Verify image is in PNG or JPG format, less than 10MB |
| Port already in use | Change port or kill process using the port |
| CUDA/GPU errors | Install compatible PyTorch version or use CPU mode |
| Import errors | Reinstall dependencies: `pip install -r requirements.txt --force-reinstall` |

## Contributing

This is a capstone project. For improvements or bug reports, please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## Project Documentation

For detailed information about:
- **Model Training**: See `model_architectures/` and `models/` directories
- **API Specifications**: Visit `/docs` endpoint when running the application
- **Frontend Implementation**: Check `frontend/js/` for interactive features
- **Deployment Configuration**: Refer to `Dockerfile` and `render.yaml`

## License

This project is part of a capstone project for academic purposes at Ashesi University.

## Support & Contact

For questions, bug reports, or suggestions:
- **GitHub Issues**: [Project Issues](https://github.com/sheddy174/Multimodal_Hypertension_Risk_Prediction_Model-Capstone-Project-/issues)
- **Repository**: [Multimodal Hypertension Risk Prediction](https://github.com/sheddy174/Multimodal_Hypertension_Risk_Prediction_Model-Capstone-Project-)

---

**Last Updated**: May 2026
**Version**: 1.0.0