# ==========================================
# NEXUS DAILY AI ACTION PLANNER
# ==========================================

from datetime import datetime


# ==========================================
# GET DATE
# ==========================================

def get_date(date_text):

    try:

        return datetime.strptime(
            date_text,
            "%Y-%m-%d"
        )

    except:

        return None


# ==========================================
# CREATE DAILY ACTION PLAN
# ==========================================

def create_daily_plan(
    assignments,
    presentations,
    conflicts
):

    tasks = []


    # ======================================
    # ADD ASSIGNMENTS
    # ======================================

    for assignment in assignments:

        deadline = assignment.get(
            "deadline",
            ""
        )

        try:

            hours = int(
                assignment.get(
                    "hours",
                    1
                )
            )

        except:

            hours = 1


        importance = str(
            assignment.get(
                "importance",
                "Medium"
            )
        )


        tasks.append({

            "title":
            assignment.get(
                "title",
                "Assignment"
            ),

            "type":
            "Assignment",

            "deadline":
            deadline,

            "hours":
            hours,

            "importance":
            importance,

            "action":
            "Work on this assignment"

        })


    # ======================================
    # ADD PRESENTATIONS
    # ======================================

    for presentation in presentations:

        deadline = presentation.get(
            "date",
            ""
        )

        try:

            hours = int(
                presentation.get(
                    "hours",
                    1
                )
            )

        except:

            hours = 1


        importance = str(
            presentation.get(
                "importance",
                "Medium"
            )
        )


        tasks.append({

            "title":
            presentation.get(
                "topic",
                "Presentation"
            ),

            "type":
            "Presentation",

            "deadline":
            deadline,

            "hours":
            hours,

            "importance":
            importance,

            "action":
            "Prepare your presentation"

        })


    # ======================================
    # SORT TASKS
    # ======================================

    def task_sort(task):

        deadline = get_date(
            task["deadline"]
        )


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
        key=task_sort
    )


    # ======================================
    # ADD PRIORITY
    # ======================================

    for index, task in enumerate(tasks):

        if index == 0:

            task["priority"] = "TOP"

        elif index == 1:

            task["priority"] = "NEXT"

        else:

            task["priority"] = "LATER"


    # ======================================
    # GENERATE SUMMARY
    # ======================================

    if not tasks:

        summary = (
            "No academic tasks found. "
            "Add assignments or presentations "
            "to create your action plan."
        )

    else:

        top = tasks[0]

        summary = (
            f"Focus first on "
            f"{top['title']}. "
            f"It is the next task in your "
            f"academic workload."
        )


    # ======================================
    # CONFLICT SUMMARY
    # ======================================

    conflict_count = len(
        conflicts
    )


    if conflict_count == 0:

        conflict_message = (
            "No detected academic conflicts."
        )

    elif conflict_count == 1:

        conflict_message = (
            "⚠️ 1 academic conflict "
            "needs attention."
        )

    else:

        conflict_message = (
            f"⚠️ {conflict_count} academic "
            f"conflicts need attention."
        )


    return {

        "tasks":
        tasks,

        "summary":
        summary,

        "conflict_message":
        conflict_message,

        "conflict_count":
        conflict_count

    }