"""demotrack.utils

Handy utility functions for our package
"""

import random

from .model import ExpCondition, Subject


def random_string(strlen):
    """Our little helper function for creating a random string
    """
    return ''.join([
        random.choice('ABCDEFGHIJKLMNPQRSTUVWXYZ0123456789') #Note no O (letter 'OH')
        for _ in range(strlen)
    ])


def create_random_seed_data():
    """Pre-seed the database with random-ish data
    """
    conditions = ExpCondition.find_all()

    # Make sure that we have at least two conditions
    condition_list = set([cond.condition_id for cond in conditions])
    if len(condition_list) < 2:
        if 'A' not in condition_list:
            ExpCondition(
                condition_id="A",
                condition_name="First Condition",
                description="This condition was generated as part of the seed data"
            ).save()
            condition_list.add('A')
        if 'B' not in condition_list:
            ExpCondition(
                condition_id="B",
                condition_name="Second Condition",
                description="This condition was generated as part of the seed data"
            ).save()
            condition_list.add('B')

    # Change our handy set into a list for the call to random.choice below
    condition_list = list(condition_list)

    # Taken from most popular names according to the SSA
    first_names = [
        "Emma", "Olivia", "Sophia", "Isabella", "Ava",
        "Noah", "Liam", "Mason", "Jacob", "William"
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis",
        "Garcia", "Rodriguez", "Wilson", "Martinez", "Anderson", "Taylor",
        "Thomas", "Hernandez", "Moore", "Martin", "Jackson",
    ]

    for _ in range(20):
        subject = Subject(subject_id=random_string(8))
        subject.first_name = random.choice(first_names)
        subject.last_name = random.choice(last_names)
        subject.email = subject.subject_id + "@made-up-people.com"
        subject.exp_condition = random.choice(condition_list)
        subject.save()
