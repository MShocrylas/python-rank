A tool to rank a set of items based purely on head-to-head comparisons, using the Elo rating system.

Having trouble deciding on your absolute favorite? This tool helps you break down the sometimes painful task of ranking items into simple preference choices.

# Features

 - Easy Comparisons: No more agonizing over a numbered ranking! Just choose your preference between two items.
 - Elo Rating System: Initial ranking uses the established Elo system, with more comparison methods planned for the future.
 - Save and Resume: Continue refining your rankings over multiple sessions with the `load` command.
 
# Usage

1. Prepare an Input File (for 'new' command):
        Create a .txt file.
        Place one item name on each line.

2. Run the Script:

    ### New Ranking:

        python rank.py new <filename>.txt 

    ### Continue Ranking:


        python rank.py load rankinfo_<filename>.json 

