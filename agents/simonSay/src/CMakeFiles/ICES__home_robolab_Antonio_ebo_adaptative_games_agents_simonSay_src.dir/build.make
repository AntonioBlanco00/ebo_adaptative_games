# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.22

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay

# Utility rule file for ICES__home_robolab_Antonio_ebo_adaptative_games_agents_simonSay_src.

# Include any custom commands dependencies for this target.
include src/CMakeFiles/ICES__home_robolab_Antonio_ebo_adaptative_games_agents_simonSay_src.dir/compiler_depend.make

# Include the progress variables for this target.
include src/CMakeFiles/ICES__home_robolab_Antonio_ebo_adaptative_games_agents_simonSay_src.dir/progress.make

ICES__home_robolab_Antonio_ebo_adaptative_games_agents_simonSay_src: src/CMakeFiles/ICES__home_robolab_Antonio_ebo_adaptative_games_agents_simonSay_src.dir/build.make
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold "BU robocompdsl /home/robocomp/robocomp/interfaces/IDSLs/CommonBehavior.idsl /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/CommonBehavior.ice"
	cd /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src && robocompdsl /home/robocomp/robocomp/interfaces/IDSLs/CommonBehavior.idsl /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/CommonBehavior.ice
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold "BU robocompdsl /home/robocomp/robocomp/interfaces/IDSLs/CameraSimple.idsl /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/CameraSimple.ice"
	cd /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src && robocompdsl /home/robocomp/robocomp/interfaces/IDSLs/CameraSimple.idsl /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/CameraSimple.ice
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold "BU robocompdsl /home/robocomp/robocomp/interfaces/IDSLs/EmotionalMotor.idsl /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/EmotionalMotor.ice"
	cd /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src && robocompdsl /home/robocomp/robocomp/interfaces/IDSLs/EmotionalMotor.idsl /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/EmotionalMotor.ice
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold "BU robocompdsl /home/robocomp/robocomp/interfaces/IDSLs/GestorSG.idsl /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/GestorSG.ice"
	cd /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src && robocompdsl /home/robocomp/robocomp/interfaces/IDSLs/GestorSG.idsl /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/GestorSG.ice
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold "BU robocompdsl /home/robocomp/robocomp/interfaces/IDSLs/JuegoSimonSay.idsl /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/JuegoSimonSay.ice"
	cd /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src && robocompdsl /home/robocomp/robocomp/interfaces/IDSLs/JuegoSimonSay.idsl /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/JuegoSimonSay.ice
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold "BU robocompdsl /home/robocomp/robocomp/interfaces/IDSLs/LEDArray.idsl /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/LEDArray.ice"
	cd /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src && robocompdsl /home/robocomp/robocomp/interfaces/IDSLs/LEDArray.idsl /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/LEDArray.ice
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold "BU robocompdsl /home/robocomp/robocomp/interfaces/IDSLs/Speech.idsl /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/Speech.ice"
	cd /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src && robocompdsl /home/robocomp/robocomp/interfaces/IDSLs/Speech.idsl /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/Speech.ice
.PHONY : ICES__home_robolab_Antonio_ebo_adaptative_games_agents_simonSay_src

# Rule to build all files generated by this target.
src/CMakeFiles/ICES__home_robolab_Antonio_ebo_adaptative_games_agents_simonSay_src.dir/build: ICES__home_robolab_Antonio_ebo_adaptative_games_agents_simonSay_src
.PHONY : src/CMakeFiles/ICES__home_robolab_Antonio_ebo_adaptative_games_agents_simonSay_src.dir/build

src/CMakeFiles/ICES__home_robolab_Antonio_ebo_adaptative_games_agents_simonSay_src.dir/clean:
	cd /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src && $(CMAKE_COMMAND) -P CMakeFiles/ICES__home_robolab_Antonio_ebo_adaptative_games_agents_simonSay_src.dir/cmake_clean.cmake
.PHONY : src/CMakeFiles/ICES__home_robolab_Antonio_ebo_adaptative_games_agents_simonSay_src.dir/clean

src/CMakeFiles/ICES__home_robolab_Antonio_ebo_adaptative_games_agents_simonSay_src.dir/depend:
	cd /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/CMakeFiles/ICES__home_robolab_Antonio_ebo_adaptative_games_agents_simonSay_src.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : src/CMakeFiles/ICES__home_robolab_Antonio_ebo_adaptative_games_agents_simonSay_src.dir/depend

