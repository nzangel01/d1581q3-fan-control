import time
import subprocess
import os

# --- Config ---
# Path for nct6779 controller on machine .222
HWMON_PATH = '/sys/class/hwmon/hwmon2'

# GPU Control (fan1)
GPU_PWM = os.path.join(HWMON_PATH, 'pwm1')
GPU_ENABLE = os.path.join(HWMON_PATH, 'pwm1_enable')

# CPU Control (fan2)
CPU_PWM = os.path.join(HWMON_PATH, 'pwm2')
CPU_ENABLE = os.path.join(HWMON_PATH, 'pwm2_enable')

def get_gpu_temp():
    try:
        # Query temperatures for ALL GPUs
        res = subprocess.check_output(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits']).decode()
        # Get the maximum temperature among all GPUs
        temps = [int(t.strip()) for t in res.strip().split('\n') if t.strip()]
        return max(temps) if temps else 45
    except Exception as e:
        print(f"Error getting GPU temp: {e}")
        return 45

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
    except Exception as e:
        pass

def calc_pwm(temp, t_min=40, t_max=70, p_min=100, p_max=255):
    # Quiet mode below t_min, full blast above t_max
    if temp < t_min: return p_min
    if temp > t_max: return p_max
    return p_min + (temp - t_min) * (p_max - p_min) / (t_max - t_min)

print('D-1581Q3 Triple GPU Smart Fan Control Active...')
try:
    while True:
        # GPU Control - Now monitors all 3 Tesla P4s
        g_max_temp = get_gpu_temp()
        gpu_pwm_val = calc_pwm(g_max_temp, t_min=40, t_max=75, p_min=110) # Base 110 (~1600 RPM)
        set_fan(GPU_ENABLE, GPU_PWM, gpu_pwm_val)
        
        # CPU Control
        c_temp = get_cpu_temp()
        cpu_pwm_val = calc_pwm(c_temp, t_min=45, t_max=80, p_min=100)
        set_fan(CPU_ENABLE, CPU_PWM, cpu_pwm_val)
        
        # Log status every 30 seconds to keep it clean
        # print(f"GPU Max Temp: {g_max_temp}C -> PWM: {int(gpu_pwm_val)} | CPU Temp: {c_temp}C -> PWM: {int(cpu_pwm_val))}")
        
        time.sleep(5)
except KeyboardInterrupt:
    print("\nExiting fan control...")
    # Set back to Auto (usually 5 or 2 depending on board)
    try:
        with open(GPU_ENABLE, 'w') as f: f.write('5')
        with open(CPU_ENABLE, 'w') as f: f.write('5')
    except: pass