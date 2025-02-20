cmake_minimum_required(VERSION 2.6)
PROJECT(  ebo_gpt )

INCLUDE( /home/robocomp/robocomp/cmake/robocomp.cmake )

ROBOCOMP_IDSL_TO_ICE( CommonBehavior EboMoods EmotionalMotor GPT LEDArray Speech )
