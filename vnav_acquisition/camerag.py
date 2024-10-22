import cv2

def get_camera_indices():
    indices = []
    for i in range(4):  # İlk 4 indeksi kontrol ediyoruz, daha fazlasını deneyebilirsiniz
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            indices.append(i)
            cap.release()
    return indices

def show_live_cameras(camera_indices):
    # Laptop kamerasını hariç tutuyoruz
    camera_indices = [i for i in camera_indices if i != 0]
    
    # En fazla 2 kamerayı gösteriyoruz
    if len(camera_indices) < 1:
        print("2 kamera bulunamadı, bağlantıları kontrol edin.")
        return

    # İlk iki kamerayı alıyoruz
    camera_indices = camera_indices[:1]
    caps = [cv2.VideoCapture(i) for i in camera_indices]

    while True:
        frames = []
        for cap in caps:
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
            else:
                frames.append(None)
        
        # Tüm kameraların görüntülerini aynı pencerede göster
        for i, frame in enumerate(frames):
            if frame is not None:
                cv2.imshow(f"Camera {camera_indices[i]}", frame)
        
        # Çıkmak için 'q' tuşuna bas
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Tüm kaynakları serbest bırak
    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    indices = get_camera_indices()
    print(f"Bulunan kameralar: {indices}")
    show_live_cameras(indices)
