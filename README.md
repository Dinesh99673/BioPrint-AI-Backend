---
title: Prediction of Blood Group Using Fingerprints
sdk: gradio
emoji: 😻
colorFrom: yellow
colorTo: blue
short_description: Predicts Blood Group from the image of fingerprint using CNN
sdk_version: 5.25.0
---
# 🧠 Prediction of Blood Group Using Fingerprints

This web application uses **deep learning models (VGG16 & MobileNetV2)** to predict a person's **blood group** based on a fingerprint image.

Built using **Gradio**, the app provides an interactive and user-friendly interface for quick predictions.

---

## 🚀 Features

- 🔍 Predicts one of 8 blood groups: `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`
- 📊 Uses **two different models** to ensure accuracy and compare predictions
- 💡 Shows confidence scores and agreement status between models
- 🌐 Fully accessible through Hugging Face Spaces — no installation required
- 🖼 Includes a sample dataset to try the app easily

---

## 🧠 Models Used

| Model         | Architecture    | Input Size |
|---------------|------------------|------------|
| VGG16         | Convolutional    | 224x224    |
| MobileNetV2   | Lightweight CNN  | 224x224    |

Both models were trained using TensorFlow and saved as `.h5` files. Each model independently predicts the blood group based on the fingerprint image.

---

## 🗂 Sample Dataset

A folder named `sample_dataset` is included in this Space, containing example fingerprint images for each blood group.

Each subfolder corresponds to a blood type:

sample_dataset/ ├── A+/ 
                ├── A-/ 
                ├── B+/ 
                ├── B-/ 
                ├── AB+/ 
                ├── AB-/ 
                ├── O+/ 
                └── O-/


You can try out the app by uploading any image from this dataset!

---

## 🖼 Sample Usage

1. Upload a fingerprint image (JPG/PNG)
2. The app preprocesses the image automatically
3. Both models make predictions
4. You receive:
   - Predicted blood group from **both models**
   - Their **confidence scores**
   - Whether the models **agree or disagree**

---

## 📁 File Structure

predicting-blood-group-using-fingerprints │ 
├── app.py # Gradio app logic 
├── VGG16.h5 # Trained VGG16 model 
├── MobileNetV2.h5 # Trained MobileNetV2 model 
├── requirements.txt # Project dependencies 
├── sample_dataset/ # Example fingerprint images 
│ └── [A+, A-, ..., O-]/ # One folder per blood group 
├── README.md # Project overview (this file) 
└── .gitattributes # Git LFS tracking (auto-created)

---

## 🛠 Run Locally (Optional)

To run this app on your own machine:

### 1. Clone the repo:
```bash
git clone https://huggingface.co/spaces/your-username/predicting-blood-group-using-fingerprints
cd predicting-blood-group-using-fingerprints

### 2. Install Dependencies:
pip install -r requirements.txt

### 3. Launch App:
python app.py

Then visit: http://127.0.0.1:7860

---

Feel free to customize the README as needed.