# Occupancy Monitor
Small python script to check by camera if a room is occupied.

The script checks for movement in the pixels (video frame is processed) and runs a (simple) haar classifier to detect faces-

If some movement or faces are detected for a continuous amount of time (customizable & derived from number of frames) a notification is printed. Also includes notifications to be sent by email (with current video frame) and logging of all terminal output (both are customizable).
If configured images of triggerd event are saved to disk.

# Download

Simply clone this git.The files included in git are:
- occupancy_monitor.py (essential)
- haarcascade_frontalface_default.xml (essential)
- user_config.json (essential)
- requirements.txt (optional)

# Start

Configure the system settings to your liking in user_config.json.
You will need to provide your screens resolution (x,y) and email settings (from & to address, server, server port and password).
The sript will create the archive (for saving of event pictures) and log folder, if not existing.

# Q&A
t.b.d

# Futher improvments (Backlog)
- dynamic setting of seconds to arm when updating current system status (seconds of continuous movement or face present before notifying user)
- implementation of ML for face detection (recognize familiar faces, in sense of human trained)
