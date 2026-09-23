from datetime import datetime


# ==========================================
# CALCULATE ALL TASK PRIORITIES
# ==========================================

def calculate_priorities(information):

    tasks = []


    # ==========================================
    # ASSIGNMENTS
    # ==========================================

    for assignment in information.get("assignments", []):

        deadline = assignment.get("deadline")

        estimated_hours = assignment.get("hours", 1)

        importance = assignment.get(
            "importance",
            "Medium"
        )

        priority = calculate_priority(
            deadline,
            estimated_hours,
            importance
        )

        tasks.append({

            "name": assignment["title"],

            "type": "Assignment",

            "date": deadline,

            "hours": estimated_hours,

            "importance": importance,

            "priority": priority

        })


    # ==========================================
    # PRESENTATIONS
    # ==========================================

    for presentation in information.get("presentations", []):

        date = presentation.get("date")

        preparation_hours = presentation.get(
            "hours",
            1
        )

        importance = presentation.get(
            "importance",
            "Medium"
        )

        priority = calculate_priority(
            date,
            preparation_hours,
            importance
        )

        tasks.append({

            "name": presentation["topic"],

            "type": "Presentation",

            "date": date,

            "hours": preparation_hours,

            "importance": importance,

            "priority": priority

        })


    # ==========================================
    # PRIORITY ORDER
    # ==========================================

    priority_order = {

        "URGENT": 1,

        "HIGH": 2,

        "MEDIUM": 3,

        "LOW": 4

    }


    tasks.sort(

        key=lambda task:
        priority_order.get(
            task["priority"],
            5
        )

    )


    return tasks


# ==========================================
# CALCULATE SINGLE TASK PRIORITY
# ==========================================

def calculate_priority(
    date,
    hours,
    importance="Medium"
):

    try:

        # Convert database date
        # Example: 2026-09-28

        deadline = datetime.strptime(
            str(date),
            "%Y-%m-%d"
        )


        # Today's date

        today = datetime.now()


        # Calculate remaining days

        days_left = (
            deadline.date() - today.date()
        ).days


        # Convert hours safely

        try:

            hours = int(hours)

        except:

            hours = 1


        if hours < 1:

            hours = 1


        # Convert importance to lowercase

        importance = str(
            importance
        ).lower().strip()


        # ==========================================
        # URGENT
        # ==========================================

        if days_left < 0:

            return "URGENT"


        if days_left <= 1:

            return "URGENT"


        # ==========================================
        # HIGH
        # ==========================================

        # Very important task

        if importance == "high" and days_left <= 7:

            return "HIGH"


        # Heavy workload with limited time

        if days_left <= 3:

            return "HIGH"


        if days_left <= 7 and hours >= 6:

            return "HIGH"


        # ==========================================
        # MEDIUM
        # ==========================================

        if importance == "high":

            return "MEDIUM"


        if days_left <= 7:

            return "MEDIUM"


        if days_left <= 14 and hours >= 8:

            return "MEDIUM"


        if importance == "medium":

            return "MEDIUM"


        # ==========================================
        # LOW
        # ==========================================

        return "LOW"


    except:

        return "MEDIUM"