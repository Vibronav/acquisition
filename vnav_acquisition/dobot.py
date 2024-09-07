import threading
from dobot_api import DobotApiDashboard, DobotApiMove
from time import sleep
import time

PARAMS = 0  # PARAMS variable can be set to 0 or 1

def connect_robot():
    try:
        ip = "192.168.1.6"
        dashboard_p = 29999
        move_p = 30003
        feed_p = 30004
        print("Connecting to the robot...")
        dashboard = DobotApiDashboard(ip, dashboard_p)
        move = DobotApiMove(ip, move_p)
        print("Connection successful!")
        return dashboard, move
    except Exception as e:
        print("Connection failed :(")
        raise e

def enable_robot(dashboard):
    try:
        print("Enabling the robot...")
        if PARAMS == 0:
            dashboard.EnableRobot()
        else:
            load = 0.1
            centerX = 0.1
            centerY = 0.1
            centerZ = 0.1
            dashboard.EnableRobot(load, centerX, centerY, centerZ)
        print("Robot enabled!")
    except Exception as e:
        print("Error during robot enabling :(")
        raise e

def move_to_position(dashboard, move, position):
    try:
        x, y, z, r = position
        print(f"Moving to position: ({x}, {y}, {z}, {r})")
        # Setting movement parameters for smooth and linear motion
        userparam = "User=0"
        toolparam = "Tool=0"

        # Hız ve ivme ayarlarını DobotApiDashboard üzerinden yapın
        dashboard.SpeedL(100)  # SpeedL komutunu doğru şekilde çağır
        dashboard.AccL(1)      # AccL komutunu doğru şekilde çağır
        dashboard.SpeedFactor(25) # genel speed kısmı

        speedlparam = "SpeedL=15"  # Adjust the speed as needed
        acclparam = "AccL=1"  # Adjust the acceleration as needed
        cpparam = "CP=100"  # Continuous Path

        move.MovL(x, y, z, r, userparam, toolparam, speedlparam, acclparam, cpparam)
        sleep(1)  # Wait for the movement to complete
        print("Movement completed.")
    except Exception as e:
        print(f"Error during movement: {e}")
        raise e

if __name__ == '__main__':
    dashboard, move = connect_robot()

    try:
        enable_robot(dashboard)

        # İlk pozisyonlar
        P1 = (350, 0, 20, 0)  # X, Y, Z, R
        P2 = (P1[0], 0, 20, 0)  # X, Y, Z, R
        P3 = (P1[0], 0, -22, 0)  # X, Y, Z, R

        # İlk hareketler
        move_to_position(dashboard, move, P1)
        move_to_position(dashboard, move, P2)
        move_to_position(dashboard, move, P3)
        move_to_position(dashboard, move, P1)

        # İlk hareket setini tekrarla
        for _ in range(2):
            P1 = (P1[0] + 5, P1[1], P1[2], P1[3])
            P2 = (P1[0], P2[1], P2[2], P2[3])
            P3 = (P1[0], P3[1], P3[2], P3[3])
            print(f"İlk döngü - P1: {P1}, P2: {P2}, P3: {P3}")
            move_to_position(dashboard, move, P1)
            move_to_position(dashboard, move, P2)
            move_to_position(dashboard, move, P3)
            move_to_position(dashboard, move, P1)  

    except Exception as e:
        print(f"İlk hareket sırasında hata oluştu: {e}")

    # İkinci hareket seti
    try:  

        # Yeni pozisyonlar ikinci döngü için
        P1 = (350, -25, 20, 0)  # X, Y, Z, R
        P2 = (P1[0], -25, 20, 0)  # X, Y, Z, R
        P3 = (P1[0], -25, -22, 0)  # X, Y, Z, R

        # Kontrol için pozisyonları yazdır
        print(f"İkinci döngü başlangıç - P1: {P1}, P2: {P2}, P3: {P3}")

        # İkinci hareket seti
        move_to_position(dashboard, move, P1)
        move_to_position(dashboard, move, P2)
        move_to_position(dashboard, move, P3)
        move_to_position(dashboard, move, P1)

        # İkinci hareket setini tekrarla
        print("İkinci döngüye giriliyor...")
        for _ in range(2):
            P1 = (P1[0] + 5, P1[1], P1[2], P1[3])
            P2 = (P1[0], P2[1], P2[2], P2[3])
            P3 = (P1[0], P3[1], P3[2], P3[3])
            print(f"İkinci döngü - P1: {P1}, P2: {P2}, P3: {P3}")
            move_to_position(dashboard, move, P1)
            move_to_position(dashboard, move, P2)
            move_to_position(dashboard, move, P3)
            move_to_position(dashboard, move, P1)

    except Exception as e:
        print(f"İkinci hareket sırasında hata oluştu: {e}")
        
    finally:
        # En son robotu devre dışı bırak
        try:
            dashboard.DisableRobot()
            print("Robot devre dışı bırakıldı.")
        except Exception as final_disable_error:
            print(f"Robotu devre dışı bırakma sırasında hata oluştu: {final_disable_error}")


