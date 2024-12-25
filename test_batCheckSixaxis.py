import unittest
from unittest.mock import patch, mock_open
from batCheckSixaxis import (
    format_id,
    get_curr_devices,
    get_id_and_val,
    call_display_func,
)


class TestBatCheckSixaxis(unittest.TestCase):

    @patch("os.listdir")
    def test_get_curr_devices(self, mock_listdir):
        mock_listdir.return_value = [
            "sony_controller_battery_00:21:4f:13:09:52",
            "sony_controller_battery_00:21:4f:13:08:30",
            "random_device",
        ]
        devices = get_curr_devices("/mock/path")
        self.assertEqual(
            devices,
            [
                "sony_controller_battery_00:21:4f:13:09:52",
                "sony_controller_battery_00:21:4f:13:08:30",
            ],
        )

    def test_format_id(self):
        device_id = "00:21:4f:13:09:52"
        formatted_id = format_id(device_id)
        self.assertEqual(formatted_id, "00214130952")

    @patch("builtins.open", new_callable=mock_open, read_data="75\n")
    def test_get_id_and_val(self, mock_file):
        device = "sony_controller_battery_00:21:4f:13:09:52"
        with patch("os.path.exists", return_value=True):
            device_id, bat_val = get_id_and_val(device)
        self.assertEqual(device_id, "00214130952")
        self.assertEqual(bat_val, 3)  # 75 // 25 = 3

    @patch("os.system")
    def test_call_display_func(self, mock_system):
        with patch("batCheckSixaxis.icon_path", "/mock/icons/bat"), patch(
            "batCheckSixaxis.disp_exec_path", "/mock/path/code/batDisplay"
        ), patch("batCheckSixaxis.disp_cmd_options", "-x 24 -y 16 -t 5"), patch(
            "batCheckSixaxis.__debug", False
        ):

            call_display_func(3)
            expected_cmd = (
                "/mock/path/code/batDisplay -x 24 -y 16 -t 5 /mock/icons/bat3.png"
            )
            mock_system.assert_called_once_with(expected_cmd)


if __name__ == "__main__":
    unittest.main()
