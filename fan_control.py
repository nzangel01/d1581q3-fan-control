import time
import subprocess
import os

# --- Config ---
HWMON_PATH = '/sys/class/hwmon/hwmon3'
# GPU Control (fan1)
GPU_PWM = os.path.join(HWMON_PATH, 'pwm1')
GPU_ENABLE = os.path.join(HWMON_PATH, 'pwm1_enable')
# CPU Control (fan2)
CPU_PWM = os.path.join(HWMON_PATH, 'pwm2')
CPU_ENABLE = os.path.join(HWMON_PATH, 'pwm2_enable')

def get_gpu_temp():
    try:
        res = subprocess.check_output(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits']).decode()
        return int(res.strip())
    except: return 45

def get_cpu_temp():
    try:
        res = subprocess.check_output(['sensors', 'coretemp-isa-0000']).decode()
        for line in res.split('\n'):
            if 'Package id 0' in line:
                return int(float(line.split('+')[1].split('°')[0]))
    except: return 40
    return 40

def set_fan(enable_file, pwm_file, val):
    try:
        with open(enable_file, 'w') as f: f.write('1')
        with open(pwm_file, 'w') as f: f.write(str(int(val)))
    except: pass

def calc_pwm(temp, t_min=40, t_max=75, p_min=80, p_max=255):
    if temp < t_min: return p_min
    if temp > t_max: return p_max
    return p_min + (temp - t_min) * (p_max - p_min) / (t_max - t_min)

print('D-1581Q3 Smart Fan Control Active...')
try:
    while True:
        # GPU Control
        g_temp = get_gpu_temp()
        set_fan(GPU_ENABLE, GPU_PWM, calc_pwm(g_temp))
        # CPU Control
        c_temp = get_cpu_temp()
        set_fan(CPU_ENABLE, CPU_PWM, calc_pwm(c_temp, t_min=45, t_max=80))
        time.sleep(5)
except KeyboardInterrupt:
    with open(GPU_ENABLE, 'w') as f: f.write('5')
    with open(CPU_ENABLE, 'w') as f: f.write('5')
