#
#import ALL THE LIBRARIES
#
import serial
import RPi.GPIO as GPIO
from as7265x import AS7265X
from smbus import SMBus
import time
import sysimport csv
from datetime import datetime
import board
import adafruit_bme680


collecting_data = True

def signal_handler(sig, frame):
    """Handle Ctrl+C to stop data collection gracefully"""
    global collecting_data
    print("\nStopping data collection...")
    collecting_data = False

#set up bme 680
def setup_bme688():
  i2c = board.I2C()  # uses board.SCL and board.SDA
  # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
  bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)
  bme680.sea_level_pressure = 1013.25
  return bme680

#set up hyperspectral AS7265
def setup_AS7265():
  i2c = SMBus(1)
  sensor = AS7265X(i2c)
  if not sensor.begin():
    print("Error: Device not connected.")
    sys.exit()
    sensor.softReset()
    time.sleep(2)
    sensor.setMeasurementMode(2)
    sensor.enableBulb(0)
    sensor.enableBulb(1)
    sensor.enableBulb(2)
    sensor.disableIndicator()
    sensor.setIntegrationCycles(1)

return sensor

#
# create file to save data function
#
#
#
def create_csv_spectral(filename="hyperspectral_data.csv"):
  spectral_headers = ['timestamp','loop count','A_cal', 'A_raw', 'B_cal', 'B_raw', 'C_cal', 'C_raw', 
        'D_cal', 'D_raw', 'E_cal', 'E_raw', 'F_cal', 'F_raw',
        'G_cal', 'G_raw', 'H_cal', 'H_raw', 'I_cal', 'I_raw',
        'J_cal', 'J_raw', 'K_cal', 'K_raw', 'L_cal', 'L_raw',
        'R_cal', 'R_raw', 'S_cal', 'S_raw', 'T_cal', 'T_raw',
        'U_cal', 'U_raw', 'V_cal', 'V_raw', 'W_cal', 'W_raw']
  bme_headers = ['timestamp,'loop_count", temperature','gas,'humidity','pressure','altitude']
                 
  with open("hyperspectral_data.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(spectral_headers)
    
  with open("bme680_data.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(bme_headers)
  return "hyperspectral_data.csv", "bme680_data.csv"


####
# create file to save data function
###

def collect_bme680_data(bme_sensor, temperature_offset=-5):
    """Collect data from BME680 sensor"""
    return {
        'temperature': bme_sensor.temperature + temperature_offset,
        'gas': bme_sensor.gas,
        'humidity': bme_sensor.relative_humidity,
        'pressure': bme_sensor.pressure,
        'altitude': bme_sensor.altitude
    }

#
#
# collect data
#
#

def collect_spectral_data(sensor, loop_count):
    """Collect data from sensor and return as dictionary"""
    timestamp = time.time()
    
    # Wait for data to be available
    while not sensor.dataAvailable():
        time.sleep(0.01)
    
    return {
        'timestamp': timestamp,
        'loop_count': loop_count,
        'A_cal': sensor.getCalibratedA(), 'A_raw': sensor.getA(),
        'B_cal': sensor.getCalibratedB(), 'B_raw': sensor.getB(),
        'C_cal': sensor.getCalibratedC(), 'C_raw': sensor.getC(),
        'D_cal': sensor.getCalibratedD(), 'D_raw': sensor.getD(),
        'E_cal': sensor.getCalibratedE(), 'E_raw': sensor.getE(),
        'F_cal': sensor.getCalibratedF(), 'F_raw': sensor.getF(),
        'G_cal': sensor.getCalibratedG(), 'G_raw': sensor.getG(),
        'H_cal': sensor.getCalibratedH(), 'H_raw': sensor.getH(),
        'I_cal': sensor.getCalibratedI(), 'I_raw': sensor.getI(),
        'J_cal': sensor.getCalibratedJ(), 'J_raw': sensor.getJ(),
        'K_cal': sensor.getCalibratedK(), 'K_raw': sensor.getK(),
        'L_cal': sensor.getCalibratedL(), 'L_raw': sensor.getL(),
        'R_cal': sensor.getCalibratedR(), 'R_raw': sensor.getR(),
        'S_cal': sensor.getCalibratedS(), 'S_raw': sensor.getS(),
        'T_cal': sensor.getCalibratedT(), 'T_raw': sensor.getT(),
        'U_cal': sensor.getCalibratedU(), 'U_raw': sensor.getU(),
        'V_cal': sensor.getCalibratedV(), 'V_raw': sensor.getV(),
        'W_cal': sensor.getCalibratedW(), 'W_raw': sensor.getW()
    }
  
def save_spectral_data_to_csv(data, filename):
    """Save data dictionary to CSV file"""
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            data['timestamp'], data['loop_count'],
            data['A_cal'], data['A_raw'], data['B_cal'], data['B_raw'],
            data['C_cal'], data['C_raw'], data['D_cal'], data['D_raw'],
            data['E_cal'], data['E_raw'], data['F_cal'], data['F_raw'],
            data['G_cal'], data['G_raw'], data['H_cal'], data['H_raw'],
            data['I_cal'], data['I_raw'], data['J_cal'], data['J_raw'],
            data['K_cal'], data['K_raw'], data['L_cal'], data['L_raw'],
            data['R_cal'], data['R_raw'], data['S_cal'], data['S_raw'],
            data['T_cal'], data['T_raw'], data['U_cal'], data['U_raw'],
            data['V_cal'], data['V_raw'], data['W_cal'], data['W_raw']
        ])

def save_gps_data_to_csv(data,filename):
  """Save BME680 data dictionary to CSV file"""
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            data['timestamp'], data['loop_count'],
            data['temperature'], data['gas'], 
            data['humidity'], data['pressure'], data['altitude']
        ])

def main():
    global collecting_data
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create CSV file with headers
    filename = create_csv_with_headers()
    
    # Set up sensor
    sensor = setup_sensor()
    
    print("Data collection started. Press Ctrl+C to stop...")
    
    loop_count = 0
    try:
        while collecting_data:
            # Collect data from sensor
            data = collect_sensor_data(sensor, loop_count)
            
            # Save to CSV
            save_data_to_csv(data, filename)
            
            # Print progress (optional)
            print(f"Loop {loop_count}: Data collected and saved at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            loop_count += 1
            # Optional: Add small delay between readings if needed
            # time.sleep(0.1)
            
    except Exception as e:
        print(f"Error during data collection: {e}")
    
    finally:
        # Clean up - turn off bulbs
        sensor.disableBulb(0)
        sensor.disableBulb(1)
        sensor.disableBulb(2)
        
        print(f"Data collection stopped. Total readings: {loop_count}")
        print(f"Data saved to: {filename}")

if __name__ == "__main__":
    main()
