# ==========================================
# NEXUS CONFLICT DETECTOR
# ==========================================


def detect_conflicts(information):

    conflicts = []


    assignments = information.get(
        "assignments",
        []
    )

    presentations = information.get(
        "presentations",
        []
    )

    classes = information.get(
        "classes",
        []
    )


    # ==========================================
    # 1. ASSIGNMENT + PRESENTATION
    #    SAME DATE
    # ==========================================

    for assignment in assignments:

        for presentation in presentations:

            assignment_date = str(
                assignment.get(
                    "deadline",
                    ""
                )
            ).strip()


            presentation_date = str(
                presentation.get(
                    "date",
                    ""
                )
            ).strip()


            if (
                assignment_date
                and presentation_date
                and assignment_date == presentation_date
            ):

                conflicts.append({

                    "type":
                    "Deadline Conflict",

                    "message":
                    (
                        f"{assignment['title']} and "
                        f"{presentation['topic']} "
                        f"are scheduled for the same date."
                    )

                })


    # ==========================================
    # 2. MULTIPLE ASSIGNMENTS
    #    SAME DATE
    # ==========================================

    for i in range(
        len(assignments)
    ):

        for j in range(
            i + 1,
            len(assignments)
        ):

            first = assignments[i]

            second = assignments[j]


            first_date = str(
                first.get(
                    "deadline",
                    ""
                )
            ).strip()


            second_date = str(
                second.get(
                    "deadline",
                    ""
                )
            ).strip()


            if (
                first_date
                and second_date
                and first_date == second_date
            ):

                conflicts.append({

                    "type":
                    "Assignment Conflict",

                    "message":
                    (
                        f"{first['title']} and "
                        f"{second['title']} "
                        f"have the same deadline."
                    )

                })


    # ==========================================
    # 3. MULTIPLE PRESENTATIONS
    #    SAME DATE
    # ==========================================

    for i in range(
        len(presentations)
    ):

        for j in range(
            i + 1,
            len(presentations)
        ):

            first = presentations[i]

            second = presentations[j]


            first_date = str(
                first.get(
                    "date",
                    ""
                )
            ).strip()


            second_date = str(
                second.get(
                    "date",
                    ""
                )
            ).strip()


            if (
                first_date
                and second_date
                and first_date == second_date
            ):

                conflicts.append({

                    "type":
                    "Presentation Conflict",

                    "message":
                    (
                        f"{first['topic']} and "
                        f"{second['topic']} "
                        f"are scheduled for the same date."
                    )

                })


    # ==========================================
    # 4. CALCULATE DAILY WORKLOAD
    # ==========================================

    workload = {}


    # ASSIGNMENT HOURS

    for assignment in assignments:

        date = str(
            assignment.get(
                "deadline",
                ""
            )
        ).strip()


        hours = assignment.get(
            "hours",
            1
        )


        try:

            hours = int(hours)

        except:

            hours = 1


        if date:

            workload[date] = (
                workload.get(
                    date,
                    0
                )
                + hours
            )


    # PRESENTATION HOURS

    for presentation in presentations:

        date = str(
            presentation.get(
                "date",
                ""
            )
        ).strip()


        hours = presentation.get(
            "hours",
            1
        )


        try:

            hours = int(hours)

        except:

            hours = 1


        if date:

            workload[date] = (
                workload.get(
                    date,
                    0
                )
                + hours
            )


    # ==========================================
    # 5. HEAVY WORKLOAD
    # ==========================================

    for date, hours in workload.items():

        if hours > 5:

            conflicts.append({

                "type":
                "Heavy Workload",

                "message":
                (
                    f"You have approximately "
                    f"{hours} hours of academic "
                    f"work connected to {date}."
                )

            })


    # ==========================================
    # 6. VERY HEAVY WORKLOAD
    # ==========================================

    for date, hours in workload.items():

        if hours > 8:

            conflicts.append({

                "type":
                "Critical Workload",

                "message":
                (
                    f"Your workload for {date} "
                    f"is approximately {hours} hours. "
                    f"Consider starting some tasks earlier."
                )

            })


    return conflicts