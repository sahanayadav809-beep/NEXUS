# ==========================================
# CREATE ACTION PLAN
# ==========================================

def create_action_plan(tasks, classes=None):

    plan = []

    if classes is None:
        classes = []


    for task in tasks:

        priority = task.get(
            "priority",
            "MEDIUM"
        )

        task_type = task.get(
            "type",
            "Task"
        )

        hours = task.get(
            "hours",
            1
        )

        date = task.get(
            "date"
        )

        importance = task.get(
            "importance",
            "Medium"
        )


        # Convert hours safely

        try:

            hours = int(hours)

        except:

            hours = 1


        if hours < 1:

            hours = 1


        # ==========================================
        # CREATE SMALL STEPS
        # ==========================================

        if task_type == "Assignment":

            steps = [

                f"Understand the requirements of {task['name']}.",

                "Collect the required study material.",

                "Complete the main assignment work.",

                "Review the answers and correct mistakes.",

                "Finalize and submit the assignment."

            ]


        elif task_type == "Presentation":

            steps = [

                f"Research the topic: {task['name']}.",

                "Prepare the main presentation content.",

                "Create and organize the slides.",

                "Review the presentation for errors.",

                "Practice the presentation before presenting."

            ]


        else:

            steps = [

                f"Understand the requirements of {task['name']}.",

                "Collect the required information.",

                "Complete the main work.",

                "Review the completed work.",

                "Finalize the task."

            ]


        # ==========================================
        # PRIORITY ADVICE
        # ==========================================

        if priority == "URGENT":

            priority_advice = (

                "Start this task immediately because "
                "the deadline is very close or has passed."

            )


        elif priority == "HIGH":

            priority_advice = (

                "Start this task today and give it "
                "focused study time."

            )


        elif priority == "MEDIUM":

            priority_advice = (

                "Schedule dedicated time for this task "
                "before the deadline."

            )


        else:

            priority_advice = (

                "Keep this task in your planned workload "
                "and complete higher-priority tasks first."

            )


        # ==========================================
        # IMPORTANCE ADVICE
        # ==========================================

        if str(importance).lower() == "high":

            importance_advice = (

                "This task is marked HIGH importance, "
                "so give it additional attention."

            )

        elif str(importance).lower() == "medium":

            importance_advice = (

                "This task has MEDIUM importance."

            )

        else:

            importance_advice = (

                "This task has LOW importance and can "
                "follow higher-priority work."

            )


        # ==========================================
        # TIMETABLE ADVICE
        # ==========================================

        timetable_advice = ""

        if classes:

            timetable_advice = (

                " Keep your scheduled classes in mind "
                "when selecting study time."

            )


        # ==========================================
        # COMPLETE ACTION DESCRIPTION
        # ==========================================

        action = (

            priority_advice
            + " "
            + importance_advice
            + timetable_advice

        )


        # ==========================================
        # ADD PLAN
        # ==========================================

        plan.append({

            "task": task["name"],

            "type": task_type,

            "date": date,

            "hours": hours,

            "priority": priority,

            "importance": importance,

            "steps": steps,

            "action": action

        })


    return plan


# ==========================================
# NEXUS RECOMMENDATION
# ==========================================

def generate_recommendation(tasks, conflicts):

    if not tasks:

        return (

            "No academic tasks are available yet. "

            "Add assignments or presentations "
            "to get a recommendation."

        )


    # ==========================================
    # TOP TASK
    # ==========================================

    top_task = tasks[0]


    task_name = top_task.get(
        "name",
        "your task"
    )

    priority = top_task.get(
        "priority",
        "MEDIUM"
    )

    date = top_task.get(
        "date",
        "an upcoming date"
    )

    hours = top_task.get(
        "hours",
        1
    )

    importance = top_task.get(
        "importance",
        "Medium"
    )


    # ==========================================
    # CONFLICT MESSAGE
    # ==========================================

    conflict_message = ""


    if conflicts:

        conflict_message = (

            f" NEXUS also detected "
            f"{len(conflicts)} conflict(s), "
            f"so review the conflict section."

        )


    # ==========================================
    # RECOMMENDATION
    # ==========================================

    if priority == "URGENT":

        return (

            f"NEXUS recommends starting with "
            f"{task_name} immediately. "

            f"It is marked {priority} priority, "
            f"has a deadline of {date}, "
            f"requires approximately {hours} hour(s), "
            f"and has {importance} importance."

            f"{conflict_message}"

        )


    elif priority == "HIGH":

        return (

            f"NEXUS recommends prioritizing "
            f"{task_name} today. "

            f"It is marked {priority} priority, "
            f"has a deadline of {date}, "
            f"requires approximately {hours} hour(s), "
            f"and has {importance} importance."

            f"{conflict_message}"

        )


    elif priority == "MEDIUM":

        return (

            f"NEXUS recommends scheduling "
            f"{task_name} soon. "

            f"It has {priority} priority, "
            f"a deadline of {date}, "
            f"requires approximately {hours} hour(s), "
            f"and has {importance} importance."

            f"{conflict_message}"

        )


    else:

        return (

            f"NEXUS recommends keeping "
            f"{task_name} in your planned workload. "

            f"It has {priority} priority, "
            f"a deadline of {date}, "
            f"requires approximately {hours} hour(s), "
            f"and has {importance} importance."

            f"{conflict_message}"

        )