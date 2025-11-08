#!/usr/bin/env python3
"""
R307S Fingerprint Database Clear Script
Clears saved fingerprint slots/templates from the R307S module
"""

import os
import sys
import argparse
from typing import Optional, List
import logging

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

class R307FingerprintClear:
    """R307S fingerprint sensor database management"""
    
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
                self.fingerprint = None
                logger.info("Disconnected from sensor")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
    
    def get_template_count(self) -> int:
        """Get the number of stored templates"""
        try:
            count = self.fingerprint.getTemplateCount()
            return count
        except Exception as e:
            logger.error(f"Failed to get template count: {e}")
            return -1
    
    def list_templates(self) -> List[int]:
        """List all stored template positions"""
        try:
            templates = []
            count = self.get_template_count()
            
            if count == -1:
                return []
            
            logger.info(f"Scanning for templates... (Total count: {count})")
            
            # R307S typically has 162 template slots (0-161)
            for position in range(162):
                try:
                    # Try to read template - if it exists, this won't throw an error
                    if self.fingerprint.loadTemplate(position):
                        templates.append(position)
                except:
                    # Template doesn't exist at this position
                    pass
            
            return templates
            
        except Exception as e:
            logger.error(f"Failed to list templates: {e}")
            return []
    
    def delete_template(self, position: int) -> bool:
        """Delete a specific template at given position"""
        try:
            logger.info(f"Deleting template at position {position}...")
            self.fingerprint.deleteTemplate(position)
            logger.info(f"✅ Template at position {position} deleted successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete template at position {position}: {e}")
            return False
    
    def clear_all_templates(self) -> bool:
        """Clear all templates from the database"""
        try:
            logger.info("Clearing all templates from database...")
            self.fingerprint.clearDatabase()
            logger.info("✅ All templates cleared successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
            return False
    
    def clear_specific_slot(self, position: int) -> bool:
        """Clear a specific slot by position"""
        if not self.connect():
            return False
        
        try:
            # Check if template exists
            count = self.get_template_count()
            logger.info(f"Current template count: {count}")
            
            # Delete the specific template
            success = self.delete_template(position)
            return success
            
        except Exception as e:
            logger.error(f"Error during slot clearing: {e}")
            return False
        finally:
            self.disconnect()
    
    def clear_all_slots(self, confirm: bool = False) -> bool:
        """Clear all slots from the database"""
        if not self.connect():
            return False
        
        try:
            # Get current count
            count = self.get_template_count()
            logger.info(f"Current template count: {count}")
            
            if count == 0:
                logger.info("Database is already empty!")
                return True
            
            if not confirm:
                logger.warning("⚠️  WARNING: This will delete ALL templates!")
                logger.warning(f"   About to delete {count} template(s)")
            
            # Clear all templates
            success = self.clear_all_templates()
            
            if success:
                # Verify deletion
                new_count = self.get_template_count()
                logger.info(f"New template count: {new_count}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error during database clearing: {e}")
            return False
        finally:
            self.disconnect()
    
    def show_database_status(self):
        """Show current database status"""
        if not self.connect():
            return False
        
        try:
            count = self.get_template_count()
            
            print(f"\n{'='*50}")
            print(f"📊 R307S Database Status")
            print(f"{'='*50}")
            print(f"Total templates stored: {count}")
            
            if count > 0:
                templates = self.list_templates()
                if templates:
                    print(f"\nStored template positions:")
                    for pos in sorted(templates):
                        print(f"  • Slot {pos}")
                else:
                    print("\n⚠️  Could not enumerate template positions")
            else:
                print("\n✅ Database is empty")
            
            print(f"{'='*50}\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Error getting database status: {e}")
            return False
        finally:
            self.disconnect()

def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(
        description="Clear fingerprint templates from R307S sensor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clearModuleSlots.py --status              # Show current database status
  python clearModuleSlots.py --clear-all           # Clear all templates
  python clearModuleSlots.py --clear-slot 5        # Clear template at position 5
  python clearModuleSlots.py --list                # List all stored template positions
        """
    )
    
    parser.add_argument('--port', type=str, default='COM7', 
                       help='Serial port (default: COM7)')
    parser.add_argument('--baudrate', type=int, default=57600,
                       help='Baud rate (default: 57600)')
    parser.add_argument('--status', action='store_true',
                       help='Show current database status')
    parser.add_argument('--list', action='store_true',
                       help='List all stored template positions')
    parser.add_argument('--clear-all', action='store_true',
                       help='Clear all templates from database')
    parser.add_argument('--clear-slot', type=int, metavar='POSITION',
                       help='Clear template at specific position (0-161)')
    parser.add_argument('--yes', action='store_true',
                       help='Skip confirmation prompt for --clear-all')
    
    args = parser.parse_args()
    
    print("R307S Fingerprint Database Clear Tool")
    print("=" * 50)
    
    # Create clear instance
    clear_tool = R307FingerprintClear(port=args.port, baudrate=args.baudrate)
    
    success = False
    
    try:
        if args.status:
            # Show database status
            success = clear_tool.show_database_status()
            
        elif args.list:
            # List all templates
            if not clear_tool.connect():
                return False
            
            count = clear_tool.get_template_count()
            print(f"\n📊 Total templates: {count}")
            
            if count > 0:
                templates = clear_tool.list_templates()
                if templates:
                    print(f"\n📋 Stored template positions:")
                    for pos in sorted(templates):
                        print(f"  • Slot {pos}")
                else:
                    print("\n⚠️  Could not enumerate template positions")
            else:
                print("\n✅ Database is empty")
            
            clear_tool.disconnect()
            success = True
            
        elif args.clear_all:
            # Clear all templates
            if not args.yes:
                response = input(f"\n⚠️  WARNING: This will delete ALL templates!\nAre you sure? (yes/no): ")
                if response.lower() != 'yes':
                    print("❌ Operation cancelled")
                    return False
            
            success = clear_tool.clear_all_slots(confirm=True)
            
            if success:
                print("\n✅ All templates cleared successfully!")
            else:
                print("\n❌ Failed to clear templates")
                
        elif args.clear_slot is not None:
            # Clear specific slot
            if args.clear_slot < 0 or args.clear_slot > 161:
                print(f"❌ Invalid position: {args.clear_slot}")
                print("   Position must be between 0 and 161")
                return False
            
            success = clear_tool.clear_specific_slot(args.clear_slot)
            
            if success:
                print(f"\n✅ Template at position {args.clear_slot} cleared successfully!")
            else:
                print(f"\n❌ Failed to clear template at position {args.clear_slot}")
                
        else:
            # Default: show status
            print("\nNo action specified. Showing database status...\n")
            success = clear_tool.show_database_status()
            
            print("\n💡 Usage tips:")
            print("  python clearModuleSlots.py --status              # Show database status")
            print("  python clearModuleSlots.py --list                # List all templates")
            print("  python clearModuleSlots.py --clear-all           # Clear all templates")
            print("  python clearModuleSlots.py --clear-slot 5        # Clear specific slot")
            
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
