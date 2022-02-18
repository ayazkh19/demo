"""
    this file is part of web application in flask framework
    this is partial views file containing view logic of application
    and is not workable standalone
    only for demonstration purpose
"""


from flask import Blueprint,render_template,redirect,url_for, request, flash, jsonify, make_response
from flask_security import login_required, roles_required, roles_accepted
from myproject.models import *
from sqlalchemy import and_, or_
import requests
import json
from flask_login import login_user
from datetime import datetime
from myproject.helper import (get_unfiltered_projectlist,
                              get_filtered_projectlist,
                              get_date_for_sqlite,
                              compare_date_range,
                              format_date)

#######################################################################################################
############################    BLUEPRINT    ################################################
#######################################################################################################

P_blueprint = Blueprint('P',__name__, template_folder='templates/P')

###################################################################################
############################    ROUTING    ########################################
###################################################################################
@P_blueprint.route('/')
def pcindex():
    return render_template('pcindex.html')

## 2. List with projects
@P_blueprint.route('/projectlist')
def projectlist():
    CurrentUserId = request.cookies.get('CurrentUserId')
    print(CurrentUserId)
    return render_template('projectslist.html')


## 3. Map with projects (TO BE MADE)
@P_blueprint.route('/projectmap')
def wdt():
    return render_template('projectsmap.html')


# reg project via ajx
@P_blueprint.route('regProjAjx', methods=['POST'])
def reg_new_proj():
    # via ajax
    if request.method == 'POST':
        project_name = request.form.get('ProjectName')
        project_number = request.form.get('ProjectNumber')
        start_date = request.form.get('daterange')[0:10]
        end_date = request.form.get('daterange')[12:]
        remarks = request.form.get('ProjectRemarks')
        loc_lat = request.form.get('LocLat')
        loc_lon = request.form.get('LocLon')

        # checking for duplicate project name and number
        if (Project.query.filter(Project.ProjectName == project_name).count() + Project.query.filter(
                Project.ProjectNumber == project_number).count()) < 1:
            # converting start and end date to python datetime object
            start_date = get_date_for_sqlite(start_date, datetime)
            end_date = get_date_for_sqlite(end_date, datetime)

            new_project = Project(project_name, project_number, start_date, end_date, remarks, loc_lat, loc_lon)
            db.session.add(new_project)
            db.session.commit()

            return jsonify({'msg': 'created'})
        else:
            if (Project.query.filter(Project.ProjectNumber == project_number).count() > 0) & (
                    Project.query.filter(Project.ProjectName == project_name).count() > 0):
                return jsonify({'msg': 'name/code'})
            if (Project.query.filter(Project.ProjectName == project_name).count() > 0) & (
                    Project.query.filter(Project.ProjectNumber == project_number).count() == 0):
                return jsonify({'msg': 'name'})
            if (Project.query.filter(Project.ProjectNumber == project_number).count() > 0) & (
                    Project.query.filter(Project.ProjectName == project_name).count() == 0):
                return jsonify({'msg': 'code'})
            return jsonify({'msg': 'unexpected'})


# 4. Project registration
@P_blueprint.route('/projectregistration',methods = ['GET','POST'])
def projectregistration():
    if request.method == "POST":
        project_name = request.form["ProjectName"]
        project_number = request.form["ProjectNumber"]
        start_date = request.form["daterange"][0:10]
        end_date = request.form["daterange"][12:]
        remarks = request.form["ProjectRemarks"]
        loc_lat = request.form["LocLat"]
        loc_lon = request.form["LocLon"]
        # print('start date: ', start_date)
        # print('end date: ', end_date)
        # checking for duplicate project name and number
        if ( Project.query.filter(Project.ProjectName==project_name).count() + Project.query.filter(Project.ProjectNumber==project_number).count() ) < 1:
            # converting start and end date to python datetime object
            start_date = get_date_for_sqlite(start_date, datetime)
            end_date = get_date_for_sqlite(end_date, datetime)

            new_project = Project(project_name, project_number, start_date, end_date, remarks,loc_lat, loc_lon)
            db.session.add(new_project)
            db.session.commit()
            flash('The project with number "'+ request.form["ProjectNumber"] + '" and name "'+ request.form["ProjectName"] + '" was registered succesfully')
            return render_template('projectslist.html') # return redirect(request.url)
        else:
            if (Project.query.filter(Project.ProjectNumber==request.form["ProjectNumber"]).count() > 0) & (Project.query.filter(Project.ProjectName==request.form["ProjectName"]).count() > 0):
                flash('This project cannot be registered because both the project code "' + request.form["ProjectNumber"] + '" and the project name "' + request.form["ProjectName"] + '" already exist')
            if (Project.query.filter(Project.ProjectName==request.form["ProjectName"]).count() > 0) & (Project.query.filter(Project.ProjectNumber==request.form["ProjectNumber"]).count() == 0):
                flash('This project cannot be registered because the project name "' + request.form["ProjectName"] + '" already exists')
            if (Project.query.filter(Project.ProjectNumber==request.form["ProjectNumber"]).count() > 0) & (Project.query.filter(Project.ProjectName==request.form["ProjectName"]).count() == 0):
                flash('This project cannot be registered because the project code "' + request.form["ProjectNumber"] + '" already exists')
            return render_template('projectregistration.html')
    return render_template('projectregistration.html')


# 5. Project specific [single project view]
@P_blueprint.route('/<ProjectNumber>')
def projectselected(ProjectNumber):
        SelectedProject = db.session.query(Project).filter(Project.ProjectNumber == ProjectNumber).all()
        return render_template('projectselected.html', Project=SelectedProject[0], mainlocations=SelectedProject[0].locationMains,
                               project_id=SelectedProject[0].Id, project_number=ProjectNumber, ProjectEmePlatenumbers = SelectedProject[0].projectEmePlatenumbers)


#eme cat data
@P_blueprint.route('/getEmeData', methods=['POST'])
def get_eme_data():
    data = []
    if request.method == 'POST':
        if request.args.get('param') == 'emeCat':
            ret = db.session.query(EmeCategory).all()
            if ret:
                for row in ret:
                    data.append({
                        'id': row.Id,
                        'name': row.EmeCategoryName
                    })
                return jsonify(data)

