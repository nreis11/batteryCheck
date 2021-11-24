import os
import glob
import time
import shutil
import unittest
from unittest.mock import patch


import batCheck_sixaxis

TEST_DIR = "./tmp"
TEST_DEVICE = "sony_controller_battery_00:21:4f:13:09:52"
TEST_DEVICE_ID = batCheck_sixaxis.formatKey(TEST_DEVICE)
TEST_DEVICE_PATH = TEST_DIR + "/" + TEST_DEVICE


class TestBatCheck(unittest.TestCase):
    def setUp(self) -> None:
        # Add device for every test run
        if not os.path.isdir(TEST_DIR):
            os.mkdir(TEST_DIR)
        os.mkdir(TEST_DEVICE_PATH)
        with open(TEST_DEVICE_PATH + "/capacity", "w") as f:
            f.write("75")
        return super().setUp()

    def tearDown(self) -> None:
        if os.listdir(TEST_DIR):
            shutil.rmtree(TEST_DIR)
        return super().tearDown()

    @patch("batCheck_sixaxis.callDisplayFunc")
    def test_add_device(self, mock_display_func):
        batCheck_sixaxis.main()
        mock_display_func.assert_called_once_with(3)

    def test_remove_device(self):
        batCheck_sixaxis.knownDevices = {"00214130952": 3}
        shutil.rmtree(TEST_DEVICE_PATH)
        batCheck_sixaxis.main()
        self.assertTrue(TEST_DEVICE_ID not in batCheck_sixaxis.knownDevices)

    def test_no_change_in_devices(self):
        pass


if __name__ == "__main__":
    unittest.main()