import cv2
import os
from pyzbar import pyzbar
import pandas as pd
from datetime import datetime
import pyttsx3
import requests
import subprocess
import time

class ISBNLookupError(Exception):
    """Raised when an ISBN lookup fails."""
    
    def __init__(self, isbn, message="Failed to look up ISBN"):
        self.isbn = isbn
        self.message = f"{message}: {isbn}"
        super().__init__(self.message)


def say(txt):
    subprocess.Popen(["say", f"{txt}"])

def play_sound(name):
    subprocess.Popen(["afplay", f"/System/Library/Sounds/{name}.aiff"])

def beep():
    play_sound("Glass")

def duplicated():
    play_sound("Funk")

def bad_book():
    play_sound("Basso")

def say_title(book):
    title = book['Title']
    print("Say title", title)
    say(title)



def get_book_info(isbn):
    url = f'https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data'
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        key = f'ISBN:{isbn}'
        if key in data:
            book = data[key]
            title = book.get('title', '')
            authors = ', '.join([a['name'] for a in book.get('authors', [])])
            publish_year = book.get('publish_date', '')
            return {
                'ISBN': isbn,
                'Title': title,
                'Authors': authors,
                'PublishYear': publish_year
            }
        else:
            raise ISBNLookupError(isbn, message = "Not found")
    except Exception as e:
        raise ISBNLookupError(isbn, message = "ISBN General Exception")


# CSV file to store ISBNs
CSV_FILE = 'books.csv'

# Load existing data or create new
try:
    df = pd.read_csv(CSV_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=['ISBN', 'Timestamp', 'Title', 'Authors', 'Published'])

say(f"There are {df.shape[0]} books currently stored.")
time.sleep(2)

# Initialize webcam
cap = cv2.VideoCapture(0)  # 0 is usually the default webcam
say("Please start scanning your books.")
beep()
duplicated()
bad_book()

print("'control-c' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect barcodes
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:

        isbn = barcode.data.decode('utf-8')
        print("BAR CODE Scanned", isbn)
        # Only add if not already in CSV

        if isbn not in df['ISBN'].values:
            try:
            
                book = get_book_info(isbn)
                title, authors, year = book['Title'], book['Authors'], book['PublishYear'] 

                print(isbn, title, authors, year)
                beep()
                say_title(book)

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                df = pd.concat([df, pd.DataFrame({'ISBN':[isbn], 'Timestamp':[timestamp],'Title':[title], 'Authors':[authors], 'Published':[year]})], ignore_index=True)
                df.to_csv(CSV_FILE, index=False)
                print(f"Scanned ISBN: {isbn} at {timestamp}")

            except ISBNLookupError as e:
                bad_book()
                print("ISBN Lookup failed:", e)

        else:
            duplicated()


        # Draw rectangle and text
        x, y, w, h = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, isbn, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Show webcam feed
    cv2.imshow('ISBN Scanner', frame)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


