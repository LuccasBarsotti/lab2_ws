#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import math
import csv
import time

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.header = [
            "Tempo", "ITTC", "LASER_BEAM_INDEX", "LASER_BEAM_ANGLE_DEGREE",
            "LASER_BEAM_LENGTH", "VELOCITY_TOTAL", "VELOCITY_AT_LASER_BEAM_DIRECTION"
        ]
        self.filename= 'data.csv'
        with open(self.filename, 'a') as file:
            writer= csv.writer(file)
            writer.writerow(self.header)
        self.time_count= 0
        self.latest_odom= None
        self.latest_scan= None
        self.ittc= []
        self.subscription = self.create_subscription(
            LaserScan,
            'scan',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.subscription2= self.create_subscription(
            Odometry,
            '/ego_racecar/odom',
            self.listener_callback2,
            10
        )
        self.subscription2

    def listener_callback(self, msg):
        self.latest_scan= msg
        self.ittc_calculation()
        #self.get_logger().info(f'I heard: range= {msg.ranges[1079]:.5f}')

    def listener_callback2(self, msg):
        self.latest_odom= msg
        self.ittc_calculation()
    
    def ittc_calculation(self):
        if self.latest_odom is not None and self.latest_scan is not None:
            v_x= self.latest_odom.twist.twist.linear.x
            laser_scan= self.latest_scan
            self.ittc= [None] * len(laser_scan.ranges)
            with open(self.filename, 'a') as file:
                writer= csv.writer(file)
                for i in range(len(laser_scan.ranges)):
                    if abs(v_x) < 0.2:
                        self.ittc[i]= 100000000.0
                    else:
                        self.ittc[i]= laser_scan.ranges[i]/(v_x*math.cos(laser_scan.angle_min + i*laser_scan.angle_increment))
                    newrow= [
                        self.time_count, self.ittc[i], i, math.degrees(laser_scan.angle_min + i*laser_scan.angle_increment), laser_scan.ranges[i], v_x, v_x*math.cos(laser_scan.angle_min + i*laser_scan.angle_increment)
                    ]
                    writer.writerow(newrow)
                self.time_count+= 2
            time.sleep(2)
            #self.get_logger().info(f'{self.ittc[i]:.5f}')
            self.get_logger().info(f'DADOS GRAVADOS COM SUCESSO!\n\n')


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()