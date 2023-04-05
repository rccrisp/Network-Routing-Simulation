#!/bin/bash

# Define the commands to run in each terminal window
COMMAND_1="python3 COMP3221_A1_Routing.py A 6000 Aconfig.txt"
COMMAND_2="python3 COMP3221_A1_Routing.py B 6001 Bconfig.txt"
COMMAND_3="python3 COMP3221_A1_Routing.py C 6002 Cconfig.txt"
COMMAND_4="python3 COMP3221_A1_Routing.py D 6003 Dconfig.txt"
COMMAND_5="python3 COMP3221_A1_Routing.py E 6004 Econfig.txt"
COMMAND_6="python3 COMP3221_A1_Routing.py F 6005 Fconfig.txt"
COMMAND_7="python3 COMP3221_A1_Routing.py G 6006 Gconfig.txt"
COMMAND_8="python3 COMP3221_A1_Routing.py H 6007 Hconfig.txt"
COMMAND_9="python3 COMP3221_A1_Routing.py I 6008 Iconfig.txt"
COMMAND_10="python3 COMP3221_A1_Routing.py J 6009 Jconfig.txt"

# Launch the terminal windows with the specified commands
gnome-terminal --title="Node A" --command="bash -c '$COMMAND_1; $SHELL'" &
gnome-terminal --title="Node B" --command="bash -c '$COMMAND_2; $SHELL'" &
gnome-terminal --title="Node C" --command="bash -c '$COMMAND_3; $SHELL'" &
gnome-terminal --title="Node D" --command="bash -c '$COMMAND_4; $SHELL'" &
gnome-terminal --title="Node E" --command="bash -c '$COMMAND_5; $SHELL'" &
gnome-terminal --title="Node F" --command="bash -c '$COMMAND_6; $SHELL'" &
gnome-terminal --title="Node G" --command="bash -c '$COMMAND_7; $SHELL'" &
gnome-terminal --title="Node H" --command="bash -c '$COMMAND_8; $SHELL'" &
gnome-terminal --title="Node I" --command="bash -c '$COMMAND_9; $SHELL'" &
gnome-terminal --title="Node J" --command="bash -c '$COMMAND_10; $SHELL'" &

# Wait for the user to terminate the programs
read -p "Press [Enter] to terminate all nodes..."

# Send the SIGINT signal to all processes matching the name "gnome-terminal"
pkill -SIGINT gnome-terminal
