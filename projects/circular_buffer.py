from collections import deque
import smbus
import time

# Dairesel arabellek boyutu
BUFFER_SIZE = 10

# Hareketli medyan filtresi fonksiyonu
def moving_median(samples):
    sorted_samples = sorted(samples)
    n = len(sorted_samples)
    if n == 0:
        return None
    if n % 2 == 1:
        return sorted_samples[n//2]
    else:
        mid = n//2
        return (sorted_samples[mid-1] + sorted_samples[mid]) / 2

# Sensörden veri okuma fonksiyonu
def read_sensor():
    # Get I2C bus
    bus = smbus.SMBus(1)

    # SHT31 address, 0x44(68)
    bus.write_i2c_block_data(0x44, 0x2C, [0x06])
    time.sleep(0.5)

    # SHT31 address, 0x44(68)
    # Read data back from 0x00(00), 6 bytes
    # Temp MSB, Temp LSB, Temp CRC, Humididty MSB, Humidity LSB, Humidity CRC
    data = bus.read_i2c_block_data(0x44, 0x00, 6)

    # Convert the data
    temp = data[0] * 256 + data[1]
    cTemp = -45 + (175 * temp / 65535.0)
    fTemp = -49 + (315 * temp / 65535.0)
    humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
    
    return cTemp, fTemp, humidity

# Dairesel arabellek oluştur
buffer = deque(maxlen=BUFFER_SIZE)

try:
    while True:
        # Sensörden veri oku
        cTemp, fTemp, humidity = read_sensor()
        
        # Veriyi filtrele ve medyanını al
        cTemp_median = moving_median([data[0] for data in buffer])
        fTemp_median = moving_median([data[1] for data in buffer])
        humidity_median = moving_median([data[2] for data in buffer])
        
        # Sonuçları arabelleğe ekle
        buffer.append((cTemp, fTemp, humidity))
        
        # Sonuçları yazdır
        print("Celsius Temperature Median:", cTemp_median)
        print("Fahrenheit Temperature Median:", fTemp_median)
        print("Humidity Median:", humidity_median)
        
        # Bekleme süresi
        time.sleep(1)

except KeyboardInterrupt:
    print("Program terminated by user.")

