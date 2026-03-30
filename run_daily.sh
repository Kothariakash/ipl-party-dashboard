#!/bin/bash

echo "Enter the match ID for today's match:"
read match_id

echo "Enter the match name (e.g., RCB vs SRH):"
read match_name

# Update the test2.py file with the new match
# Assuming the matches list is in the file

# Use sed to add the new match to the list
sed -i '' "/matches = \[/a\\
        {\"id\": \"$match_id\", \"name\": \"$match_name\"},
" test2.py

# Run the script
/Users/akashkothari/Documents/ipl_party/venv/bin/python test2.py

echo "Process completed. Check the outputs."