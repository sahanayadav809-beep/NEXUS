from flask import Flask, render_template, request, redirect

from database import get_db_connection, create_tables

from agent.analyzer import analyze_chaos
from agent.conflict_detector import detect_conflicts
from agent.priority_engine import calculate_priorities
from agent.planner import (
    create_action_plan,
    generate_recommendation
)
from agent.schedule_engine import create_study_schedule
from agent.daily_planner import create_daily_plan


app = Flask(__name__)

create_tables()


# ==========================================
# HELPER FUNCTION
# ACTIVE TASKS ONLY
# ==========================================

def get_active_information():

    connection = get_db_connection()

    assignments = connection.execute(
        """
        SELECT *
        FROM assignments
        WHERE status != 'Completed'
        ORDER BY deadline
        """
    ).fetchall()

    presentations = connection.execute(
        """
        SELECT *
        FROM presentations
        WHERE status != 'Completed'
        ORDER BY presentation_date
        """
    ).fetchall()

    classes = connection.execute(
        """
        SELECT *
        FROM timetable
        """
    ).fetchall()

    connection.close()

    information = {
        "assignments": [],
        "presentations": [],
        "classes": []
    }

    for assignment in assignments:

        information["assignments"].append({

            "title": assignment["title"],

            "deadline": assignment["deadline"],

            "hours": assignment["estimated_hours"],

            "importance": assignment["importance"],

            "status": assignment["status"]

        })

    for presentation in presentations:

        information["presentations"].append({

            "topic": presentation["topic"],

            "date": presentation["presentation_date"],

            "hours": presentation["preparation_hours"],

            "importance": presentation["importance"],

            "status": presentation["status"]

        })

    for class_item in classes:

        information["classes"].append({

            "subject": class_item["subject"],

            "day": class_item["day"],

            "start": class_item["start_time"],

            "end": class_item["end_time"],

            "room": class_item["room"]

        })

    return information


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/")
def home():

    connection = get_db_connection()

    assignments = connection.execute(
        """
        SELECT *
        FROM assignments
        ORDER BY deadline
        """
    ).fetchall()

    presentations = connection.execute(
        """
        SELECT *
        FROM presentations
        ORDER BY presentation_date
        """
    ).fetchall()

    classes = connection.execute(
        """
        SELECT *
        FROM timetable
        """
    ).fetchall()

    connection.close()

    information = get_active_information()

    conflicts = detect_conflicts(
        information
    )

    priorities = calculate_priorities(
        information
    )

    top_task = None

    if priorities:
        top_task = priorities[0]

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
        total_assignments
        + total_presentations
    )

    completed_tasks = (
        completed_assignments
        + completed_presentations
    )

    if total_tasks > 0:

        progress = round(
            (
                completed_tasks
                / total_tasks
            ) * 100
        )

    else:

        progress = 0

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


# ==========================================
# TIMETABLE
# ==========================================

@app.route(
    "/timetable",
    methods=["GET", "POST"]
)
def timetable():

    connection = get_db_connection()

    if request.method == "POST":

        subject = request.form["subject"]

        day = request.form["day"]

        start_time = request.form["start_time"]

        end_time = request.form["end_time"]

        room = request.form["room"]

        connection.execute(

            """
            INSERT INTO timetable
            (
                subject,
                day,
                start_time,
                end_time,
                room
            )

            VALUES (?, ?, ?, ?, ?)
            """,

            (
                subject,
                day,
                start_time,
                end_time,
                room
            )

        )

        connection.commit()

        connection.close()

        return redirect("/timetable")

    classes = connection.execute(

        """
        SELECT *
        FROM timetable

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
        """

    ).fetchall()

    connection.close()

    return render_template(

        "timetable.html",

        classes=classes

    )


# ==========================================
# DELETE TIMETABLE CLASS
# ==========================================

@app.route(
    "/delete-timetable/<int:class_id>",
    methods=["POST"]
)
def delete_timetable(class_id):

    connection = get_db_connection()

    connection.execute(

        """
        DELETE FROM timetable
        WHERE id = ?
        """,

        (class_id,)

    )

    connection.commit()

    connection.close()

    return redirect("/timetable")


# ==========================================
# ASSIGNMENTS
# ==========================================

@app.route(
    "/assignments",
    methods=["GET", "POST"]
)
def assignments():

    connection = get_db_connection()

    if request.method == "POST":

        title = request.form["title"]

        subject = request.form["subject"]

        deadline = request.form["deadline"]

        estimated_hours = request.form[
            "estimated_hours"
        ]

        importance = request.form["importance"]

        connection.execute(

            """
            INSERT INTO assignments
            (
                title,
                subject,
                deadline,
                estimated_hours,
                importance,
                status
            )

            VALUES (?, ?, ?, ?, ?, ?)
            """,

            (
                title,
                subject,
                deadline,
                estimated_hours,
                importance,
                "Pending"
            )

        )

        connection.commit()

        connection.close()

        return redirect("/assignments")

    assignments = connection.execute(

        """
        SELECT *
        FROM assignments
        ORDER BY deadline
        """

    ).fetchall()

    connection.close()

    return render_template(

        "assignments.html",

        assignments=assignments

    )


# ==========================================
# UPDATE ASSIGNMENT STATUS
# ==========================================

@app.route(
    "/assignment-status/<int:assignment_id>",
    methods=["POST"]
)
def update_assignment_status(
    assignment_id
):

    status = request.form["status"]

    allowed_statuses = [

        "Pending",

        "In Progress",

        "Completed"

    ]

    if status not in allowed_statuses:

        return redirect("/assignments")

    connection = get_db_connection()

    connection.execute(

        """
        UPDATE assignments

        SET status = ?

        WHERE id = ?
        """,

        (
            status,
            assignment_id
        )

    )

    connection.commit()

    connection.close()

    return redirect("/assignments")


