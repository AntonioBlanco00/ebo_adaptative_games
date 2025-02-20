cmake_minimum_required(VERSION 2.6)
PROJECT(  app_juegos )

INCLUDE( /home/robocomp/robocomp/cmake/robocomp.cmake )

ROBOCOMP_IDSL_TO_ICE( CommonBehavior GestorSG JuegoSimonSay Pasapalabra StoryTelling )
