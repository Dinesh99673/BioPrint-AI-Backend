# Blood Group Prediction from Fingerprints - Project Summary

## 🎯 Project Overview
This is a machine learning project that predicts a person's blood group (A+, A-, B+, B-, AB+, AB-, O+, O-) from fingerprint images using two different deep learning models: VGG16 and MobileNetV2.

## 🏗️ Architecture & Components

### 1. **Core Models**
- **VGG16**: A deep convolutional neural network with 16 layers, known for its excellent feature extraction capabilities
- **MobileNetV2**: A lightweight, mobile-optimized CNN designed for efficiency while maintaining good accuracy
- Both models are pre-trained and fine-tuned for blood group classification
- Models are saved as `.h5` files (VGG16.h5 and MobileNetV2.h5)

### 2. **Data Processing Pipeline**
- **Input**: Fingerprint images (JPG/PNG format)
- **Preprocessing**: 
  - Convert to RGB format
  - Resize to 128x128 pixels
  - Normalize pixel values (divide by 255.0)
  - Add batch dimension for model input
- **Output**: 8-class classification (8 blood groups)

### 3. **API Implementation (FastAPI)**
The main application (`app.py`) provides a REST API with:
- **Endpoint**: `POST /predict`
- **Input**: Image file upload
- **Output**: JSON response with predictions from both models
- **Features**:
  - CORS enabled for cross-origin requests
  - File validation (image type checking)
  - Error handling and exception management
  - Dual model predictions with confidence scores
  - Model agreement/disagreement status

### 4. **Response Format**
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
  },
  "raw_result": "Model 1 (VGG16): A+ (87.45%)\nModel 2 (MobileNetV2): A+ (82.31%)\n\n✅ Both models agree!"
}
```

## 🔬 Model Training Process
Based on the Jupyter notebooks:
1. **Data Preparation**: Images organized in folders by blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)
2. **Data Augmentation**: Using ImageDataGenerator for training data enhancement
3. **Transfer Learning**: Both models use pre-trained weights as starting point
4. **Fine-tuning**: Custom dense layers added for 8-class blood group classification
5. **Training**: Models trained on Google Colab with GPU acceleration
6. **Evaluation**: Performance metrics and classification reports generated

## 📁 Project Structure
```
├── app.py                    # Main FastAPI application
├── VGG16.h5                  # Trained VGG16 model
├── MobileNetV2.h5            # Trained MobileNetV2 model
├── requirements.txt          # Python dependencies
├── test_api.py              # API testing script
├── demo_response.py         # Sample response format demo
├── Sample dataset/          # Test fingerprint images
│   ├── A+/                  # Sample images for each blood group
│   ├── A-/
│   ├── B+/
│   ├── B-/
│   ├── AB+/
│   ├── AB-/
│   ├── O+/
│   └── O-/
├── Major Project VGG16.ipynb    # VGG16 training notebook
├── Major Project MobileNetV2.ipynb # MobileNetV2 training notebook
├── Major Project Gradio.ipynb     # Gradio interface notebook
└── README.md                # Project documentation
```

## 🚀 How It Works

### 1. **Image Upload & Processing**
- User uploads a fingerprint image via API
- Image is validated (must be image format)
- Preprocessing pipeline converts image to model-ready format

### 2. **Dual Model Prediction**
- Both VGG16 and MobileNetV2 models process the same image
- Each model outputs probability distribution over 8 blood groups
- Highest probability class is selected as prediction
- Confidence score calculated as percentage

### 3. **Result Aggregation**
- Compare predictions from both models
- Determine if models agree or disagree
- Provide final prediction based on consensus
- Return structured JSON response with all details

### 4. **Error Handling**
- File type validation
- Image processing error handling
- Model prediction error handling
- Comprehensive exception management

## 🛠️ Technology Stack
- **Backend**: FastAPI (Python web framework)
- **ML Framework**: TensorFlow/Keras
- **Models**: VGG16, MobileNetV2 (pre-trained CNNs)
- **Image Processing**: PIL (Python Imaging Library)
- **Server**: Uvicorn ASGI server
- **Testing**: Requests library for API testing

## 🎯 Key Features
1. **Dual Model Approach**: Uses two different architectures for robust predictions
2. **Confidence Scoring**: Provides confidence percentages for each prediction
3. **Model Consensus**: Checks agreement between models for reliability
4. **RESTful API**: Clean, well-documented API endpoints
5. **Error Handling**: Comprehensive error management and validation
6. **Sample Dataset**: Includes test images for all blood groups
7. **Cross-Platform**: Works on any system with Python support

## 🔧 Usage
1. **Start Server**: `python app.py` (runs on http://localhost:8000)
2. **Test API**: Use `test_api.py` script or send POST request to `/predict`
3. **Upload Image**: Send fingerprint image as multipart/form-data
4. **Get Results**: Receive JSON response with blood group predictions

## 📊 Dependencies
```
tensorflow==2.20.0
numpy==1.26.4
scikit-learn==1.6.1
pandas==2.2.2
matplotlib==3.10.0
seaborn==0.13.2
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
```

## 🧪 Testing
- **API Testing**: Use `test_api.py` to test the prediction endpoint
- **Sample Data**: Test with images from the `Sample dataset` folder
- **Response Demo**: Check `demo_response.py` for expected response format

## 🎓 Educational Value
This project demonstrates a complete machine learning pipeline from model training to production deployment, showcasing the practical application of deep learning for medical/biological classification tasks. It includes:
- Transfer learning implementation
- Model comparison and ensemble methods
- API development and deployment
- Error handling and validation
- Testing and documentation

## 🔮 Future Enhancements
- Add more sophisticated ensemble methods
- Implement model versioning
- Add batch prediction capabilities
- Include model performance metrics in API response
- Add authentication and rate limiting
- Implement model retraining pipeline
