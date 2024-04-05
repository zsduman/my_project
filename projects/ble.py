import smbus
import time
import dbus

# D-Bus bağlantısı oluşturma
bus = dbus.SystemBus()

# BlueZ servis adı ve arabirim adı
BLUEZ_SERVICE_NAME = 'org.bluez'
ADAPTER_INTERFACE = 'org.bluez.Adapter1'

# Bluetooth aygıtının yolunu belirtin
adapter_path = '/org/bluez/hci0'  

# Bluetooth aygıtının objesini alın
adapter_obj = bus.get_object(BLUEZ_SERVICE_NAME, adapter_path)

# Bluetooth aygıtı için arabirimleri tanımlayın
adapter_props = dbus.Interface(adapter_obj, dbus.PROPERTIES_IFACE)
adapter_if = dbus.Interface(adapter_obj, ADAPTER_INTERFACE)

# Bluetooth aygıtını etkinleştirin
adapter_props.Set(ADAPTER_INTERFACE, 'Powered', dbus.Boolean(True))

# Get I2C bus
bus_i2c = smbus.SMBus(1)

# Fonksiyon: Sıcaklık ve nem verilerini oku
def read_sensor_data():
    # SHT31 address, 0x44(68)
    bus_i2c.write_i2c_block_data(0x44, 0x2C, [0x06])
    time.sleep(0.5)
    # SHT31 address, 0x44(68)
    # Read data back from 0x00(00), 6 bytes
    # Temp MSB, Temp LSB, Temp CRC, Humidity MSB, Humidity LSB, Humidity CRC
    data = bus_i2c.read_i2c_block_data(0x44, 0x00, 6)
    # Convert the data
    temp = data[0] * 256 + data[1]
    cTemp = -45 + (175 * temp / 65535.0)
    fTemp = -49 + (315 * temp / 65535.0)
    humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
    return cTemp, fTemp, humidity

# Reklam verisini ayarlayın
def set_advertisement_data(cTemp, fTemp, humidity):
    manufacturer_data = bytes([0xFF, 0x12, 0x34, int(cTemp), int(fTemp), int(humidity)])  # Sıcaklık ve nem verilerini reklam verisine ekleyin
    advertise_data = {
        0x01: dbus.Array([dbus.Byte(0x06)], signature='y'),        # Flags
        0x03: dbus.Array([dbus.Byte(0x0D), dbus.Byte(0x18)], signature='y'),  # Complete list of 16-bit Service Class UUIDs
        0xFF: dbus.Array([dbus.Byte(0xFF)] + list(manufacturer_data), signature='y')  # Manufacturer specific data
    }
    adapter_if.SetDiscoveryFilter(advertise_data)

# Ana döngü
while True:
    cTemp, fTemp, humidity = read_sensor_data()  # Sıcaklık ve nem verilerini oku
    print ("Temperature in Celsius is : %.2f C" % cTemp)
    print ("Temperature in Fahrenheit is : %.2f F" % fTemp)
    print ("Relative Humidity is : %.2f %%RH" % humidity)
    set_advertisement_data(cTemp, fTemp, humidity)  # Reklam verisini ayarla
    time.sleep(60)  # 60 saniye bekleyin ve tekrar okuyun
