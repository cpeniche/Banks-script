#!/bin/bash

#Removes any line that starts with letters
sed '/^[[:upper:]]/d' "$1" > "$2"  

sed -i 's/\$\s/,\$/' "$2" 

#adds '-$' to those lines with no '-' at the end 
sed -i '/-$/!s/\$/-\$/' "$2" 

#changes first space to ','
sed -i 's/\s/,/' "$2"

#Adds the year to the date
sed -i "s/^[[:digit:]]\+\/[[:digit:]]\+/&\/"$3"/" "$2"

#Remove '-' at the end
sed -i 's/-$//' "$2"
