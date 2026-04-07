# Hypertension Multimodal Risk Prediction Model

A FastAPI-based web service that predicts hypertension risk using clinical data and retinal fundus images through multimodal AI.

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

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Access at `http://localhost:8000`

## Deployment to Render

### Prerequisites

1. **GitHub Repository**: Your code should be pushed to GitHub
2. **Model Files**: Upload your trained model files to a cloud storage service (AWS S3, Google Cloud Storage, etc.) or include them in your deployment

### Step-by-Step Deployment

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

### Troubleshooting

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

## Technologies Used

- **Backend**: FastAPI, Python 3.10
- **AI/ML**: PyTorch, scikit-learn, OpenCV
- **Image Processing**: PIL, torchvision
- **Deployment**: Docker, Render
- **Data Processing**: pandas, numpy

## License

This project is part of a capstone project for academic purposes.