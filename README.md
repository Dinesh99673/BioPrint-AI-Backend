# 🧠 Blood Group Prediction API - BioPrint AI Backend

FastAPI backend service for predicting blood group from fingerprint images using deep learning models (VGG16 & MobileNetV2). Integrated with R307s fingerprint scanner hardware and email/OTP services for the BioPrint AI healthcare management system.

## 🚀 Features

- 🔍 **AI Blood Group Prediction**: Predicts 8 blood groups (A+, A-, B+, B-, AB+, AB-, O+, O-) from fingerprint images
- 📊 **Dual Model Validation**: Uses VGG16 (94.2% accuracy) and MobileNetV2 (91.8% accuracy) for reliable predictions
- 🔐 **Fingerprint Scanner Integration**: Direct capture from R307s sensor module
- 📧 **Email Service**: Automated email notifications for hospital registrations and OTP delivery
- 🔑 **OTP Management**: Secure OTP generation and verification system
- 🌐 **RESTful API**: Clean API endpoints with automatic OpenAPI documentation

## 🧠 Models Used

| Model         | Architecture    | Accuracy | Input Size |
|---------------|----------------|----------|------------|
| VGG16         | Deep CNN        | 94.2%    | 128x128    |
| MobileNetV2   | Lightweight CNN | 91.8%    | 128x128    |


> ⚠️ **Important Disclaimer**: This AI system is currently in the **training and development phase**. The blood group predictions provided are **experimental and should not be used as the sole basis for medical decisions**. Always verify results with standard laboratory testing methods. The accuracy rates mentioned are based on limited training data and may vary in real-world scenarios. This system is intended for research and educational purposes only.

## 📁 Project Structure

```
predicting_blood_group_using_fingerprints/
├── app.py                    # FastAPI application with all endpoints
├── fingerprint-scanner.py  # R307s sensor integration
├── VGG16.h5                  # Trained VGG16 model
├── MobileNetV2.h5            # Trained MobileNetV2 model
├── requirements.txt          # Python dependencies
├── API_DOCUMENTATION.md      # Detailed API documentation
└── Sample dataset/           # Test fingerprint images
```

## 🛠 Installation & Setup

### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/Dinesh99673/BioPrint-AI-Backend.git
cd predicting_blood_group_using_fingerprints

# OR if you already have the project, navigate to the directory
cd predicting_blood_group_using_fingerprints
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

Update email credentials in `app.py`:
- `SMTP_USERNAME`: Your Gmail address
- `SMTP_PASSWORD`: Gmail app password

### 5. Run Server

```bash
python app.py
# OR
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Server runs at: `http://localhost:8000`

## 📡 API Endpoints

- `POST /predict` - Predict blood group from uploaded image
- `POST /capture-and-predict` - Capture from R307s scanner and predict
- `POST /send-email` - Send email notifications
- `POST /send-otp` - Generate and send OTP
- `POST /verify-otp` - Verify OTP
- `POST /enroll-fingerprint` - Enroll fingerprint in R307s module
- `POST /search-fingerprint` - Search fingerprint in database
- `GET /health` - Health check with system status

## 🔗 Integration

This backend integrates with the **BioPrint-AI** React frontend:
- Hospital registration and management
- Patient data access with OTP verification
- Real-time blood group detection
- Fingerprint-based patient search

## 📊 Response Format

```json
{
  "success": true,
  "predictions": {
    "vgg16": {
      "blood_group": "A+",
      "confidence": 87.45,
      "model": "VGG16"
    },
    "mobilenetv2": {
      "blood_group": "A+",
      "confidence": 82.31,
      "model": "MobileNetV2"
    },
    "agreement": "✅ Both models agree!",
    "final_prediction": "A+"
  }
}
```

## 🔧 Technology Stack

- **FastAPI** 0.104.1 - High-performance web framework
- **TensorFlow** 2.20.0 - Deep learning framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **PyFingerprint** - R307s sensor library

## 📝 Documentation

- API Documentation: `API_DOCUMENTATION.md`
- Interactive docs: `http://localhost:8000/docs` (Swagger UI)
- Alternative docs: `http://localhost:8000/redoc`

## ⚠️ Hardware Requirements

For fingerprint scanner functionality:
- R307s fingerprint sensor module
- USB connection (COM7 default, configurable)
- PyFingerprint library installed


