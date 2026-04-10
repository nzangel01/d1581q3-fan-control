# 🌪️ D-1581Q3 Smart Fan Control (Proxmox/Linux)

A Python-based smart fan control system for the **D-1581Q3** motherboard, designed to manage CPU and GPU (NVIDIA Tesla P4) fan speeds based on real-time temperatures.

ระบบควบคุมพัดลมอัจฉริยะสำหรับเมนบอร์ด **D-1581Q3** เพื่อจัดการความร้อนของ CPU และ GPU

---

## ✨ What's New in v2

- **Auto-detect hwmon path** — ไม่ hardcode `/sys/class/hwmon/hwmonX` อีกต่อไป ใช้ driver name แทน
- **Logging** — บันทึก log ลง `/var/log/fan_control.log` พร้อม console output
- **Safety limit 80°C** — เกิน 80°C ทั้ง CPU/GPU จะ full blast (255) ทันที
- **Signal handlers** — graceful shutdown คืน fan กลับ auto mode เมื่อ `systemctl stop`
- **Specific exception handling** — ไม่ใช้ bare `except: pass` อีกต่อไป
- **Timeout** — nvidia-smi / sensors ไม่ค้างเกิน 5 วินาที
- **Config dict** — ปรับ threshold ได้ที่เดียวบนสุดของไฟล์

---

## 🌡️ Fan Curve (v2)

| Zone | GPU | CPU | PWM |
|------|-----|-----|-----|
| Quiet | < 35°C | < 45°C | 80 |
| Ramp | 35–65°C | 45–65°C | 80 → 255 |
| Full | ≥ 65°C | ≥ 65°C | 255 |
| **Safety** | **> 80°C** | **> 80°C** | **255 (CRITICAL log)** |

---

## 📦 Installation

### Requirements
```bash
# Debian/Ubuntu (Proxmox)
apt-get install -y lm-sensors python3
modprobe nct6775

# Arch/CachyOS
pacman -S lm_sensors python
modprobe nct6775
```

### Deploy
```bash
git clone https://github.com/nzangel01/d1581q3-fan-control
cd d1581q3-fan-control
cp fan_control_v2.py /root/smart_fan_control.py
```

### Systemd Service
```bash
cat << 'EOF' > /etc/systemd/system/fan_control.service
[Unit]
Description=D-1581Q3 Smart Fan Control
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /root/smart_fan_control.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now fan_control
systemctl status fan_control
```

---

## 🖥️ Tested Hardware

| Machine | Board | CPU | GPU |
|---------|-------|-----|-----|
| Sheffy (.7) | D-1581Q3 | Xeon D-1581 | 4x Tesla P4 |
| PVE (.222) | D-1581Q3 | Xeon D-1581 | 3x Tesla P4 |

Driver: **nct6775** | hwmon path: auto-detected

---

**Created by nzangel01**