# ==========================================
# DELETE ASSIGNMENT
# ==========================================

@app.route(
    "/delete-assignment/<int:assignment_id>",
    methods=["POST"]
)
def delete_assignment(assignment_id):

    connection = get_db_connection()

    connection.execute(

        """
        DELETE FROM assignments
        WHERE id = ?
        """,

        (assignment_id,)

    )

    connection.commit()

    connection.close()

    return redirect("/assignments")


# ==========================================
# PRESENTATIONS
# ==========================================

@app.route(
    "/presentations",
    methods=["GET", "POST"]
)
def presentations():

    connection = get_db_connection()

    if request.method == "POST":

        topic = request.form["topic"]

        subject = request.form["subject"]

        presentation_date = request.form[
            "presentation_date"
        ]

        preparation_hours = request.form[
            "preparation_hours"
        ]

        importance = request.form["importance"]

        connection.execute(

            """
            INSERT INTO presentations
            (
                topic,
                subject,
                presentation_date,
                preparation_hours,
                importance,
                status
            )

            VALUES (?, ?, ?, ?, ?, ?)
            """,

            (
                topic,
                subject,
                presentation_date,
                preparation_hours,
                importance,
                "Planned"
            )

        )

        connection.commit()

        connection.close()

        return redirect("/presentations")

    presentations = connection.execute(

        """
        SELECT *
        FROM presentations

        ORDER BY presentation_date
        """

    ).fetchall()

    connection.close()

    return render_template(

        "presentations.html",

        presentations=presentations

    )


# ==========================================
# UPDATE PRESENTATION STATUS
# ==========================================

@app.route(
    "/presentation-status/<int:presentation_id>",
    methods=["POST"]
)
def update_presentation_status(
    presentation_id
):

    status = request.form["status"]

    allowed_statuses = [

        "Planned",

        "In Progress",

        "Completed"

    ]

    if status not in allowed_statuses:

        return redirect("/presentations")

    connection = get_db_connection()

    connection.execute(

        """
        UPDATE presentations

        SET status = ?

        WHERE id = ?
        """,

        (
            status,
            presentation_id
        )

    )

    connection.commit()

    connection.close()

    return redirect("/presentations")


# ==========================================
# DELETE PRESENTATION
# ==========================================

@app.route(
    "/delete-presentation/<int:presentation_id>",
    methods=["POST"]
)
def delete_presentation(
    presentation_id
):

    connection = get_db_connection()

    connection.execute(

        """
        DELETE FROM presentations
        WHERE id = ?
        """,

        (presentation_id,)

    )

    connection.commit()

    connection.close()

    return redirect("/presentations")


# ==========================================
# DROP YOUR CHAOS
# ==========================================

@app.route(
    "/chaos",
    methods=["GET", "POST"]
)
def chaos():

    result = None

    conflicts = []

    priorities = []

    action_plan = []

    connection = get_db_connection()

    database_assignments = connection.execute(

        """
        SELECT *
        FROM assignments

        ORDER BY deadline
        """

    ).fetchall()

    database_presentations = connection.execute(

        """
        SELECT *
        FROM presentations

        ORDER BY presentation_date
        """

    ).fetchall()

    database_classes = connection.execute(

        """
        SELECT *
        FROM timetable

        ORDER BY start_time
        """

    ).fetchall()

    connection.close()

    if request.method == "POST":

        chaos_text = request.form[
            "chaos_text"
        ]

        result = analyze_chaos(
            chaos_text
        )

        for assignment in database_assignments:

            if assignment["status"] != "Completed":

                result["assignments"].append({

                    "title":
                    assignment["title"],

                    "deadline":
                    assignment["deadline"],

                    "hours":
                    assignment["estimated_hours"],

                    "importance":
                    assignment["importance"],

                    "status":
                    assignment["status"]

                })

        for presentation in database_presentations:

            if presentation["status"] != "Completed":

                result["presentations"].append({

                    "topic":
                    presentation["topic"],

                    "date":
                    presentation["presentation_date"],

                    "hours":
                    presentation["preparation_hours"],

                    "importance":
                    presentation["importance"],

                    "status":
                    presentation["status"]

                })

        for class_item in database_classes:

            result["classes"].append({

                "subject":
                class_item["subject"],

                "day":
                class_item["day"],

                "start":
                class_item["start_time"],

                "end":
                class_item["end_time"],

                "room":
                class_item["room"]

            })

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

        database_assignments=
        database_assignments,

        database_presentations=
        database_presentations,

        database_classes=
        database_classes

    )


# ==========================================
# REMINDERS
# ==========================================

@app.route("/reminders")
def reminders():

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

        ORDER BY deadline
        """

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

        ORDER BY presentation_date
        """

    ).fetchall()

    connection.close()

    return render_template(

        "reminders.html",

        assignments=assignments,

        presentations=presentations

    )


# ==========================================
# CONFLICTS
# ==========================================

@app.route("/conflicts")
def conflicts_page():

    information = get_active_information()

    conflicts = detect_conflicts(
        information
    )

    return render_template(

        "conflicts.html",

        conflicts=conflicts

    )


# ==========================================
# STUDY SCHEDULE
# ==========================================

@app.route("/schedule")
def schedule():

    information = get_active_information()

    study_schedule = create_study_schedule(

        information["classes"],

        information["assignments"],

        information["presentations"]

    )

    return render_template(

        "schedule.html",

        study_schedule=
        study_schedule

    )


# ==========================================
# DAILY PLAN
# ==========================================

@app.route("/daily-plan")
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

        daily_plan=
        daily_plan_data

    )


# ==========================================
# RUN NEXUS
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )