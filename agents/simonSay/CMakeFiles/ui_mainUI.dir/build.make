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

# Utility rule file for ui_mainUI.

# Include any custom commands dependencies for this target.
include CMakeFiles/ui_mainUI.dir/compiler_depend.make

# Include the progress variables for this target.
include CMakeFiles/ui_mainUI.dir/progress.make

CMakeFiles/ui_mainUI: src/ui_mainUI.py

src/ui_mainUI.py: src/mainUI.ui
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold --progress-dir=/home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Generating src/ui_mainUI.py from src/mainUI.ui"
	pyside2-uic /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/mainUI.ui -o /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/src/ui_mainUI.py

ui_mainUI: CMakeFiles/ui_mainUI
ui_mainUI: src/ui_mainUI.py
ui_mainUI: CMakeFiles/ui_mainUI.dir/build.make
.PHONY : ui_mainUI

# Rule to build all files generated by this target.
CMakeFiles/ui_mainUI.dir/build: ui_mainUI
.PHONY : CMakeFiles/ui_mainUI.dir/build

CMakeFiles/ui_mainUI.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/ui_mainUI.dir/cmake_clean.cmake
.PHONY : CMakeFiles/ui_mainUI.dir/clean

CMakeFiles/ui_mainUI.dir/depend:
	cd /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay /home/robolab/Antonio/ebo_adaptative_games/agents/simonSay/CMakeFiles/ui_mainUI.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/ui_mainUI.dir/depend

