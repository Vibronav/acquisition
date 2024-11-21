from API.dobot_api import DobotApiDashboard, DobotApi, DobotApiMove, MyType, alarmAlarmJsonFile
import numpy as np
import re
import threading
from time import sleep

# Global variables
current_actual = None
algorithm_queue = None
enableStatus_robot = None
robotErrorState = False
globalLockValue = threading.Lock()


def ConnectRobot():
    try:
        ip = "192.168.1.6"
        dashboardPort = 29999
        movePort = 30003
        feedPort = 30004
        print("Connecting to the robot...")
        dashboard = DobotApiDashboard(ip, dashboardPort)
        move = DobotApiMove(ip, movePort)
        feed = DobotApi(ip, feedPort)
        print("Connection successful!")
        return dashboard, move, feed
    except Exception as e:
        print("Connection failed.")
        raise e


def RunPoint(move: DobotApiMove, point_list: list):
    move.MovL(point_list[0], point_list[1], point_list[2], point_list[3])


def GetFeed(feed: DobotApi):
    global current_actual, algorithm_queue, enableStatus_robot, robotErrorState
    hasRead = 0
    while True:
        data = bytes()
        while hasRead < 1440:
            temp = feed.socket_dobot.recv(1440 - hasRead)
            if len(temp) > 0:
                hasRead += len(temp)
                data += temp
        hasRead = 0
        feedInfo = np.frombuffer(data, dtype=MyType)
        if hex((feedInfo['test_value'][0])) == '0x123456789abcdef':
            globalLockValue.acquire()
            current_actual = feedInfo["tool_vector_actual"][0]
            algorithm_queue = feedInfo['isRunQueuedCmd'][0]
            enableStatus_robot = feedInfo['EnableStatus'][0]
            robotErrorState = feedInfo['ErrorStatus'][0]
            globalLockValue.release()
        sleep(0.001)


def WaitArrive(point_list):
    while True:
        is_arrive = True
        globalLockValue.acquire()
        if current_actual is not None:
            for index in range(4):
                if abs(current_actual[index] - point_list[index]) > 1:
                    is_arrive = False
            if is_arrive:
                globalLockValue.release()
                return
        globalLockValue.release()
        sleep(0.001)


def ClearRobotError(dashboard: DobotApiDashboard):
    global robotErrorState
    dataController, dataServo = alarmAlarmJsonFile()
    while True:
        globalLockValue.acquire()
        if robotErrorState:
            numbers = re.findall(r'-?\d+', dashboard.GetErrorID())
            numbers = [int(num) for num in numbers]
            if numbers[0] == 0:
                if len(numbers) > 1:
                    for i in numbers[1:]:
                        alarmState = False
                        if i == -2:
                            print("Robot collision detected:", i)
                            alarmState = True
                        if alarmState:
                            continue
                        for item in dataController:
                            if i == item["id"]:
                                print("Controller error ID:", i, item["zh_CN"]["description"])
                                alarmState = True
                                break
                        if alarmState:
                            continue
                        for item in dataServo:
                            if i == item["id"]:
                                print("Servo error ID:", i, item["zh_CN"]["description"])
                                break
                    choose = input("Enter 1 to clear the error and continue: ")
                    if int(choose) == 1:
                        dashboard.ClearError()
                        sleep(0.01)
                        dashboard.Continue()
        else:
            if int(enableStatus_robot[0]) == 1 and int(algorithm_queue[0]) == 0:
                dashboard.Continue()
        globalLockValue.release()
        sleep(5)


if __name__ == '__main__':
    dashboard, move, feed = ConnectRobot()
    print("Enabling robot...")
    dashboard.EnableRobot()
    print("Robot enabled!")
    feed_thread = threading.Thread(target=GetFeed, args=(feed,))
    feed_thread.setDaemon(True)
    feed_thread.start()
    feed_thread1 = threading.Thread(target=ClearRobotError, args=(dashboard,))
    feed_thread1.setDaemon(True)
    feed_thread1.start()
    print("Executing loop...")
    point_a = [220, 0, 80, 78]
    point_b = [315, 0, -35, 78]
    while True:
        RunPoint(move, point_a)
        WaitArrive(point_a)
        RunPoint(move, point_b)
        WaitArrive(point_b)