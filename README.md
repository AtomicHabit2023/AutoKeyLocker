# 🔐 Auto Key Locker (ESP32 + MicroPython)

This project controls a physical key locker system using ESP32, MicroPython, and I2C peripherals (LCD & Keypad).

---

## 🧠 Features

- I2C Keypad for code input
- I2C LCD for status display
- Password verification with optional `passwords.json` storage
- Solenoid or servo control for locking
- Simple and robust versions included

---

## 📁 File Structure

| File            | Description                                |
|-----------------|--------------------------------------------|
| `main.py`       | Main application logic                     |
| `boot.py`       | Optional ESP32 boot behavior               |
| `i2c_keypad.py` | Keypad interface via I2C                   |
| `i2c_lcd.py`    | LCD display interface (I2C)                |
| `lcd_api.py`    | Helper base for LCD drivers                |
| `verification.py` | Handles password check logic             |
| `robust.py`     | (Optional) Robust version or testing code  |
| `simple.py`     | (Optional) Simpler variant for testing     |
| `passwords.json`| Password storage file                      |
| `README.md`     | This file                                  |

---

## 📦 Version Info

**Ver 1.0 – Recovered from ESP32 on 2025-05-24**  
Tag: `v1.0`

---

## 🚀 To Run

1. Connect ESP32 via USB
2. Use Thonny to upload:
   - `main.py`, `boot.py`, all modules
3. Reset ESP32 or run via REPL

---

## 💡 Future Ideas

- Add Wi-Fi OTA unlocking via web
- Add encryption for password storage
- Battery status or timeout buzzer

---

## 🙏 Credit

Created by Joe  
ESP32 + MicroPython lover ❤️
