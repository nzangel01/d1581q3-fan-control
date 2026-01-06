# 🌪️ D-1581Q3 Smart Fan Control (Proxmox/Linux)

A Python-based smart fan control system for the **D-1581Q3** motherboard, specifically designed to manage CPU and External GPU (like NVIDIA Tesla P4) fan speeds based on real-time temperatures.
ระบบควบคุมพัดลมอัจฉริยะสำหรับเมนบอร์ด **D-1581Q3** เพื่อจัดการความร้อนของ CPU และ GPU

---

## 🇹🇭 ภาษาไทย (Thai)

โปรเจกต์นี้ช่วยแก้ปัญหาพัดลมหมุนคงที่หรือเสียงดังเกินไป โดยจะปรับรอบพัดลมตามอุณหภูมิของฮาร์ดแวร์จริง

### คุณสมบัติ
- **GPU Fan (fan1):** ควบคุมตามอุณหภูมิการ์ดจอ NVIDIA (Tesla P4)
- **CPU Fan (fan2):** ควบคุมตามอุณหภูมิ CPU Package
- **Auto-Scale:** พัดลมจะค่อยๆ เร่งความเร็วตามความร้อน (Linear Scaling)
- **Systemd Integration:** ทำงานเป็นเบื้องหลังทันทีที่เปิดเครื่อง

### วิธีติดตั้ง
1. Clone โปรเจกต์นี้
2. รันคำสั่งติดตั้งไดรเวอร์และเริ่มระบบ:
   \`\`\`bash
   apt-get install -y lm-sensors
   modprobe nct6775
   cp fan_control.py /root/smart_fan_control.py
   # สร้าง Service ตามคู่มือในไฟล์
   \`\`\`

---

## 🇺🇸 English

### Key Features
- **Independent Control:** Manages fan1 (GPU) and fan2 (CPU) based on their respective temperatures.
- **Silent & Safe:** Runs at lower speeds when idle and ramps up during heavy AI loads (Ollama).
- **Tested Hardware:** Optimized for **Xeon D-1581 (D-1581Q3 Board)** using the **nct6775** driver.

---
**Created by nzangel01**
