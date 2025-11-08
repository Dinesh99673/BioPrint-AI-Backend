# BioPrint API Documentation

## Overview
The BioPrint API now includes additional endpoints for email notifications and OTP verification, in addition to the existing blood group prediction functionality.

## Base URL
```
http://localhost:8000
```

## Existing Endpoints (Unchanged)

### 1. Health Check
- **GET** `/`
- **Description**: Basic health check
- **Response**: 
```json
{
  "message": "Blood Group Prediction API",
  "status": "running"
}
```

### 2. Blood Group Prediction
- **POST** `/predict`
- **Description**: Predict blood group from fingerprint image
- **Request**: Multipart form data with image file
- **Response**: Blood group prediction with confidence scores

## New Endpoints

### 1. Enhanced Health Check
- **GET** `/health`
- **Description**: Enhanced health check with system status
- **Response**:
```json
{
  "status": "healthy",
  "message": "BioPrint API is running",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00",
  "active_otps": 0,
  "models_loaded": {
    "vgg16": true,
    "mobilenetv2": true
  }
}
```

### 2. Send Email
- **POST** `/send-email`
- **Description**: Send email notifications
- **Request Body**:
```json
{
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "body": "Email body content"
}
```
- **Response**:
```json
{
  "success": true,
  "message": "Email sent successfully"
}
```

### 3. Send OTP
- **POST** `/send-otp`
- **Description**: Send OTP to patient email for verification
- **Request Body**:
```json
{
  "email": "patient@example.com"
}
```
- **Response**:
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "otp_expires_in": 120
}
```
- **Notes**: 
  - OTP is valid for 2 minutes
  - OTP is automatically deleted after successful verification
  - Maximum 3 attempts allowed per OTP

### 4. Verify OTP
- **POST** `/verify-otp`
- **Description**: Verify OTP and grant access
- **Request Body**:
```json
{
  "email": "patient@example.com",
  "otp": "123456"
}
```
- **Response**:
```json
{
  "success": true,
  "message": "OTP verified successfully"
}
```
- **Error Responses**:
  - `400`: Invalid OTP, expired OTP, or too many attempts
  - `500`: Server error

## OTP Security Features

1. **Time-based Expiration**: OTPs expire after 2 minutes
2. **Attempt Limiting**: Maximum 3 attempts per OTP
3. **Auto-cleanup**: Expired OTPs are automatically removed
4. **One-time Use**: OTPs are deleted after successful verification
5. **In-memory Storage**: OTPs are stored in memory (not persistent)

## Email Configuration

### Current Setup (Dummy Data)
```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@gmail.com"  # Replace with actual email
SMTP_PASSWORD = "your_app_password"     # Replace with actual app password
```

### To Configure Real Email:
1. Update the SMTP credentials in `app.py`
2. For Gmail, enable 2FA and generate an App Password
3. Test using the provided test script

## Testing

### Run the Test Script
```bash
python test_new_apis.py
```

### Manual Testing with curl

#### Send Email
```bash
curl -X POST "http://localhost:8000/send-email" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "test@example.com",
    "subject": "Test Email",
    "body": "This is a test email"
  }'
```

#### Send OTP
```bash
curl -X POST "http://localhost:8000/send-otp" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com"
  }'
```

#### Verify OTP
```bash
curl -X POST "http://localhost:8000/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "otp": "123456"
  }'
```

## Error Handling

All endpoints include comprehensive error handling:
- **400**: Bad Request (invalid input, expired OTP, etc.)
- **500**: Internal Server Error (email sending failed, server errors)

## Dependencies

New dependencies added to `requirements.txt`:
- `pydantic[email]==2.5.0` - For email validation
- `Pillow==10.0.0` - For image processing (already used)

## Security Considerations

1. **Email Credentials**: Store SMTP credentials securely
2. **OTP Storage**: Currently in-memory (consider Redis for production)
3. **Rate Limiting**: Consider adding rate limiting for OTP requests
4. **Input Validation**: All inputs are validated using Pydantic
5. **Error Messages**: Avoid exposing sensitive information in error messages

## Production Recommendations

1. **Use Environment Variables**: Store email credentials in environment variables
2. **Redis Storage**: Use Redis for OTP storage in production
3. **Rate Limiting**: Implement rate limiting for OTP requests
4. **Logging**: Add comprehensive logging for audit trails
5. **Monitoring**: Add monitoring for email delivery and OTP usage
6. **SSL/TLS**: Ensure secure email transmission
7. **Backup Email Service**: Consider using services like SendGrid or AWS SES

## Integration with Frontend

The new APIs are designed to work seamlessly with the BioPrint React frontend:
- Email notifications for hospital approval/rejection
- OTP system for patient access verification
- Health checks for system monitoring
- All responses follow consistent JSON format
