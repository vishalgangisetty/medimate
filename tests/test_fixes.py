import sys
import os

from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.reminder import ReminderManager
from src.otc_manager import OTCManager

import unittest

class TestFixes(unittest.TestCase):

    def test_mark_as_taken_existence(self):
        """Verify mark_as_taken exists and accepts correct arguments"""
        rm = ReminderManager()
        self.assertTrue(hasattr(rm, 'mark_as_taken'))
        
        # Mock adherence collection to avoid actual DB writes
        rm.adherence = MagicMock()
        
        # Test call
        try:
            result = rm.mark_as_taken("test_user", "Test Med", "08:00")
            self.assertTrue(result['success'])
            rm.adherence.insert_one.assert_called_once()
            
            args = rm.adherence.insert_one.call_args[0][0]
            self.assertEqual(args['medicine_name'], "Test Med")
            self.assertEqual(args['status'], "taken")
            self.assertEqual(args['scheduled_time'], "08:00")
        except Exception as e:
            self.fail(f"mark_as_taken failed with error: {e}")

    @patch('src.otc_manager.OTCManager._initialize_otc_db')
    def test_otc_manager_initialization(self, mock_init):
        """Verify OTC Manager initializes"""
        with patch('src.otc_manager.VectorStoreManager') as MockVectorStore:
            # Setup mock behavior
            mock_vs_instance = MockVectorStore.return_value
            mock_vs_instance.index.describe_index_stats.return_value = MagicMock(
                namespaces={'otc_medicines': MagicMock(vector_count=100)}
            )
            
            try:
                manager = OTCManager()
                self.assertIsNotNone(manager)
            except Exception as e:
                self.fail(f"OTCManager initialization failed: {e}")
        
    def test_ui_import(self):
        """Verify src/ui_pages_medical.py imports correctly (syntax check)"""
        try:
            import src.ui_pages_medical
        except ImportError as e:
            # Ignore import errors related to streamlit or missing env vars
            pass
        except SyntaxError as e:
            self.fail(f"Syntax Error in ui_pages_medical.py: {e}")

if __name__ == '__main__':
    unittest.main()
