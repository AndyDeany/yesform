source venv/Scripts/activate
mv "$(cat csv_location.txt)" ./ferret.csv
python proform.py
deactivate
