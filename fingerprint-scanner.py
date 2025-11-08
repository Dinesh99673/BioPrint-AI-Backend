#!/usr/bin/env python3
"""
R307S Fingerprint Capture Script using PyFingerprint Library
This version uses the PyFingerprint library for more reliable communication

Red - 3.3V
Black - GND 
Yellow - Tx (Transmit)
Green - Rx (Receive)
Baudrate - 57600

"""

import os
import sys
from datetime import datetime
from typing import Optional
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from pyfingerprint.pyfingerprint import PyFingerprint
except ImportError:
    print("PyFingerprint library not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyfingerprint"])
    from pyfingerprint.pyfingerprint import PyFingerprint

class R307FingerprintCaptureLibrary:
    """R307S fingerprint sensor capture using PyFingerprint library"""
    
    def __init__(self, port: str = 'COM7', baudrate: int = 57600, address: int = 0xFFFFFFFF, password: int = 0x00000000):
        self.port = port
        self.baudrate = baudrate
        self.address = address
        self.password = password
        self.fingerprint = None
        
    def connect(self) -> bool:
        """Initialize connection to the sensor"""
        try:
            logger.info(f"Connecting to {self.port} at {self.baudrate} baud...")
            self.fingerprint = PyFingerprint(self.port, self.baudrate, self.address, self.password)
            
            if not self.fingerprint.verifyPassword():
                logger.error("The given fingerprint sensor password is wrong")
                return False
            
            logger.info("✅ Sensor connected and verified successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize sensor: {e}")
            return False
    
    def disconnect(self):
        """Close connection to sensor"""
        if self.fingerprint:
            try:
                # PyFingerprint doesn't have explicit disconnect, but we can clear the reference
                self.fingerprint = None
                logger.info("Disconnected from sensor")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
    
    def capture_fingerprint(self, timeout: int = 10) -> bool:
        """Capture fingerprint image from sensor with timeout"""
        try:
            logger.info("Place your finger on the sensor...")
            
            start_time = time.time()
            # Wait for finger to be placed and read image with timeout
            while not self.fingerprint.readImage():
                if time.time() - start_time > timeout:
                    logger.error(f"Fingerprint capture timeout after {timeout} seconds")
                    return False
                time.sleep(0.1)  # Small delay to avoid busy waiting
            
            logger.info("✅ Fingerprint captured successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Fingerprint capture failed: {e}")
            return False
    
    def download_and_save_image(self) -> Optional[str]:
        """Download image data and save as BMP file"""
        try:
            logger.info("Downloading image...")
            
            # Create Images directory if it doesn't exist
            os.makedirs('Images', exist_ok=True)
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Images/fingerprint_{timestamp}.bmp"
            
            # Download image using PyFingerprint library
            self.fingerprint.downloadImage(filename)
            
            logger.info(f"✅ Fingerprint image saved as {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to download and save image: {e}")
            return None
    
    def capture_and_save(self, timeout: int = 10) -> Optional[str]:
        """Main method to capture and save fingerprint with timeout"""
        try:
            # Connect to sensor
            if not self.connect():
                return None
            
            # Capture fingerprint with timeout
            if not self.capture_fingerprint(timeout=timeout):
                return None
            
            # Download and save image
            filename = self.download_and_save_image()
            return filename
            
        except Exception as e:
            logger.error(f"Error during capture: {e}")
            return None
        finally:
            self.disconnect()
    
    def find_next_available_slot(self) -> Optional[int]:
        """Find the next available slot number in the module"""
        try:
            # Get template count to know how many are stored
            try:
                template_count = self.fingerprint.getTemplateCount()
                logger.info(f"Current template count: {template_count}")
            except AttributeError:
                # If getTemplateCount doesn't exist, start from 0
                template_count = 0
                logger.info("Template count method not available, starting search from slot 0")
            
            # R307S typically has 1000 slots (0-999)
            max_slots = 1000
            
            # Start searching from where we have templates, but check from beginning to be safe
            start_slot = max(0, template_count - 10)  # Start a bit before template count
            if start_slot < 0:
                start_slot = 0
            
            # Check each slot to find the first empty one
            for slot in range(start_slot, max_slots):
                try:
                    # Try to load template from slot - this will raise exception if slot is empty
                    # Some versions return True/False, others raise exceptions
                    try:
                        result = self.fingerprint.loadTemplate(slot, 1)  # Load to CharBuffer1
                        # If loadTemplate returns True or doesn't raise exception, slot is occupied
                        continue
                    except:
                        # Exception means slot is empty or error occurred
                        # Check if it's truly empty by trying to search
                        try:
                            # Try a simple check - if we can't load, it's likely empty
                            logger.info(f"Found available slot: {slot}")
                            return slot
                        except:
                            continue
                except Exception as e:
                    # If loading fails, slot is likely empty
                    logger.info(f"Found available slot: {slot} (empty)")
                    return slot
            
            logger.error("No available slots found")
            return None
            
        except Exception as e:
            logger.error(f"Error finding available slot: {e}")
            # Return a default slot if all else fails (start from 0)
            logger.warning("Using slot 0 as fallback")
            return 0
    
    def enroll_fingerprint(self, timeout: int = 10) -> Optional[int]:
        """
        Enroll a new fingerprint in the module.
        Captures fingerprint twice for verification, then stores it.
        Returns the slot number where fingerprint is stored, or None if failed.
        """
        try:
            # Connect to sensor
            if not self.connect():
                return None
            
            logger.info("Starting fingerprint enrollment...")
            logger.info("Step 1: Place your finger on the sensor...")
            
            # First capture
            start_time = time.time()
            while not self.fingerprint.readImage():
                if time.time() - start_time > timeout:
                    logger.error(f"First capture timeout after {timeout} seconds")
                    return None
                time.sleep(0.1)
            
            logger.info("✅ First capture successful!")
            self.fingerprint.convertImage(0x01)  # Convert to template and store in buffer 1
            
            logger.info("Step 2: Remove your finger and place it again...")
            time.sleep(2)  # Give user time to remove finger
            
            # Second capture for verification
            start_time = time.time()
            while not self.fingerprint.readImage():
                if time.time() - start_time > timeout:
                    logger.error(f"Second capture timeout after {timeout} seconds")
                    return None
                time.sleep(0.1)
            
            logger.info("✅ Second capture successful!")
            self.fingerprint.convertImage(0x02)  # Convert to template and store in buffer 2
            
            # Compare the two characteristics
            # compareCharacteristics() returns 0 if they don't match, or a value > 0 if they match
            try:
                match_score = self.fingerprint.compareCharacteristics()
                if match_score == 0:
                    logger.error("Fingerprints do not match! Please try again.")
                    return None
                logger.info(f"✅ Fingerprints match with score: {match_score}")
            except AttributeError:
                # If compareCharacteristics doesn't exist, try alternative method
                try:
                    # Some versions use matchTemplate() or other methods
                    if hasattr(self.fingerprint, 'matchTemplate'):
                        if not self.fingerprint.matchTemplate():
                            logger.error("Fingerprints do not match! Please try again.")
                            return None
                    else:
                        # Skip comparison if method doesn't exist (less secure but will work)
                        logger.warning("Template comparison method not available, proceeding without verification")
                except Exception as e:
                    logger.warning(f"Could not compare templates: {e}, proceeding anyway")
            
            logger.info("✅ Creating template...")
            self.fingerprint.createTemplate()  # Combine both templates into CharBuffer1
            
            # Find next available slot - try simple approach first
            slot = None
            try:
                # Try to get template count and use next slot
                template_count = self.fingerprint.getTemplateCount()
                slot = template_count
                logger.info(f"Using next slot number: {slot} (based on template count: {template_count})")
            except (AttributeError, Exception) as e:
                # Fallback: try to find available slot
                logger.warning(f"Could not get template count: {e}, trying to find available slot")
                slot = self.find_next_available_slot()
                if slot is None:
                    logger.warning("Could not find available slot, using slot 0")
                    slot = 0
            
            # Store template in the found slot
            # storeTemplate(position) stores template from CharBuffer1 to specified position
            try:
                result = self.fingerprint.storeTemplate(slot)
                # Some versions return True/False, others return nothing
                logger.info(f"✅ Fingerprint stored in slot {slot}!")
                logger.info(f"✅ Fingerprint enrolled successfully in slot {slot}!")
                return slot
            except Exception as e:
                logger.error(f"Error storing template in slot {slot}: {e}")
                # Try storing in next slot if current one failed
                try:
                    next_slot = slot + 1
                    logger.info(f"Trying next slot: {next_slot}")
                    self.fingerprint.storeTemplate(next_slot)
                    logger.info(f"✅ Fingerprint enrolled successfully in slot {next_slot}!")
                    return next_slot
                except Exception as e2:
                    logger.error(f"Error storing in next slot: {e2}")
                    # Last resort: try slot 0
                    try:
                        logger.info("Trying slot 0 as last resort")
                        self.fingerprint.storeTemplate(0)
                        logger.info(f"✅ Fingerprint enrolled successfully in slot 0!")
                        return 0
                    except Exception as e3:
                        logger.error(f"Error storing in slot 0: {e3}")
                        return None
            
        except Exception as e:
            logger.error(f"Error during fingerprint enrollment: {e}")
            return None
        finally:
            self.disconnect()
    
    def search_fingerprint(self, timeout: int = 10) -> Optional[int]:
        """
        Search for a fingerprint in the module.
        Captures fingerprint, converts to template, and searches the database.
        Returns the slot number if found, None if not found.
        """
        try:
            # Connect to sensor
            if not self.connect():
                return None
            
            logger.info("Searching for fingerprint...")
            logger.info("Place your finger on the sensor...")
            
            # Capture fingerprint
            start_time = time.time()
            while not self.fingerprint.readImage():
                if time.time() - start_time > timeout:
                    logger.error(f"Fingerprint capture timeout after {timeout} seconds")
                    return None
                time.sleep(0.1)
            
            logger.info("✅ Fingerprint captured!")
            self.fingerprint.convertImage(0x01)  # Convert to template and store in buffer 1
            
            # Search for the template in the database
            # Search in slots 0-999 with security level 3
            logger.info("Searching database...")
            result = self.fingerprint.searchTemplate()
            
            position_number = result[0]
            accuracy_score = result[1]
            
            if position_number == -1:
                logger.warning("Fingerprint not found in database")
                return None
            
            logger.info(f"✅ Fingerprint found in slot {position_number} with accuracy {accuracy_score}")
            return position_number
            
        except Exception as e:
            logger.error(f"Error during fingerprint search: {e}")
            return None
        finally:
            self.disconnect()

def main():
    """Main function"""
    print("R307S Fingerprint Capture Script (Library Version)")
    print("=" * 55)
    
    # Create capture instance
    capture = R307FingerprintCaptureLibrary(port='COM7', baudrate=57600)
    
    # Capture and save fingerprint
    result = capture.capture_and_save()
    
    if result:
        print(f"\n✅ Success! Fingerprint saved as: {result}")
        return True
    else:
        print("\n❌ Failed to capture fingerprint")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
