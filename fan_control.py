import time
import subprocess
import os

# --- Config ---
HWMON_PATH = '/sys/class/hwmon/hwmon2'
GPU_PWM = os.path.join(HWMON_PATH, 'pwm1')
GPU_ENABLE = os.path.join(HWMON_PATH, 'pwm1_enable')
CPU_PWM = os.path.join(HWMON_PATH, 'pwm2')
CPU_ENABLE = os.path.join(HWMON_PATH, 'pwm2_enable')

def get_gpu_temp():
    try:
        res = subprocess.check_output(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits']).decode()
        temps = [int(t.strip()) for t in res.strip().split('\n') if t.strip()]
        return max(temps) if temps else 45
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
        if not os.path.exists(enable_file): return
        with open(enable_file, 'w') as f: f.write('1')
        with open(pwm_file, 'w') as f: f.write(str(int(val)))
    except: pass

def calc_pwm(temp, t_min=40, t_max=65, p_min=120, p_max=255):
    # Aggressive curve for Tesla P4 x3
    if temp < t_min: return p_min
    if temp > t_max: return p_max
    return p_min + (temp - t_min) * (p_max - p_min) / (t_max - t_min)

print('D-1581Q3 Aggressive Triple GPU Fan Control Active...')
try:
    while True:
        g_max_temp = get_gpu_temp()
        # Scale fan faster: 40C -> 120 (Quiet), 65C -> 255 (Full)
        gpu_pwm_val = calc_pwm(g_max_temp, t_min=40, t_max=65, p_min=120)
        set_fan(GPU_ENABLE, GPU_PWM, gpu_pwm_val)
        
        c_temp = get_cpu_temp()
        cpu_pwm_val = calc_pwm(c_temp, t_min=45, t_max=75, p_min=100)
        set_fan(CPU_ENABLE, CPU_PWM, cpu_pwm_val)
        
        time.sleep(3) # Faster check (3s instead of 5s)
except KeyboardInterrupt:
    try:
        with open(GPU_ENABLE, 'w') as f: f.write('5')
        with open(CPU_ENABLE, 'w') as f: f.write('5')
    except: pass
