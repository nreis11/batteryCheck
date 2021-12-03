import os
import shutil
import unittest
from unittest.mock import patch
import batCheckSixaxis

batCheckSixaxis.DEVICE_PATH = TEST_DIR = "./tmp"
TEST_DEVICE = "sony_controller_battery_00:21:4f:13:09:52"
TEST_DEVICE_ID = batCheckSixaxis.format_id(TEST_DEVICE)
TEST_DEVICE_PATH = TEST_DIR + "/" + TEST_DEVICE
TEST_BATTERY_VAL = "75"


class TestBatCheck(unittest.TestCase):
    def setUp(self) -> None:
        # Add device for every test run
        if not os.path.isdir(TEST_DIR):
            os.mkdir(TEST_DIR)
        os.mkdir(TEST_DEVICE_PATH)
        with open(TEST_DEVICE_PATH + "/capacity", "w") as f:
            f.write(TEST_BATTERY_VAL)
        return super().setUp()

    def tearDown(self) -> None:
        if os.listdir(TEST_DIR):
            shutil.rmtree(TEST_DIR)
        return super().tearDown()

    @patch("batCheckSixaxis.call_display_func")
    def test_add_device(self, mock_display_func):
        batCheckSixaxis.main()
        mock_display_func.assert_called_once_with(3)
        self.assertTrue(TEST_DEVICE_ID in batCheckSixaxis.known_devices)

    def test_remove_device(self):
        batCheckSixaxis.known_devices = {TEST_DEVICE_ID: 3}
        shutil.rmtree(TEST_DEVICE_PATH)
        batCheckSixaxis.main()
        self.assertTrue(TEST_DEVICE_ID not in batCheckSixaxis.known_devices)

    def test_no_change_in_devices(self):
        pass


if __name__ == "__main__":
    unittest.main()