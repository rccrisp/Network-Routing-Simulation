# My Markdown File

This is my first **Markdown** file. It contains some _italic_ and **bold** text.

## Setup

### Installing Modules

The main program uses only modules included in pythons stdlib. However, if you wish to make use of the GenerateConfigFiles.py for creating a new network topology, or for resetting the network topology after making changes using the CLI, you should install the required modules.

All of the required modules are included in the requirements.txt file. They can be installed in a virtual environment with 

`pip install -r requirements.txt`

### Network Topology

I have included my network topology in the local folder "config." My network program has a path to this directory from the home directory. If you want to change the network topology, you can either edit the text files, or run GenerateConfigFiles.py (note this program does make use of the python module networkx)

## Starting the Program

To start the program, you may either call each terminal/router separately as

`python COMP3221_A1_Routing.py <Node-ID> <Port-NO> <Node-Config-File>`

Or, you can call every terminal at once using the shell script in "run_network.sh". You will need to make this script executable by calling 

`chmod +x run_network.sh`

Inside the terminal. The script can then be run as 

`./run_network.sh`

Inside this calling terminal, you may close all of the program terminals (running the network simulation) by pressing enter


## Functionality

### Change Link Cost

To change a link cost, navigate to the terminal that is currently running this router instance (ie, to alter a link with Node A, use the terminal running Node A), and type the command update. Note any other command will prompt the user to enter the command "update" in order to update a node. 

The terminal will then ask the user for a Node ID, which should be a node that has a direct link with this current node. If a node that is not a direct neighbour is specified, the program will refuse this command, and print a list of nodes adjacent according to the network topology. These nodes are not guaranteed to be active.

Once the user has specified a valid link, the terminal will prompt the user for an updated link cost. This input must be a number greater than zero. 

If a valid link cost is provided, the program will confirm this new link has been accepted and is being updated

### Client Failures

The program is able to handle link failures in two ways

1. If the terminal running the program fails (exits or is killed by user), the program is able to detect a node failure. This simulates the case when a node fails completetly, and all of its links become inactive.  Each node in the network keeps track of the last time communication was received from each of its neighbours. If it does not receive communication from a node for two consecutive broadcast cycles (more than 20 seconds according the to the 10 second delay specified in the assignment), the node assumes this node has failed and updates its links accordingly.
2. Links can also fail through the Change Link Cost functionality. In this case, only the specified link is assumed to have been changed. To do so, simply update the existing link cost to be infinite ('inf').

## Resetting Network Topology

To return the network to its initial topology, simply run the GenerateConfigFiles.py file again.

## Conclusion

That's all for now. Thanks for reading!
