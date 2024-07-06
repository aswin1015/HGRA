import sqlite3

# Connect to the SQLite database (create it if it doesn't exist)
conn = sqlite3.connect('gestures.db')
c = conn.cursor()
try:
    c.execute('drop table gestures')
except:
    pass
# Create a table to store gestures and their corresponding actions
c.execute('''CREATE TABLE IF NOT EXISTS gestures
             (gesture_id int,gesture text,description text, action text)''')
# Insert some sample data into the table

#create smaple data as list of tuples with 1st element being id 2nd element being the gesture from gest and 3rd and 4th as blank strings
sample_data = [
    (1,'open_palm', 'select text and copy it','select_and_copy'),
    (2,'fist', 'pauses the video currently playing','pause_video'),
    (3,'thumbs_up','closes the current window','close_window'),
    (4,'Circle','mute the system speaker','mute'),
    (5,'Rock','opens notepad','open_notepad'),
    (6,'W','paste the selected text','paste'),
    (7,'Stop','change window','change_window'),
    (8,'cheese','captures the current screen','screenshot'),
    (9,'tri','reads 5 news headline from BBC','news'),
    (10,'forward','fast forward in video player','fast_forward'),
    (11,'double_peace','plays songs in a folder','play_songs'),
    ]

c.executemany('INSERT INTO gestures VALUES (?, ?, ?,?)', sample_data)

# Commit changes and close connection
conn.commit()
conn.close()
