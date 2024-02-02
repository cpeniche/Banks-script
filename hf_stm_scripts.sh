#!/bin/bash

#Removes any line that starts with letters
sed '/^[[:upper:]]/d' "$1" > "$2"  

#Removes spaces and insert ','
sed -i 's/-*\$\s*/,&/' "$2"   

#changes first space to ','
sed -i 's/\s/,/' "$2"

#if a date is found add the year otherwise remove the line
sed -i "s/^[[:digit:]]\+\/[[:digit:]]\+/&\/"$3"/ ; t ; d" "$2"

#reverse sign on digits
sed -i 's/-\$/\$/ ; t ; s/\$/-\$/' "$2"
