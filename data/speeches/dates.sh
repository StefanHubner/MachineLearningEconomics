# Create a CSV file and write the header
echo "Filename;Date" > ../speeches.csv

# Loop through each file in the directory
for file in *; do
  if [ -f "$file" ]; then
    # Extract date from the first 10 lines
    date=$(head -n 10 "$file" | grep -Eo '[0-9]{1,2} [A-Za-z]+ [0-9]{4}')
    if [ ! -z "$date" ]; then
      # Write filename and date to the CSV file
      echo "$file;$date" >> ../speeches.csv
    fi
  fi
done

