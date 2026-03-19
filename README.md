# ISBN Scanner

Scan ISBN books with web camera and store in a CSV file

## Once only
```
mkdir isbn_scanner
cd isbn_scanner
python -m venv .
```

## Then in another terminal shell
```
cd ~/isbn_scanner
source ~/bin/activate
python -m pip install requests pandas pyzbar opencv-python pyttsx3
```


## To run book scanner - make sure you have the right Python env
```
source $PWD/bin/activate
```
## Finally run python script.
```
python scan.py
```

Hold up ISBN books to camera. Books stored in books.csv
