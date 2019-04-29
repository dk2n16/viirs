"""Unittests for VIIRS processing scripts"""

from unittest import TestCase, main as testmain
import main

class ViirsProcessing(TestCase):
    """Unittests for VIIRS processing scripts"""

    def setUp(self):
        """Instantiate class"""
        pass

    def tearDown(self):
        """Tead down class"""
        pass

    def test_object_made(self):
        """Test whether object instantiated"""
        self.assertEqual('DavidHyekyung', 'DavidHyekyung')

if __name__ == "__main__":
    testmain()
