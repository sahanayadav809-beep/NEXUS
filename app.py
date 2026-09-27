from functools import wraps
import os

from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection, create_tables

from agent.analyzer import analyze_chaos
from agent.conflict_detector import detect_conflicts
from agent.priority_engine import calculate_priorities
from agent.planner import create_action_plan, generate_recommendation
from agent.schedule_engine import create_study_schedule
from agent.daily_planner import create_daily_plan


app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "nexus-dev-secret-change-me"
)

create_tables()


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if "user_id" not in session:
            return redirect(
                url_for("login", next=request.path)
            )

        return view(*args, **kwargs)

    return wrapped


def current_user_id():
    return session["user_id"]


# =========================================================
# ACTIVE USER INFORMATION
# =========================================================

def get_active_information():

    user_id = current_user_id()

    connection = get_db_connection()

    assignments = connection.execute(
        """
        SELECT *
        FROM assignments
        WHERE user_id = ?
        AND status != 'Completed'
        ORDER BY deadline
        """,
        (user_id,)
    ).fetchall()

    presentations = connection.execute(
        """
        SELECT *
        FROM presentations
        WHERE user_id = ?
        AND status != 'Completed'
        ORDER BY presentation_date
        """,
        (user_id,)
    ).fetchall()

    classes = connection.execute(
        """
        SELECT *
        FROM timetable
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return {

        "assignments": [
            {
                "title": a["title"],
                "deadline": a["deadline"],
                "hours": a["estimated_hours"],
                "importance": a["importance"],
                "status": a["status"]
            }
            for a in assignments
        ],

        "presentations": [
            {
                "topic": p["topic"],
                "date": p["presentation_date"],
                "hours": p["preparation_hours"],
                "importance": p["importance"],
                "status": p["status"]
            }
            for p in presentations
        ],

        "classes": [
            {
                "subject": c["subject"],
                "day": c["day"],
                "start": c["start_time"],
                "end": c["end_time"],
                "room": c["room"]
            }
            for c in classes
        ]

    }


# =========================================================
# USER AVAILABLE IN TEMPLATES
# =========================================================

@app.context_processor
def inject_user():

    return {
        "logged_in_user": session.get("user_name")
    }


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        connection = get_db_connection()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        if not user:

            flash("Invalid email or password.")

            return render_template(
                "login.html"
            )

        if not check_password_hash(
            user["password_hash"],
            password
        ):

            flash("Invalid email or password.")

            return render_template(
                "login.html"
            )

        # Clear old session
        session.clear()

        # Store logged-in user
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        return redirect(
            url_for("home")
        )

    return render_template(
        "login.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm = request.form.get(
            "confirm_password",
            ""
        )

        # Check required fields
        if not name or not email or len(password) < 6:

            flash(
                "Enter your name, a valid email, and a password of at least 6 characters."
            )

            return render_template(
                "register.html"
            )

        # Check passwords
        if password != confirm:

            flash(
                "Passwords do not match."
            )

            return render_template(
                "register.html"
            )

        connection = get_db_connection()

        try:

            # Check existing account
            existing = connection.execute(
                """
                SELECT id
                FROM users
                WHERE email = ?
                """,
                (email,)
            ).fetchone()

            if existing:

                flash(
                    "An account with that email already exists."
                )

                return render_template(
                    "register.html"
                )

            # Create user
            connection.execute(
                """
                INSERT INTO users
                (name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (
                    name,
                    email,
                    generate_password_hash(password)
                )
            )

            connection.commit()

            # Get newly created user
            user = connection.execute(
                """
                SELECT *
                FROM users
                WHERE email = ?
                """,
                (email,)
            ).fetchone()

            # Handle old SQLite records
            if not connection.postgres:

                for table in (
                    "assignments",
                    "presentations",
                    "timetable"
                ):

                    connection.execute(
                        f"""
                        UPDATE {table}
                        SET user_id = ?
                        WHERE user_id IS NULL
                        """,
                        (user["id"],)
                    )

                connection.commit()

        finally:

            connection.close()

        # Automatically login after registration
        session.clear()

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        return redirect(
            url_for("home")
        )

    return render_template(
        "register.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not email or not new_password or not confirm_password:
            flash("Please fill all fields.", "error")
            return redirect(url_for("forgot_password"))

        if new_password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("forgot_password"))

        if len(new_password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("forgot_password"))

        connection = get_db_connection()

        user = connection.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if not user:
            connection.close()
            flash("No account found with that email.", "error")
            return redirect(url_for("forgot_password"))

        password_hash = generate_password_hash(new_password)

        connection.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, user["id"])
        )

        connection.commit()
        connection.close()

        flash("Password reset successfully. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("forgot_password.html")

# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
@login_required
def home():

    user_id = current_user_id()

    connection = get_db_connection()

    assignments = connection.execute(
        """
        SELECT *
        FROM assignments
        WHERE user_id = ?
        ORDER BY deadline
        """,
        (user_id,)
    ).fetchall()

    presentations = connection.execute(
        """
        SELECT *
        FROM presentations
        WHERE user_id = ?
        ORDER BY presentation_date
        """,
        (user_id,)
    ).fetchall()

    classes = connection.execute(
        """
        SELECT *
        FROM timetable
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    information = get_active_information()

    conflicts = detect_conflicts(
        information
    )

    priorities = calculate_priorities(
        information
    )

    top_task = (
        priorities[0]
        if priorities
        else None
    )

    recommendation = generate_recommendation(
        priorities,
        conflicts
    )

    total_assignments = len(
        assignments
    )

    completed_assignments = sum(
        1
        for item in assignments
        if item["status"] == "Completed"
    )

    total_presentations = len(
        presentations
    )

    completed_presentations = sum(
        1
        for item in presentations
        if item["status"] == "Completed"
    )

    total_tasks = (
        total_assignments +
        total_presentations
    )

    completed_tasks = (
        completed_assignments +
        completed_presentations
    )

    progress = (
        round(
            (completed_tasks / total_tasks) * 100
        )
        if total_tasks
        else 0
    )

    return render_template(
        "index.html",
        assignments=assignments,
        presentations=presentations,
        classes=classes,
        conflicts=conflicts,
        priorities=priorities,
        top_task=top_task,
        recommendation=recommendation,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        progress=progress
    )


# =========================================================
# TIMETABLE
# =========================================================

@app.route("/timetable", methods=["GET", "POST"])
@login_required
def timetable():

    user_id = current_user_id()

    connection = get_db_connection()

    if request.method == "POST":

        connection.execute(
            """
            INSERT INTO timetable
            (
                user_id,
                subject,
                day,
                start_time,
                end_time,
                room
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                request.form["subject"],
                request.form["day"],
                request.form["start_time"],
                request.form["end_time"],
                request.form.get("room", "")
            )
        )

        connection.commit()
        connection.close()

        return redirect(
            url_for("timetable")
        )

    classes = connection.execute(
        """
        SELECT *
        FROM timetable
        WHERE user_id = ?

        ORDER BY
        CASE day
            WHEN 'Monday' THEN 1
            WHEN 'Tuesday' THEN 2
            WHEN 'Wednesday' THEN 3
            WHEN 'Thursday' THEN 4
            WHEN 'Friday' THEN 5
            WHEN 'Saturday' THEN 6
            WHEN 'Sunday' THEN 7
        END,

        start_time
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "timetable.html",
        classes=classes
    )


@app.route(
    "/delete-timetable/<int:class_id>",
    methods=["POST"]
)
@login_required
def delete_timetable(class_id):

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM timetable
        WHERE id = ?
        AND user_id = ?
        """,
        (
            class_id,
            current_user_id()
        )
    )

    connection.commit()
    connection.close()

    return redirect(
        url_for("timetable")
    )


# =========================================================
# ASSIGNMENTS
# =========================================================

@app.route("/assignments", methods=["GET", "POST"])
@login_required
def assignments():

    user_id = current_user_id()

    connection = get_db_connection()

    if request.method == "POST":

        connection.execute(
            """
            INSERT INTO assignments
            (
                user_id,
                title,
                subject,
                deadline,
                estimated_hours,
                importance,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                request.form["title"],
                request.form["subject"],
                request.form["deadline"],
                request.form["estimated_hours"],
                request.form["importance"],
                "Pending"
            )
        )

        connection.commit()
        connection.close()

        return redirect(
            url_for("assignments")
        )

    rows = connection.execute(
        """
        SELECT *
        FROM assignments
        WHERE user_id = ?
        ORDER BY deadline
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "assignments.html",
        assignments=rows
    )


@app.route(
    "/assignment-status/<int:assignment_id>",
    methods=["POST"]
)
@login_required
def update_assignment_status(assignment_id):

    status = request.form.get(
        "status"
    )

    if status not in [
        "Pending",
        "In Progress",
        "Completed"
    ]:

        return redirect(
            url_for("assignments")
        )

    connection = get_db_connection()

    connection.execute(
        """
        UPDATE assignments
        SET status = ?
        WHERE id = ?
        AND user_id = ?
        """,
        (
            status,
            assignment_id,
            current_user_id()
        )
    )

    connection.commit()
    connection.close()

    return redirect(
        url_for("assignments")
    )


@app.route(
    "/delete-assignment/<int:assignment_id>",
    methods=["POST"]
)
@login_required
def delete_assignment(assignment_id):

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM assignments
        WHERE id = ?
        AND user_id = ?
        """,
        (
            assignment_id,
            current_user_id()
        )
    )

    connection.commit()
    connection.close()

    return redirect(
        url_for("assignments")
    )


# =========================================================
# PRESENTATIONS
# =========================================================

@app.route(
    "/presentations",
    methods=["GET", "POST"]
)
@login_required
def presentations():

    user_id = current_user_id()

    connection = get_db_connection()

    if request.method == "POST":

        connection.execute(
            """
            INSERT INTO presentations
            (
                user_id,
                topic,
                subject,
                presentation_date,
                preparation_hours,
                importance,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                request.form["topic"],
                request.form["subject"],
                request.form["presentation_date"],
                request.form["preparation_hours"],
                request.form["importance"],
                "Planned"
            )
        )

        connection.commit()
        connection.close()

        return redirect(
            url_for("presentations")
        )

    rows = connection.execute(
        """
        SELECT *
        FROM presentations
        WHERE user_id = ?
        ORDER BY presentation_date
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "presentations.html",
        presentations=rows
    )


@app.route(
    "/presentation-status/<int:presentation_id>",
    methods=["POST"]
)
@login_required
def update_presentation_status(
    presentation_id
):

    status = request.form.get(
        "status"
    )

    if status not in [
        "Planned",
        "In Progress",
        "Completed"
    ]:

        return redirect(
            url_for("presentations")
        )

    connection = get_db_connection()

    connection.execute(
        """
        UPDATE presentations
        SET status = ?
        WHERE id = ?
        AND user_id = ?
        """,
        (
            status,
            presentation_id,
            current_user_id()
        )
    )

    connection.commit()
    connection.close()

    return redirect(
        url_for("presentations")
    )


@app.route(
    "/delete-presentation/<int:presentation_id>",
    methods=["POST"]
)
@login_required
def delete_presentation(
    presentation_id
):

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM presentations
        WHERE id = ?
        AND user_id = ?
        """,
        (
            presentation_id,
            current_user_id()
        )
    )

    connection.commit()
    connection.close()

    return redirect(
        url_for("presentations")
    )


