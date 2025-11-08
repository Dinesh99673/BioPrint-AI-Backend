#!/usr/bin/env python3
"""
Demo script showing the new dual-model prediction API response format
"""
import json

# Sample response showing both model predictions
sample_response = {
    "success": True,
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

print("🎯 New Dual-Model Prediction API Response Format:")
print("=" * 60)
print(json.dumps(sample_response, indent=2))

print("\n" + "=" * 60)
print("📋 Key Changes from Previous Version:")
print("• Added 'predictions' object containing both models")
print("• VGG16 and MobileNetV2 predictions are separate")
print("• Agreement status between models")
print("• Final prediction based on model consensus")
print("• Backward compatibility with 'raw_result' field")
print("=" * 60)
