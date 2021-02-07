# TG Nextera XT - Opentrons Automation

## Description
This repository contains the code for operation of the Opentrons OT2 robot to automate the TG Nextera library preparation

There are four steps in the workflow performed in the robot:

1. First PCR for amplicon generation
2. Clean up
3. Second PCR for indexing
4. Clean up

Note that the two clean up protocols are the same.  


There is a jupyter notebook available for simulating the protocols to more easily track the actions the robot will take for each protocol. 