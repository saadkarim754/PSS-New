# PIEAS SPORTICS SOCIETY
#### Video Demo:  <https://www.loom.com/share/12c84fabe30a4c00ae03aa1a479aab1d?sid=d7afce28-9d8f-44e2-b244-f00f20fe93d8>
#### Description:

The PIEAS SPORTICS SOCIETY project is a web application designed to manage sports events and player profiles for the sports society at PIEAS. The application enables users to register, login, and enroll in various sports events. It also provides a comprehensive dashboard for admins to create and manage events, track registrations, and download participant data in CSV format.

## Project Files

### `app.py`
This is the main application file where the Flask app is initialized and all routes are defined. It includes functionalities for user registration, login, profile management, event creation, and CSV download.

### `helpers.py`
This file contains helper functions used across the application, such as apology for rendering error messages.

### `templates/`
This directory contains all HTML templates for the application, including:
- `index.html`: The home page of the application.
- `register.html`: The registration page for new users.
- `login.html`: The login page for existing users.
- `profile.html`: The profile page where users can view and update their information.
- `create_event.html`: The page for admins to create new events.
- `event_details.html`: The page displaying details of a specific event, including a button to download participant data.
- `show_csv_settings.html`: The page where admins can filter data before downloading CSV files.

### `static/`
This directory contains static files like CSS and JavaScript used in the application.

## Design Choices

1. **Flask Framework**: Chosen for its simplicity and flexibility, making it suitable for a project of this scale.
2. **SQLite Database**: Used for its ease of setup and integration with Flask. It is sufficient for the application's needs.
3. **Session Management**: Implemented using Flask-Session to manage user sessions and maintain login states.
4. **Password Security**: Passwords are hashed using Werkzeug's security module to ensure user data is protected.

## Features

- **User Registration and Login**: Users can create accounts and log in to the application.
- **Profile Management**: Users can view and update their profile information.
- **Event Registration**: Users can enroll in multiple sports events.
- **Admin Dashboard**: Admins can create new events, manage existing events, and download participant data.
- **CSV Download**: Admins can download filtered participant data in CSV format based on selected criteria.

## Challenges

One of the challenges faced during development was ensuring the integrity and validation of user input, particularly for phone numbers and passwords. The application enforces a strict format for phone numbers and a minimum length requirement for passwords to enhance security and user experience.

## Future Enhancements

- **Email Notifications**: Implementing email notifications for event registrations and updates.
- **User Roles**: Expanding the admin dashboard to include more granular user role management.
- **Enhanced Analytics**: Adding more detailed analytics and reporting features for admins.
- **ability to remove admins by having a super admin**

This project has been a great learning experience, and I am proud of the features and functionality implemented. I look forward to further enhancing the application based on feedback and user needs.

## changes to git
- :the ssh keys are already set up
- :use these three steps
- :git init
- :git add .
- :git commit -m "your commit message"
- :git push -u origin main