import os
from io import BytesIO, StringIO  # Import BytesIO
import csv  # Ensure csv is imported if you're working with CSV data
from cs50 import SQL
from werkzeug.utils import secure_filename
from flask import Flask, flash, redirect, render_template, request, session, send_file,  url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from helpers import apology, login_required, lookup, usd



# Configure application
app = Flask(__name__)
# Custom filter
app.jinja_env.filters["usd"] = usd
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///pss.db")
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Show homepage with events"""
    events = db.execute("SELECT id, name, description, start_date, end_date, image FROM events")
    is_admin = [row['user_id'] for row in db.execute("SELECT user_id FROM admins")]
    user_id = session.get("user_id")
    return render_template("index.html", events=events, is_admin=is_admin, user_id=user_id)




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username and password were submitted
        username = request.form.get("username")
        password = request.form.get("password")
        if not username:
            return apology("must provide username", 400)
        if not password:
            return apology("must provide password", 400)
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 400)
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = username  # Store the username in the session
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (e.g., by clicking a link or via redirect)
    return render_template("login.html")











def admin_required(f):
    """
    Decorator to require admin privileges for certain routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Ensure the user is logged in
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        # Check if the logged-in user is an admin
        user_id = session.get("user_id")
        user = db.execute("SELECT * FROM admins WHERE user_id = ?", (user_id,))
        if not user:
            flash("You need to be an admin to access this page.")
            return redirect(url_for("index"))  # Redirect to a safe page if not an admin
        return f(*args, **kwargs)
    return decorated_function








@app.route("/admins")
@login_required
def admins():
    """Show list of current admins and allow adding new admins"""
    # Fetch all admins
    admins = db.execute("""
        SELECT users.id, users.username
        FROM admins
        JOIN users ON admins.user_id = users.id
    """)

    # Fetch all users
    users = db.execute("""
        SELECT id, username FROM users
    """)

    return render_template("admins.html", admins=admins, users=users)


@app.route("/add_admin", methods=["POST"])
@admin_required
@login_required
def add_admin():
    """Add a new admin"""
    user_id = request.form.get("user_id")
    if user_id:
        user_id = int(user_id)  # Ensure user_id is an integer

        # Check if the user is already an admin
        existing_admin = db.execute("SELECT * FROM admins WHERE user_id = ?", (user_id,))
        if existing_admin:
            flash("User is already an admin.")
        else:
            # Add the user as an admin
            db.execute("INSERT INTO admins (user_id) VALUES (?)", (user_id))
            flash("Admin added successfully.")
    else:
        flash("No user selected.")

    return redirect(url_for("admins"))










