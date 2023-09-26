while read -r url; do
  # Extract file name from URL
  filename=$(basename "$url")
  
  # Download the PDF file
  wget "$url" -O "$filename"
  
  # Convert PDF to text
  pdftotext "$filename"
  
  # Remove the downloaded PDF
  rm "$filename"
done < ../hrefs.txt

