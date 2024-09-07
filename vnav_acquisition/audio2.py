import pyaudio
import numpy as np
import matplotlib.pyplot as plt

# Parametreler
FORMAT = pyaudio.paInt16  # Veri formatı
CHANNELS = 1              # Mono
RATE = 44100              # Örnekleme oranı
CHUNK = 1024              # Her defasında okunacak veri boyutu (buffer)

# PyAudio nesnesi oluşturma
p = pyaudio.PyAudio()

# Ses akışı başlatma
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Grafik oluşturma
plt.ion()  # Interaktif mod açma
fig, ax = plt.subplots()

x = np.arange(0, 2 * CHUNK, 2)  # X ekseni için veri noktaları
line, = ax.plot(x, np.random.rand(CHUNK))

ax.set_ylim(-32768, 32767)
ax.set_xlim(0, CHUNK)

# Tüm veriyi saklamak için liste
all_data = []

print("Canlı ses gösteriliyor...")

try:
    while True:
        # Veri okuma
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        
        # Gelen veriyi listeye ekleme
        all_data.extend(data)
        
        # Çizgiyi güncelleme
        line.set_ydata(data)
        ax.set_xlim(0, len(all_data))
        ax.set_ylim(-32768, 32767)
        
        # Tüm veriyi yeniden çizme
        ax.clear()
        ax.plot(np.arange(len(all_data)), all_data)
        
        plt.draw()
        plt.pause(0.01)
except KeyboardInterrupt:
    print("Program durduruldu.")

# Temizleme
stream.stop_stream()
stream.close()
p.terminate()

# Çizimi durdur
plt.ioff()
plt.show()
