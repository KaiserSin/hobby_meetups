# Hobby Meetups

Hobby Meetups is a simple web application for finding and organizing local activities. Whether you want to play board games, study together, or start a small hobby group, you can create a meetup, browse events by category, join other people's plans, and check user profiles.

## Features

* **User Authentication:** Users can create an account, log in securely, and log out when they are done.
* **Manage Meetups:** Logged in users can create meetup announcements, edit them, and delete their own events.
* **View and Search:** Anyone can browse the list of meetups and search for events using keywords.
* **Categories:** Each meetup can belong to one or more categories, which makes the list clearer and easier to browse.
* **Join Meetups:** Logged in users can join a meetup and leave a short comment for the organizer.
* **User Profiles:** Every user has a public profile page with basic stats and a list of the meetups they have created.

## How to Test Locally

To make the setup process as easy as possible, this project includes automated setup scripts.

**For Mac and Linux users:**
1. Clone the repository.
2. Open your terminal and navigate to the project folder.
3. Run the setup script: `bash setup.sh`
4. The script will automatically create a virtual environment, install Flask, initialize the database, and start the server.

**For Windows users:**
1. Clone the repository.
2. Open Command Prompt and navigate to the project folder.
3. Run the setup script: `setup.bat`
4. The script will automatically create a virtual environment, install Flask, initialize the database, and start the server.
