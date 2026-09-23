# ==========================================
# NEXUS SMART STUDY SCHEDULE ENGINE
# ==========================================

from datetime import datetime


# ==========================================
# TIME → MINUTES
# ==========================================

def time_to_minutes(time_text):

    try:

        time_object = datetime.strptime(
            time_text,
            "%H:%M"
        )

        return (
            time_object.hour * 60
            + time_object.minute
        )

    except:

        return None


# ==========================================
# MINUTES → TIME
# ==========================================

def minutes_to_time(minutes):

    hours = minutes // 60

    mins = minutes % 60

    return f"{hours:02d}:{mins:02d}"


# ==========================================
# DATE → DATE OBJECT
# ==========================================

def date_to_object(date_text):

    try:

        return datetime.strptime(
            date_text,
            "%Y-%m-%d"
        )

    except:

        return None


# ==========================================
# GET AVAILABLE STUDY TIME
# ==========================================

def find_free_slots(
    classes,
    day
):

    day_start = 9 * 60

    day_end = 17 * 60


    busy_slots = []


    # --------------------------------------
    # GET CLASSES FOR SELECTED DAY
    # --------------------------------------

    for class_item in classes:

        class_day = str(
            class_item.get(
                "day",
                ""
            )
        ).strip().lower()


        if class_day != day.lower():

            continue


        start = class_item.get(
            "start",
            ""
        )


        end = class_item.get(
            "end",
            ""
        )


        start_minutes = time_to_minutes(
            start
        )


        end_minutes = time_to_minutes(
            end
        )


        if (
            start_minutes is not None
            and end_minutes is not None
        ):

            busy_slots.append(
                (
                    start_minutes,
                    end_minutes
                )
            )


    # --------------------------------------
    # SORT CLASSES
    # --------------------------------------

    busy_slots.sort()


    # --------------------------------------
    # FIND FREE PERIODS
    # --------------------------------------

    free_slots = []

    current_time = day_start


    for start, end in busy_slots:

        if start > current_time:

            free_slots.append({

                "start":
                current_time,

                "end":
                start

            })


        if end > current_time:

            current_time = end


    # --------------------------------------
    # AFTER LAST CLASS
    # --------------------------------------

    if current_time < day_end:

        free_slots.append({

            "start":
            current_time,

            "end":
            day_end

        })


    return free_slots


# ==========================================
# CREATE TASK LIST
# ==========================================

def create_tasks(
    assignments,
    presentations
):

    tasks = []


    # ======================================
    # ASSIGNMENTS
    # ======================================

    for assignment in assignments:

        try:

            hours = int(
                assignment.get(
                    "hours",
                    1
                )
            )

        except:

            hours = 1


        if hours < 1:

            hours = 1


        tasks.append({

            "title":
            assignment.get(
                "title",
                "Assignment"
            ),

            "type":
            "Assignment",

            "deadline":
            assignment.get(
                "deadline",
                ""
            ),

            "hours":
            hours,

            "importance":
            assignment.get(
                "importance",
                "Medium"
            )

        })


    # ======================================
    # PRESENTATIONS
    # ======================================

    for presentation in presentations:

        try:

            hours = int(
                presentation.get(
                    "hours",
                    1
                )
            )

        except:

            hours = 1


        if hours < 1:

            hours = 1


        tasks.append({

            "title":
            presentation.get(
                "topic",
                "Presentation"
            ),

            "type":
            "Presentation",

            "deadline":
            presentation.get(
                "date",
                ""
            ),

            "hours":
            hours,

            "importance":
            presentation.get(
                "importance",
                "Medium"
            )

        })


    return tasks


# ==========================================
# SORT TASKS
# ==========================================

def sort_tasks(tasks):

    def sort_key(task):

        deadline = date_to_object(
            task["deadline"]
        )


        # High importance comes first
        importance = task[
            "importance"
        ].lower()


        if importance == "high":

            importance_value = 1

        elif importance == "medium":

            importance_value = 2

        else:

            importance_value = 3


        if deadline is None:

            return (
                datetime.max,
                importance_value
            )


        return (
            deadline,
            importance_value
        )


    tasks.sort(
        key=sort_key
    )


# ==========================================
# CREATE SMART SCHEDULE
# ==========================================

def create_study_schedule(
    classes,
    assignments,
    presentations
):

    schedule = []


    days = [

        "Monday",

        "Tuesday",

        "Wednesday",

        "Thursday",

        "Friday"

    ]


    # ======================================
    # CREATE TASKS
    # ======================================

    tasks = create_tasks(

        assignments,

        presentations

    )


    # ======================================
    # SORT BY DEADLINE
    # ======================================

    sort_tasks(tasks)


    # ======================================
    # CREATE AVAILABLE SLOTS
    # ======================================

    all_slots = []


    for day in days:

        free_slots = find_free_slots(

            classes,

            day

        )


        for slot in free_slots:

            all_slots.append({

                "day":
                day,

                "start":
                slot["start"],

                "end":
                slot["end"]

            })


    # ======================================
    # ALLOCATE TASKS
    # ======================================

    for task in tasks:

        remaining_minutes = (
            task["hours"] * 60
        )


        deadline = date_to_object(
            task["deadline"]
        )


        for slot in all_slots:

            if remaining_minutes <= 0:

                break


            # --------------------------------
            # AVAILABLE STUDY SLOT
            # --------------------------------

            start = slot["start"]

            end = slot["end"]


            available_minutes = (
                end - start
            )


            if available_minutes < 30:

                continue


            # --------------------------------
            # MAX 2 HOURS PER SESSION
            # --------------------------------

            study_minutes = min(

                available_minutes,

                remaining_minutes,

                120

            )


            if study_minutes < 30:

                continue


            study_end = (
                start
                + study_minutes
            )


            schedule.append({

                "day":
                slot["day"],

                "start":
                minutes_to_time(
                    start
                ),

                "end":
                minutes_to_time(
                    study_end
                ),

                "task":
                task["title"],

                "type":
                task["type"],

                "importance":
                task["importance"],

                "deadline":
                task["deadline"],

                "hours":
                round(
                    study_minutes / 60,
                    1
                )

            })


            # --------------------------------
            # UPDATE FREE SLOT
            # --------------------------------

            slot["start"] = study_end


            remaining_minutes -= (
                study_minutes
            )


        # ==================================
        # IF WORK REMAINS
        # ==================================

        if remaining_minutes > 0:

            schedule.append({

                "day":
                "⚠️ Unscheduled",

                "start":
                "--",

                "end":
                "--",

                "task":
                task["title"],

                "type":
                task["type"],

                "importance":
                task["importance"],

                "deadline":
                task["deadline"],

                "hours":
                round(
                    remaining_minutes / 60,
                    1
                )

            })


    return schedule