# =========================================================
# DROP YOUR CHAOS
# =========================================================

@app.route(
    "/chaos",
    methods=["GET", "POST"]
)
@login_required
def chaos():

    result = None

    conflicts = []
    priorities = []
    action_plan = []

    user_id = current_user_id()

    connection = get_db_connection()

    database_assignments = connection.execute(
        """
        SELECT *
        FROM assignments
        WHERE user_id = ?
        ORDER BY deadline
        """,
        (user_id,)
    ).fetchall()

    database_presentations = connection.execute(
        """
        SELECT *
        FROM presentations
        WHERE user_id = ?
        ORDER BY presentation_date
        """,
        (user_id,)
    ).fetchall()

    database_classes = connection.execute(
        """
        SELECT *
        FROM timetable
        WHERE user_id = ?
        ORDER BY start_time
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    if request.method == "POST":

        result = analyze_chaos(
            request.form["chaos_text"]
        )

        for a in database_assignments:

            if a["status"] != "Completed":

                result["assignments"].append(
                    {
                        "title": a["title"],
                        "deadline": a["deadline"],
                        "hours": a["estimated_hours"],
                        "importance": a["importance"],
                        "status": a["status"]
                    }
                )

        for p in database_presentations:

            if p["status"] != "Completed":

                result["presentations"].append(
                    {
                        "topic": p["topic"],
                        "date": p["presentation_date"],
                        "hours": p["preparation_hours"],
                        "importance": p["importance"],
                        "status": p["status"]
                    }
                )

        for c in database_classes:

            result["classes"].append(
                {
                    "subject": c["subject"],
                    "day": c["day"],
                    "start": c["start_time"],
                    "end": c["end_time"],
                    "room": c["room"]
                }
            )

        conflicts = detect_conflicts(
            result
        )

        priorities = calculate_priorities(
            result
        )

        action_plan = create_action_plan(
            priorities,
            result["classes"]
        )

    return render_template(
        "chaos.html",
        result=result,
        conflicts=conflicts,
        priorities=priorities,
        action_plan=action_plan,
        database_assignments=database_assignments,
        database_presentations=database_presentations,
        database_classes=database_classes
    )


# =========================================================
# REMINDERS
# =========================================================

@app.route("/reminders")
@login_required
def reminders():

    user_id = current_user_id()

    connection = get_db_connection()

    assignments = connection.execute(
        """
        SELECT
            title,
            subject,
            deadline,
            estimated_hours,
            importance,
            status

        FROM assignments

        WHERE user_id = ?

        ORDER BY deadline
        """,
        (user_id,)
    ).fetchall()

    presentations = connection.execute(
        """
        SELECT
            topic,
            subject,
            presentation_date,
            preparation_hours,
            importance,
            status

        FROM presentations

        WHERE user_id = ?

        ORDER BY presentation_date
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "reminders.html",
        assignments=assignments,
        presentations=presentations
    )


# =========================================================
# CONFLICTS
# =========================================================

@app.route("/conflicts")
@login_required
def conflicts_page():

    conflicts = detect_conflicts(
        get_active_information()
    )

    return render_template(
        "conflicts.html",
        conflicts=conflicts
    )


# =========================================================
# STUDY SCHEDULE
# =========================================================

@app.route("/schedule")
@login_required
def schedule():

    information = get_active_information()

    study_schedule = create_study_schedule(
        information["classes"],
        information["assignments"],
        information["presentations"]
    )

    return render_template(
        "schedule.html",
        study_schedule=study_schedule
    )


# =========================================================
# DAILY PLAN
# =========================================================

@app.route("/daily-plan")
@login_required
def daily_plan():

    information = get_active_information()

    conflicts = detect_conflicts(
        information
    )

    daily_plan_data = create_daily_plan(
        information["assignments"],
        information["presentations"],
        conflicts
    )

    return render_template(
        "daily_plan.html",
        daily_plan=daily_plan_data
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )