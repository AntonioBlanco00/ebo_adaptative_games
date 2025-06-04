cmake_minimum_required(VERSION 2.6)
PROJECT(  pasapalabra )

INCLUDE( /home/robocomp/robocomp/cmake/robocomp.cmake )

ROBOCOMP_IDSL_TO_ICE( CommonBehavior CameraSimple EmotionalMotor GestorSG LEDArray Pasapalabra Speech )
