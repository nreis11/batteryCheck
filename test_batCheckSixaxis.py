import unittest
from unittest.mock import patch, mock_open, MagicMock
from inotify_simple import flags
from batCheckSixaxis import get_bat_val, call_display_func, main


class TestBatCheckSixaxis(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="50\n")
    def test_get_bat_val_valid(self, mock_file):
        """Test get_bat_val with valid battery capacity."""
        device = "sony_controller_battery_00:21:4f:13:09:52"
        with patch(
            "os.path.join", return_value=f"/sys/class/power_supply/{device}/capacity"
        ):
            self.assertEqual(get_bat_val(device), 2)

    @patch("builtins.open", new_callable=mock_open, read_data="invalid\n")
    def test_get_bat_val_invalid(self, mock_file):
        """Test get_bat_val with invalid battery capacity."""
        device = "sony_controller_battery_invalid"
        with patch(
            "os.path.join", return_value=f"/sys/class/power_supply/{device}/capacity"
        ):
            self.assertEqual(get_bat_val(device), 0)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_get_bat_val_file_not_found(self, mock_file):
        """Test get_bat_val when capacity file is missing."""
        device = "sony_controller_battery_missing"
        with patch(
            "os.path.join", return_value=f"/sys/class/power_supply/{device}/capacity"
        ):
            self.assertEqual(get_bat_val(device), 0)

    @patch("os.system")
    @patch("os.path.join", return_value="/mock/path/icons/bat2.png")
    def test_call_display_func(self, mock_join, mock_system):
        """Test call_display_func ensures correct command execution."""
        call_display_func(2)
        mock_system.assert_called_once_with(
            "/mock/path/code/batDisplay -x 24 -y 16 -t 5 /mock/path/icons/bat2.png"
        )

    @patch(
        "inotify_simple.INotify.read",
        return_value=[
            MagicMock(
                mask=flags.CREATE, name="sony_controller_battery_00:21:4f:13:09:52"
            )
        ],
    )
    @patch("os.path.exists", return_value=True)
    @patch("batCheckSixaxis.get_bat_val", return_value=2)
    @patch("batCheckSixaxis.call_display_func")
    def test_main_new_device(
        self, mock_display, mock_get_bat_val, mock_exists, mock_inotify_read
    ):
        """Test main with a newly connected device."""
        with patch("inotify_simple.INotify.add_watch"):
            with patch("sys.exit", side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    main()

        mock_get_bat_val.assert_called_once_with(
            "sony_controller_battery_00:21:4f:13:09:52"
        )
        mock_display.assert_called_once_with(2)

    @patch(
        "inotify_simple.INotify.read",
        return_value=[
            MagicMock(
                mask=flags.DELETE, name="sony_controller_battery_00:21:4f:13:09:52"
            )
        ],
    )
    @patch("os.path.exists", return_value=True)
    @patch("batCheckSixaxis.get_bat_val", return_value=2)
    def test_main_device_removal(
        self, mock_get_bat_val, mock_exists, mock_inotify_read
    ):
        """Test main when a device is removed."""
        with patch("inotify_simple.INotify.add_watch"):
            with patch("sys.exit", side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    main()

        mock_get_bat_val.assert_not_called()  # No need to fetch battery value on DELETE


if __name__ == "__main__":
    unittest.main()
