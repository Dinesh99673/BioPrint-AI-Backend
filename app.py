#Importing the required Libraries
import tensorflow as tf
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from PIL import Image
import uvicorn
import io
import smtplib
import random
import string
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import sys
import os

# Import fingerprint scanner library
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Import the fingerprint scanner module (handle hyphenated filename)
import importlib.util
scanner_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fingerprint-scanner.py")
spec = importlib.util.spec_from_file_location("fingerprint_scanner", scanner_path)
fingerprint_scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fingerprint_scanner)
R307FingerprintCaptureLibrary = fingerprint_scanner.R307FingerprintCaptureLibrary

# Create FastAPI app
app = FastAPI(
    title="Blood Group Prediction API",
    description="API for predicting blood group from fingerprint images using VGG16 and MobileNetV2 models",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Accessing the models
model1 = tf.keras.models.load_model("VGG16.h5")
model2 = tf.keras.models.load_model("MobileNetV2.h5")

# Blood group labels
class_labels = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

# Email configuration (dummy data - replace with actual values)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "dc7821836954@gmail.com"  # Replace with actual email
SMTP_PASSWORD = "pyrdwgzsbzrzfaoc"     # Replace with actual app password

# In-memory storage for OTPs
otp_storage = {}

# Pydantic models for new APIs
class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

# Preprocessing function
def preprocess(image):
    image = image.convert("RGB").resize((128, 128))
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image

# Prediction function
def predict(image):
    if image is None:
        return "No image uploaded."

    try:
        processed = preprocess(image)
    except Exception as e:
        return f"Image preprocessing failed: {str(e)}"

    try:
        pred1 = model1.predict(processed)[0]
        pred2 = model2.predict(processed)[0]
    except Exception as e:
        return f"Prediction failed: {str(e)}"

    idx1 = np.argmax(pred1)
    idx2 = np.argmax(pred2)

    label1 = class_labels[idx1]
    label2 = class_labels[idx2]

    confidence1 = round(pred1[idx1] * 100, 2)
    confidence2 = round(pred2[idx2] * 100, 2)

    agreement = "✅ Both models agree!" if label1 == label2 else "⚠️ Models disagree."

    result = f"Model 1 (VGG16): {label1} ({confidence1}%)\n"
    # result += f"Model 2 (MobileNetV2): {label2} ({confidence2}%)\n\n"
    # result += agreement

    return result

# Email and OTP helper functions
def send_email(to: str, subject: str, body: str) -> bool:
    """Send email using SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, to, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def generate_otp() -> str:
    """Generate 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def cleanup_expired_otps():
    """Clean up expired OTPs from storage"""
    current_time = time.time()
    expired_emails = [email for email, data in otp_storage.items() 
                     if current_time > data["expires_at"]]
    for email in expired_emails:
        del otp_storage[email]

@app.get("/")
async def root():
    return {"message": "Blood Group Prediction API", "status": "running"}

@app.post("/predict")
async def predict_blood_group(file: UploadFile = File(...)):
    """
    Predict blood group from fingerprint image.

    Upload a fingerprint image (JPG/PNG) to get blood group predictions from both VGG16 and MobileNetV2 models.
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read image file
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Preprocess the image
        processed_image = preprocess(image)

        # Get predictions from both models
        try:
            pred1 = model1.predict(processed_image)[0]  # VGG16
            pred2 = model2.predict(processed_image)[0]  # MobileNetV2
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Model prediction failed: {str(e)}")

        # Get results for both models
        idx1 = np.argmax(pred1)
        idx2 = np.argmax(pred2)

        blood_group1 = class_labels[idx1]  # VGG16 prediction
        blood_group2 = class_labels[idx2]  # MobileNetV2 prediction

        confidence1 = round(pred1[idx1] * 100, 2)  # VGG16 confidence
        confidence2 = round(pred2[idx2] * 100, 2)  # MobileNetV2 confidence

        # Check agreement between models
        agreement = "✅ Both models agree!" if blood_group1 == blood_group2 else "⚠️ Models disagree."

        # Create formatted results for backward compatibility
        vgg16_result = f"Model 1 (VGG16): {blood_group1} ({confidence1}%)"
        mobilenet_result = f"Model 2 (MobileNetV2): {blood_group2} ({confidence2}%)"
        raw_result = f"{vgg16_result}\n{mobilenet_result}\n\n{agreement}"

        return {
            "success": True,
            "predictions": {
                "vgg16": {
                    "blood_group": blood_group1,
                    "confidence": confidence1,
                    "model": "VGG16"
                },
                "mobilenetv2": {
                    "blood_group": blood_group2,
                    "confidence": confidence2,
                    "model": "MobileNetV2"
                },
                "agreement": agreement,
                "final_prediction": blood_group1 if blood_group1 == blood_group2 else "Needs verification"
            },
            "raw_result": raw_result
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# New API endpoints for BioPrint system

@app.post("/send-email")
async def send_email_endpoint(email_data: EmailRequest):
    """
    Send email endpoint for hospital notifications and other communications.
    """
    try:
        success = send_email(
            to=email_data.to,
            subject=email_data.subject,
            body=email_data.body
        )
        
        if success:
            return {
                "success": True,
                "message": "Email sent successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-otp")
async def send_otp_endpoint(otp_request: OTPRequest):
    """
    Send OTP to patient email for verification.
    OTP is valid for 2 minutes.
    """
    try:
        email = otp_request.email
        otp = generate_otp()
        
        # Clean up expired OTPs first
        cleanup_expired_otps()
        
        # Store OTP with expiration (2 minutes)
        otp_storage[email] = {
            "otp": otp,
            "expires_at": time.time() + 120,  # 2 minutes
            "attempts": 0,
            "created_at": time.time()
        }
        
        # Send OTP via email
        subject = "BioPrint AI - OTP Verification"
        body = f"""
        Your OTP for BioPrint AI access is: {otp}
        
        This OTP will expire in 2 minutes.
        
        If you didn't request this OTP, please ignore this email.
        
        Best regards,
        BioPrint AI Team
        """
        
        success = send_email(to=email, subject=subject, body=body)
        
        if success:
            return {
                "success": True,
                "message": "OTP sent successfully",
                "otp_expires_in": 120
            }
        else:
            # Remove OTP if email sending failed
            if email in otp_storage:
                del otp_storage[email]
            raise HTTPException(status_code=500, detail="Failed to send OTP")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-otp")
async def verify_otp_endpoint(verify_data: OTPVerify):
    """
    Verify OTP and grant access.
    OTP is deleted after successful verification.
    """
    try:
        email = verify_data.email
        otp = verify_data.otp
        
        # Clean up expired OTPs first
        cleanup_expired_otps()
        
        if email not in otp_storage:
            raise HTTPException(status_code=400, detail="OTP not found or expired")
        
        stored_data = otp_storage[email]
        
        # Check if OTP is expired
        if time.time() > stored_data["expires_at"]:
            del otp_storage[email]
            raise HTTPException(status_code=400, detail="OTP expired")
        
        # Check attempts limit (max 3 attempts)
        if stored_data["attempts"] >= 3:
            del otp_storage[email]
            raise HTTPException(status_code=400, detail="Too many attempts. OTP has been invalidated.")
        
        # Verify OTP
        if stored_data["otp"] == otp:
            # Remove OTP after successful verification
            del otp_storage[email]
            return {
                "success": True,
                "message": "OTP verified successfully"
            }
        else:
            # Increment attempts
            otp_storage[email]["attempts"] += 1
            remaining_attempts = 3 - otp_storage[email]["attempts"]
            if remaining_attempts > 0:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid OTP. {remaining_attempts} attempts remaining."
                )
            else:
                del otp_storage[email]
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid OTP. Maximum attempts reached. OTP has been invalidated."
                )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/capture-and-predict")
async def capture_and_predict_blood_group():
    """
    Capture fingerprint from hardware scanner and predict blood group.
    
    This endpoint:
    1. Connects to the R307S fingerprint scanner (COM7, 57600 baud)
    2. Captures fingerprint image (10 second timeout)
    3. Saves as BMP file
    4. Processes through VGG16 and MobileNetV2 models
    5. Returns blood group predictions
    """
    try:
        # Initialize fingerprint scanner with hardcoded settings
        capture = R307FingerprintCaptureLibrary(port='COM7', baudrate=57600)
        
        # Capture fingerprint with 10 second timeout
        filename = capture.capture_and_save(timeout=10)
        
        if filename is None:
            raise HTTPException(
                status_code=400, 
                detail="No fingerprint detected please try again"
            )
        
        # Check if file exists
        if not os.path.exists(filename):
            raise HTTPException(
                status_code=500,
                detail="Fingerprint file was not saved correctly. Please try again."
            )
        
        # Read and process the BMP image
        try:
            image = Image.open(filename)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to read fingerprint image: {str(e)}"
            )
        
        # Preprocess the image
        processed_image = preprocess(image)
        
        # Get predictions from both models
        try:
            pred1 = model1.predict(processed_image)[0]  # VGG16
            pred2 = model2.predict(processed_image)[0]  # MobileNetV2
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Model prediction failed: {str(e)}")
        
        # Get results for both models
        idx1 = np.argmax(pred1)
        idx2 = np.argmax(pred2)
        
        blood_group1 = class_labels[idx1]  # VGG16 prediction
        blood_group2 = class_labels[idx2]  # MobileNetV2 prediction
        
        confidence1 = round(pred1[idx1] * 100, 2)  # VGG16 confidence
        confidence2 = round(pred2[idx2] * 100, 2)  # MobileNetV2 confidence
        
        # Check agreement between models
        agreement = "✅ Both models agree!" if blood_group1 == blood_group2 else "⚠️ Models disagree."
        
        # Create formatted results for backward compatibility
        vgg16_result = f"Model 1 (VGG16): {blood_group1} ({confidence1}%)"
        mobilenet_result = f"Model 2 (MobileNetV2): {blood_group2} ({confidence2}%)"
        raw_result = f"{vgg16_result}\n{mobilenet_result}\n\n{agreement}"
        
        return {
            "success": True,
            "predictions": {
                "vgg16": {
                    "blood_group": blood_group1,
                    "confidence": confidence1,
                    "model": "VGG16"
                },
                "mobilenetv2": {
                    "blood_group": blood_group2,
                    "confidence": confidence2,
                    "model": "MobileNetV2"
                },
                "agreement": agreement,
                "final_prediction": blood_group1 if blood_group1 == blood_group2 else "Needs verification"
            },
            "raw_result": raw_result,
            "source": "hardware_scanner",
            "image_path": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Handle hardware connection errors
        error_message = str(e).lower()
        if "no such file or directory" in error_message or "cannot open" in error_message or "com" in error_message.lower():
            raise HTTPException(
                status_code=503,
                detail="Hardware scanner not detected. Please ensure the fingerprint scanner is connected to COM7 and try again."
            )
        elif "timeout" in error_message.lower():
            raise HTTPException(
                status_code=400,
                detail="No fingerprint detected please try again"
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Fingerprint capture and prediction failed: {str(e)}"
            )

@app.post("/enroll-fingerprint")
async def enroll_fingerprint_endpoint():
    """
    Enroll a new fingerprint in the R307S module.
    
    This endpoint:
    1. Connects to the fingerprint scanner (COM7, 57600 baud)
    2. Captures fingerprint twice for verification
    3. Stores fingerprint in the module
    4. Returns the slot number where fingerprint is stored
    """
    try:
        # Initialize fingerprint scanner with hardcoded settings
        capture = R307FingerprintCaptureLibrary(port='COM7', baudrate=57600)
        
        # Enroll fingerprint with 10 second timeout per capture
        slot_number = capture.enroll_fingerprint(timeout=10)
        print(slot_number)
        if slot_number is None:
            raise HTTPException(
                status_code=400,
                detail="Fingerprint enrollment failed. Please ensure the sensor is connected and try again."
            )
        
        return {
            "success": True,
            "slot_number": slot_number,
            "message": f"Fingerprint enrolled successfully in slot {slot_number}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Handle hardware connection errors
        error_message = str(e).lower()
        if "no such file or directory" in error_message or "cannot open" in error_message or "com" in error_message.lower():
            raise HTTPException(
                status_code=503,
                detail="Hardware scanner not detected. Please ensure the fingerprint scanner is connected to COM7 and try again."
            )
        elif "timeout" in error_message.lower():
            raise HTTPException(
                status_code=400,
                detail="Fingerprint enrollment timeout. Please try again."
            )
        elif "do not match" in error_message.lower():
            raise HTTPException(
                status_code=400,
                detail="Fingerprints do not match. Please try enrolling again."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Fingerprint enrollment failed: {str(e)}"
            )

@app.post("/search-fingerprint")
async def search_fingerprint_endpoint():
    """
    Search for a fingerprint in the R307S module.
    
    This endpoint:
    1. Connects to the fingerprint scanner (COM7, 57600 baud)
    2. Captures fingerprint from sensor
    3. Searches the module's database for a match
    4. Returns the slot number if found
    """
    try:
        # Initialize fingerprint scanner with hardcoded settings
        capture = R307FingerprintCaptureLibrary(port='COM7', baudrate=57600)
        
        # Search for fingerprint with 10 second timeout
        slot_number = capture.search_fingerprint(timeout=10)
        
        if slot_number is None:
            return {
                "success": False,
                "slot_number": None,
                "message": "Fingerprint not found in database"
            }
        
        return {
            "success": True,
            "slot_number": slot_number,
            "message": f"Fingerprint found in slot {slot_number}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Handle hardware connection errors
        error_message = str(e).lower()
        if "no such file or directory" in error_message or "cannot open" in error_message or "com" in error_message.lower():
            raise HTTPException(
                status_code=503,
                detail="Hardware scanner not detected. Please ensure the fingerprint scanner is connected to COM7 and try again."
            )
        elif "timeout" in error_message.lower():
            raise HTTPException(
                status_code=400,
                detail="Fingerprint capture timeout. Please try again."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Fingerprint search failed: {str(e)}"
            )

@app.get("/health")
async def health_check():
    """
    Enhanced health check endpoint with system status.
    """
    cleanup_expired_otps()  # Clean up expired OTPs on health check
    
    return {
        "status": "healthy",
        "message": "BioPrint API is running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "active_otps": len(otp_storage),
        "models_loaded": {
            "vgg16": model1 is not None,
            "mobilenetv2": model2 is not None
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
