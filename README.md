# DillyKindle

Minimal Raspberry Pi e-paper reader.

## Raspberry Pi Lite setup

Run:

git clone https://github.com/amilpattni/dillykindle.git
cd dillykindle
./setup_pi_lite.sh
./run_epaper.sh

## Notes

- Use Raspberry Pi OS Lite.
- Do not run pip install -r requirements.txt on the Pi.
- Use ./setup_pi_lite.sh for Pi setup.
- Use ./run_epaper.sh to start the e-paper app.
- Books can be uploaded from Edit books -> Add books.

## Pico button controller

The Raspberry Pi Pico acts as a USB keyboard.

Button mapping:

- GP15 -> w + Enter -> up
- GP11 -> s + Enter -> down
- GP7 -> e + Enter -> select
- GP3 -> q + Enter -> back
- GP16 -> x + Enter -> sleep/exit

Each button connects between its Pico GPIO pin and GND.

To set up the Pico on a new Pi:

1. Install CircuitPython on the Pico.
2. Plug the Pico into the Pi.
3. Run:

./scripts/setup_pico_keyboard.sh

The Pico can stay plugged in from boot. If the Pico does not reload immediately after setup, reboot the Pi.


## Reader zoom controls

While reading:

- Tap SELECT -> bookmark page
- Hold SELECT + UP -> zoom in
- Hold SELECT + DOWN -> zoom out

Zoom is handled by the Pico sending serial commands `ZOOM_IN` and `ZOOM_OUT`.


## Auto-start on boot

To make DillyKindle start automatically when the Pi boots:

./scripts/install_autostart.sh
sudo reboot

Useful commands:

sudo systemctl status dillykindle.service
sudo systemctl stop dillykindle.service
sudo systemctl start dillykindle.service
sudo systemctl disable dillykindle.service
journalctl -u dillykindle.service -n 80 --no-pager


## GP16 app sleep

The Pico GP16 button is an app-level sleep toggle, not the real power-off control.

- Hold GP16 for 1.2 seconds -> show DillyKindle sleep screen
- Hold GP16 again for 1.2 seconds -> wake back into the app
- PiSugar custom button long tap -> true safe shutdown
