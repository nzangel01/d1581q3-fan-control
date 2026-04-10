#!/usr/bin/env python3
import time
import os
import sys
import signal
import logging
import subprocess
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('/var/log/fan_control.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

CONFIG = {
    'hwmon_path': '/sys/class/hwmon',
    'gpu': {'temp_min': 35, 'temp_max': 65, 'pwm_min': 80, 'pwm_max': 255},
    'cpu': {'temp_min': 45, 'temp_max': 65, 'pwm_min': 80, 'pwm_max': 255},
    'safety_max_temp': 80,
    'check_interval': 3,
}

def find_hwmon():
    for p in Path('/sys/class/hwmon').glob('hwmon*'):
        name = (p / 'name').read_text().strip() if (p / 'name').exists() else ''
        if 'nct6775' in name or 'coretemp' in name:
            return str(p)
    logger.warning('HWMon not found, using default')
    return '/sys/class/hwmon/hwmon2'

def get_gpu_temp():
    try:
        res = subprocess.check_output(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'], timeout=5)
        temps = [int(t.strip()) for t in res.decode().strip().split('\n') if t.strip()]
        return max(temps) if temps else 45
    except FileNotFoundError:
        logger.warning('nvidia-smi not found, GPU monitoring disabled')
        return None
    except Exception as e:
        logger.error(f'GPU temp read error: {e}')
        return None

def get_cpu_temp():
    try:
        res = subprocess.check_output(['sensors', 'coretemp-isa-0000'], timeout=5).decode()
        for line in res.split('\n'):
            if 'Package id 0' in line:
                return int(float(line.split('+')[1].split('°')[0]))
    except FileNotFoundError:
        logger.error('lm-sensors not found')
        return None
    except Exception as e:
        logger.error(f'CPU temp read error: {e}')
    return None

def set_fan(hwmon_path, fan_num, val):
    enable_file = Path(hwmon_path) / f'pwm{fan_num}_enable'
    pwm_file = Path(hwmon_path) / f'pwm{fan_num}'
    
    if not enable_file.exists() or not pwm_file.exists():
        return False
    
    try:
        enable_file.write_text('1')
        pwm_file.write_text(str(int(val)))
        return True
    except Exception as e:
        logger.error(f'Fan {fan_num} write error: {e}')
        return False

def calc_pwm(temp, config):
    if temp < config['temp_min']:
        return config['pwm_min']
    if temp > config['temp_max']:
        return config['pwm_max']
    return config['pwm_min'] + (temp - config['temp_min']) * (config['pwm_max'] - config['pwm_min']) / (config['temp_max'] - config['temp_min'])

def shutdown_handler(signum, frame):
    logger.info('Shutting down gracefully...')
    for fan_num in [1, 2]:
        try:
            (Path(CONFIG['hwmon_path']) / f'pwm{fan_num}_enable').write_text('5')
        except: pass
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)

def main():
    hwmon_path = find_hwmon()
    logger.info(f'D-1581Q3 Fan Control v2 started on {hwmon_path}')
    
    while True:
        gpu_temp = get_gpu_temp()
        if gpu_temp is not None:
            if gpu_temp > CONFIG['safety_max_temp']:
                logger.critical(f'GPU OVERHEAT {gpu_temp}°C! Full fan speed!')
                set_fan(hwmon_path, 1, 255)
            else:
                gpu_pwm = calc_pwm(gpu_temp, CONFIG['gpu'])
                set_fan(hwmon_path, 1, gpu_pwm)
                logger.debug(f'GPU: {gpu_temp}°C -> PWM {gpu_pwm}')
        else:
            logger.debug('GPU monitoring disabled')
        
        cpu_temp = get_cpu_temp()
        if cpu_temp is not None:
            if cpu_temp > CONFIG['safety_max_temp']:
                logger.critical(f'CPU OVERHEAT {cpu_temp}°C! Full fan speed!')
                set_fan(hwmon_path, 2, 255)
            else:
                cpu_pwm = calc_pwm(cpu_temp, CONFIG['cpu'])
                set_fan(hwmon_path, 2, cpu_pwm)
                logger.debug(f'CPU: {cpu_temp}°C -> PWM {cpu_pwm}')
        
        time.sleep(CONFIG['check_interval'])

if __name__ == '__main__':
    main()