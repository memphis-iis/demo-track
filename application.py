#!/usr/bin/env python

import os
import random
import logging
import datetime

import flask
from flask import Flask, render_template, request, abort, flash, redirect, url_for

from demotrack.model import Subject, ExpCondition, ensure_tables
from demotrack.utils import random_string, create_random_seed_data


# Note that application as the main WSGI app is required for Python apps
# on Elastic Beanstalk
application = Flask(__name__)
application.secret_key = application.config.get('FLASK_SECRET', "My Default Secret")


# This will be called before the first request is ever serviced
@application.before_first_request
def before_first():
    ensure_tables()


# This will be called before every request, so we can set up any global data that
# we want all requests to see
@application.before_request
def before_request():
    flask.g.year = datetime.datetime.now().year


#Helper for logic we use multiple times
def find_condition_stats(subjects, conditions=None):
    """Given a list of subjects, return a sorted list of condition 'stats' -
    dictionaries corresponding to an ExpCondition instance with the added
    key 'subject_count'
    """
    # Use our special data handling to turn conditions in dictionaries we can
    # use for holding some stats for the home page
    if not conditions:
        conditions = ExpCondition.find_all()

    condition_stats = [cond.get_item() for cond in conditions]

    # Build a cross-reference from condition ID's to the index in our
    # condition_stats list. While we're at it, we also initialize counts
    condition_ref = {}
    for idx, cond in enumerate(condition_stats):
        condition_ref[cond['condition_id']] = idx
        cond['subject_count'] = 0

    # Now gather per-condition counts
    for subject in subjects:
        cid = subject.exp_condition
        if cid in condition_ref:
            # Normal - find our item using our cross ref and up the subject count
            idx = condition_ref[cid]
            condition_stats[idx]['subject_count'] += 1
        else:
            # Whoops - somehow we have a condition not seen before - display stats
            # for it but make sure they know this is a problem
            cond = ExpCondition(condition_id=cid, condition_name="MISSING CONDITION").get_item()
            cond['subject_count'] = 1
            condition_ref[cid] = len(condition_stats)
            condition_stats.append(cond)

    return condition_stats


#Our home/index page
@application.route('/')
@application.route('/home')
def main_page():
    subjects = Subject.find_all()
    condition_stats = find_condition_stats(subjects)
    return render_template("home.html", **locals())



# A POST request to the URL is a request to generate random data
@application.route('/utils/randomize', methods=['POST'])
def random_seed_data():
    create_random_seed_data()
    return redirect(url_for('main_page'))


# View all the current subject
@application.route('/subjects')
def subjects():
    subjects=Subject.find_all()
    condition_names = dict([
        (cond.condition_id, cond.condition_name)
        for cond in ExpCondition.find_all()
    ])
    return render_template("subjects_all.html", **locals())


# View a single subject
@application.route('/subjects/<sid>')
def subject_view(sid=None):
    subject = Subject.find(sid)
    if not subject:
        abort(404) #Subject not found

    condition = ExpCondition.find(subject.exp_condition)

    return render_template("subject_view.html", **locals())


# Edit a single subject
@application.route('/subjects/<sid>/edit', methods=['GET', 'POST'])
def subject_edit(sid=None):
    if sid == "new":
        #For new subjects, if we aren't getting an ID specified, we'll make up a
        #(short-ish) subject ID (but they are allowed to change it)
        new_id = request.form.get("subject_id", "") or random_string(8)
        subject = Subject(subject_id=new_id, first_name="", last_name="", email="", exp_condition="")
        allow_key_edit = True
    else:
        subject = Subject.find(sid)
        allow_key_edit = False

    if not subject:
        abort(404) #Subject not found

    conditions = ExpCondition.find_all()
    condition_stats = find_condition_stats(Subject.find_all(), conditions)

    #Get a list of the experimental conditions with the least subjects
    min_conditions = []
    if condition_stats:
        min_count = min(cond['subject_count'] for cond in condition_stats)
        for cond in condition_stats:
            if cond['subject_count'] <= min_count:
                min_conditions.append(cond['condition_id'])

    if request.method == "GET":
        #Show edit view
        errors = list()
        return render_template("subject_edit.html", **locals())

    elif request.method == "POST":
        subject.subject_id = request.form.get("subject_id", "")
        subject.first_name = request.form.get("first_name", "")
        subject.last_name = request.form.get("last_name", "")
        subject.email = request.form.get("email", "")
        subject.exp_condition = request.form.get("exp_condition", "")

        errors = list(subject.errors())
        if not errors:
            #Perform any extra checks for a valid subject
            if subject.exp_condition not in [c.condition_id for c in conditions]:
                errors.append("A subject must have an experimental condition")

        if errors:
            return render_template("subject_edit.html", **locals())

        subject.save()
        flash("Subject %s saved" % subject.subject_id)
        return redirect(url_for('subjects'))

    else:
        #Shouldn't happen - but let's be overly cautious :)
        abort(405)


# View all experimental conditions
@application.route('/conds')
def conditions():
    conditions = ExpCondition.find_all()
    condition_stats = dict([
        (cond['condition_id'], cond['subject_count'])
        for cond in find_condition_stats(Subject.find_all(), conditions)
    ])
    return render_template("conditions_all.html", **locals())


# View a single experimental condition
@application.route('/conds/<cid>')
def condition_view(cid=None):
    condition = ExpCondition.find(cid)
    if not condition:
        abort(404) #Conditions not found

    subjects = [subj for subj in Subject.find_all() if subj.exp_condition == cid]

    return render_template("condition_view.html", **locals())


# Edit an experimental condition
@application.route('/conds/<cid>/edit', methods=['GET', 'POST'])
def condition_edit(cid=None):
    if cid == "new":
        condition = ExpCondition(condition_id="", condition_name="", description="")
        allow_key_edit = True
    else:
        condition = ExpCondition.find(cid)
        allow_key_edit = False

    if not condition:
        abort(404) #Subject not found

    if request.method == "GET":
        #Show edit view
        errors = list()
        return render_template("condition_edit.html", **locals())

    elif request.method == "POST":
        condition.condition_id = request.form.get("condition_id", "")
        condition.condition_name = request.form.get("condition_name", "")
        condition.description = request.form.get("description", "")

        errors = list(condition.errors())
        if errors:
            return render_template("condition_edit.html", **locals())

        condition.save()
        flash("Condition %s saved" % condition.condition_id)
        return redirect(url_for('conditions'))

    else:
        #Shouldn't happen - but let's be overly cautious :)
        abort(405)


# Final app settings depending on whether or not we are set for debug mode
if os.environ.get('DEBUG', None):
    # Debug mode - running on a workstation
    application.debug = True
    logging.basicConfig(level=logging.DEBUG)
else:
    # We are running on AWS Elastic Beanstalk (or something like it)
    application.debug = False
    logging.basicConfig(level=logging.INFO)


# Our entry point - called when our application is started "locally". NOTE that
# this WILL NOT be run by Elastic Beanstalk
def main():
    application.run()
if __name__ == '__main__':
    main()
