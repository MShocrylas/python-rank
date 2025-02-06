A tool designed to rank a set of items through head-to-head comparisons, powered by the Elo rating system.

Struggling to rank your favorites? This tool simplifies the process by breaking it down into straightforward pairwise choices.

# Features
- **Pairwise Comparisons**: Rank items effortlessly by selecting your preference between two options at a time.  
- **Elo Rating System**: Utilizes the proven Elo system for initial rankings, with plans to support additional comparison methods in the future.  
- **Save and Resume**: Save your progress and return to refine your rankings later using the load command.  

# Usage

1. **Prepare an Input File** (for the 'new' command):  
   Create a `.txt` file with one item per line.  

2. **Run the Script**:  
   - **New Ranking**:  
     ```bash  
     python rank.py new <filename>.txt  
     ```  
   - **Continue Ranking**:  
     ```bash  
     python rank.py load rankinfo_<filename>.json  
     ```  
