cmake_minimum_required(VERSION 2.6)
PROJECT(  simonSay )

INCLUDE( /home/robocomp/robocomp/cmake/robocomp.cmake )

ROBOCOMP_IDSL_TO_ICE( CommonBehavior CameraSimple EmotionalMotor GestorSG JuegoSimonSay LEDArray Speech )