@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Show and update user profile"""
    user_id = session.get("user_id")

    if request.method == "POST":
        # Retrieve form data
        username = request.form.get("username")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        department = request.form.get("department")
        semester = request.form.get("semester")
        university_registration_number = request.form.get("university_registration_number")
        gender = request.form.get("gender")

        # Ensure all required fields are provided
        if not username or not email or not phone_number or not department or not semester or not university_registration_number or not gender:
            return apology("must provide all required fields", 400)

        # Update user details in the database
        db.execute("""
            UPDATE users
            SET username = ?, email = ?, phone_number = ?, department = ?, semester = ?, university_registration_number = ?, gender = ?
            WHERE id = ?
        """, username, email, phone_number, department, semester, university_registration_number, gender, user_id)

        # Update session data
        session["username"] = username

        flash("Profile updated!")
        return redirect("/profile")

    # Fetch user details
    user = db.execute("SELECT username, email, phone_number, department, semester, university_registration_number, gender FROM users WHERE id = ?", user_id)
    if len(user) != 1:
        return apology("User not found", 404)
    user = user[0]

    # Fetch registered events
    events = db.execute("""
        SELECT e.id, e.name, e.start_date, e.end_date, s.name AS sport_name
        FROM registrations r
        JOIN events e ON r.event_id = e.id
        JOIN sports s ON r.sport_id = s.id
        WHERE r.user_id = ?
        ORDER BY e.start_date
    """, user_id)

    return render_template("profile.html", user=user, events=events)











@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to home page
    return redirect("/")




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""
    if request.method == "POST":
        # Retrieve form data
        username = request.form.get("username")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmation")
        department = request.form.get("department")
        semester = request.form.get("semester")
        university_registration_number = request.form.get("university_registration_number")
        gender = request.form.get("gender")

        # Check if all required fields are provided
        if not username or not email or not phone_number or not password or not confirm_password or not department or not semester or not university_registration_number or not gender:
            flash("All fields are required.", "danger")
            return redirect("/register")

        # Ensure password and confirmation match
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect("/register")

        # Validate password length
        if len(password) <= 7:
            flash("Password must be at least 8 characters long.", "danger")
            return redirect("/register")

        # Check if username or email already exists
        rows = db.execute("SELECT * FROM users WHERE username = ? OR email = ?", username, email)
        if len(rows) > 0:
            flash("Username or email already taken.", "danger")
            return redirect("/register")

        # Hash the password
        hashh = generate_password_hash(password)

        # Insert the new user into the database
        result = db.execute("INSERT INTO users (username, email, phone_number, hash, department, semester, university_registration_number, gender) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            username, email, phone_number, hashh, department, semester, university_registration_number, gender)

        # Retrieve the new user's ID
        user_id = result

        # Set the session user ID
        session["user_id"] = user_id
        session["username"] = username  # Store the username in the session

        # Flash a success message
        flash("Registered successfully!", "success")
        return redirect("/")

    # GET request renders the registration form
    return render_template("register.html")








@app.route("/create_event", methods=["GET", "POST"])
@login_required
@admin_required
def create_event():
    """Create a new event"""
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        description = request.form.get("description")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        image = request.files.get("image")

        # Validate form data
        if not name or not description or not start_date or not end_date:
            return apology("must provide all required fields", 400)

        # Handle image upload
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join('static/uploads', filename))
        else:
            filename = None
        # Insert event into the database
        db.execute("INSERT INTO events (name, description, start_date, end_date, image) VALUES (?, ?, ?, ?, ?)",
                   name, description, start_date, end_date, filename)
        flash("Event created!")
        return redirect("/")
    # GET request renders the event creation form
    return render_template("create_event.html")




@app.route("/delete_event", methods=["GET", "POST"])
@admin_required
@login_required
def delete_event():
    """Delete an event"""
    if request.method == "POST":
        # Get the event ID from the form
        event_id = request.form.get("event_id")
        # Validate event ID
        if not event_id:
            return apology("must provide an event ID", 400)
        # Delete related registrations
        db.execute("DELETE FROM registrations WHERE event_id = ?", event_id)
        # Delete the event
        db.execute("DELETE FROM events WHERE id = ?", event_id)
        flash("Event deleted!")
        return redirect("/")
    # GET request renders the event deletion form
    events = db.execute("SELECT id, name FROM events")
    return render_template("delete_event.html", events=events)







@app.route("/event/<int:event_id>")
def event_details(event_id):
    """Show details for a specific event and allow CSV download"""
    # Fetch event details
    event = db.execute("SELECT * FROM events WHERE id = ?", event_id)
    if len(event) != 1:
        return apology("Event not found", 404)
    event = event[0]
    # Fetch registrations for the event
    registrations = db.execute("SELECT u.username, u.email, u.phone_number FROM registrations r JOIN users u ON r.user_id = u.id WHERE r.event_id = ?", event_id)
    return render_template("event_details.html", event=event, registrations=registrations)





@app.route('/show_csv_settings/<int:event_id>', methods=['GET', 'POST'])
@login_required
def show_csv_settings(event_id):
    if request.method == 'POST':
        sport_id = request.form.get('sport_id')
        department = request.form.get('department')
        gender = request.form.get('gender')

        # Redirect to download CSV route with parameters
        return redirect(url_for('download_filtered_csv',
                                sport_id=sport_id,
                                department=department,
                                gender=gender,
                                event_id=event_id))

    # Fetch sports data for the filter form
    sports = db.execute("SELECT * FROM sports")

    # Hardcoded departments
    departments = [
        'DCIS',
        'DPhy',
        'DEE',
        'DME',
        'DCHE',
        'DMME',
        'DChy',
        'DNE'
    ]

    return render_template('show_csv_settings.html',
                           event_id=event_id,
                           sports=sports,
                           departments=departments)




@app.route('/download_filtered_csv', methods=['POST'])
@admin_required
@login_required
def download_filtered_csv():
    # Get filter parameters from form data
    sport_id = request.form.get('sport_id')
    department = request.form.get('department')
    gender = request.form.get('gender')

    # Construct SQL query based on the filters
    query = """
    SELECT
        users.id AS user_id,
        users.username,
        users.email,
        users.phone_number,
        users.department,
        users.gender,
        sports.name AS sport_name,
        events.name AS event_name
    FROM users
    JOIN registrations ON users.id = registrations.user_id
    JOIN sports ON registrations.sport_id = sports.id
    JOIN events ON registrations.event_id = events.id
    WHERE 1=1
    """
    params = []
    if sport_id:
        query += " AND registrations.sport_id = ?"
        params.append(sport_id)
    if department:
        query += " AND users.department = ?"
        params.append(department)
    if gender:
        query += " AND users.gender = ?"
        params.append(gender)

    # Execute the query
    users = db.execute(query, *params)

    # Create CSV using StringIO
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'User ID', 'Username', 'Email', 'Phone Number',
        'Department', 'Gender', 'Sport Name', 'Event Name'
    ])
    for user in users:
        writer.writerow([
            user['user_id'],
            user['username'],
            user['email'],
            user['phone_number'],
            user['department'],
            user['gender'],
            user['sport_name'],
            user['event_name']
        ])

    output.seek(0)

    # Convert StringIO to BytesIO
    byte_output = BytesIO(output.getvalue().encode('utf-8'))
    output.close()

    # Construct the filename based on filters
    filename_parts = []
    if sport_id:
        sport_name = db.execute("SELECT name FROM sports WHERE id = ?", sport_id)
        if sport_name:
            filename_parts.append(f"Sport_{sport_name[0]['name']}")
    if department:
        filename_parts.append(f"Department_{department}")
    if gender:
        filename_parts.append(f"Gender_{gender}")
    if not filename_parts:
        filename_parts.append("All_Users")

    filename = '_'.join(filename_parts) + '.csv'

    return send_file(byte_output, mimetype='text/csv', as_attachment=True, download_name=filename)









@app.route('/register_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def register_event(event_id):
    if request.method == 'POST':
        user_id = session['user_id']
        sports_ids = request.form.getlist('sports')  # List of selected sports IDs

        # Register user for the event and selected sports
        for sport_id in sports_ids:
            db.execute("INSERT INTO registrations (user_id, event_id, sport_id) VALUES (?, ?, ?)", user_id, event_id, sport_id)

        # Fetch event details for flash message
        event = db.execute("SELECT * FROM events WHERE id = ?", event_id)
        if len(event) != 1:
            return apology("Event not found", 404)
        event = event[0]

        # Fetch sports names for the selected sports IDs
        placeholders = ', '.join(['?'] * len(sports_ids))  # Create placeholders for SQL IN clause
        sports = db.execute(f"SELECT name FROM sports WHERE id IN ({placeholders})", *sports_ids)

        # Fetch user's name
        user = db.execute("SELECT username FROM users WHERE id = ?", user_id)
        if len(user) != 1:
            return apology("User not found", 404)
        user = user[0]

        # Create flash message
        sport_names = ", ".join(sport['name'] for sport in sports)
        flash(f'{user["username"]} has registered for {event["name"]} with sports: {sport_names}')
        return redirect('/')

    # GET request: Show form to register for events
    event = db.execute("SELECT * FROM events WHERE id = ?", event_id)
    sports = db.execute("SELECT * FROM sports")
    if len(event) != 1:
        return apology("Event not found", 404)
    event = event[0]
    return render_template('register_event.html', event=event, sports=sports)










@app.route("/apply_representative", methods=["GET", "POST"])
@login_required
def apply_representative():
    if request.method == "POST":
        user_id = session["user_id"]
        experience = request.form.get("experience")
        suggestions = request.form.get("suggestions")

        if not user_id:
            flash("You must be logged in to apply.", "danger")
            return redirect(url_for("login"))

        if not experience or not suggestions:
            flash("Please fill out all fields.", "warning")
            return redirect(url_for("apply_representative"))

        try:
            # Debugging output
            print(f"DEBUG: user_id={user_id}, experience={experience}, suggestions={suggestions}")

            db.execute("""
                INSERT INTO departmental_rep_applicants (user_id, experience, suggestions)
                VALUES (?, ?, ?)
            """, (user_id), (experience), (suggestions))

            flash("Application submitted successfully.", "success")
        except Exception as e:
            # Print out the error for debugging
            print(f"DEBUG: Error occurred: {e}")
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for("index"))
    return render_template("apply_representative.html")












@app.route("/select_representative", methods=["GET", "POST"])
@login_required
@admin_required
def select_representative():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        if user_id:
            user_id = int(user_id)  # Ensure user_id is an integer

        # Debugging: Print the user_id to ensure it's correctly retrieved
        print(f"User ID from form: {user_id}")

        # Check if the user_id exists in the users table (debugging step)
        user_exists = db.execute("SELECT id FROM users WHERE id = ?", (user_id))
        if not user_exists:
            return redirect(url_for('select_representative'))

        # Check if the user is already a selected representative
        existing_rep = db.execute("SELECT * FROM selected_departmental_reps WHERE user_id = ?", (user_id))
        print(f"Existing Rep Query Result: {existing_rep}")  # Debugging ste


        if existing_rep:
            flash("User is already a selected representative.")
        else:
            try:
                db.execute("""
                    INSERT INTO selected_departmental_reps (user_id)
                    VALUES (?)
                """, (user_id))
                flash("Representative selected successfully.")
            except Exception as e:
                # Debugging: Log the exception and flash an error message
                print(f"Error inserting representative: {e}")
                flash("An error occurred while selecting the representative.")

    # Debugging: Print applicants query to verify correct selection
    applicants = db.execute("""
        SELECT a.user_id, u.username, u.department, a.experience, a.suggestions
        FROM departmental_rep_applicants a
        JOIN users u ON a.user_id = u.id
    """)
    print(f"Applicants Query Result: {applicants}")  # Debugging step

    return render_template("select_representative.html", applicants=applicants)


@app.route("/enrollment_call")
def enrollment_call():
    return render_template("enrollment_call.html")
