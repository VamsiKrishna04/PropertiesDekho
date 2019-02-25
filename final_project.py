from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Project, Property, User

# Import Flask class from flask library
# request to get form data
# jsonify to configure endpoint for application
from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify
# Works as dictionary To store values 
# for longetivity of user's session with server
from flask import session as login_session
# Random , String To create pseudo random string
# which will identify each session
import random
import string
# flow_from_clientsecrets method creates flow object
# from clientsecrets json file
# which stores client id, client secret, and other OAuth parameters
from oauth2client.client import flow_from_clientsecrets
# FlowExchangeError to catch if any error occours when trying 2 exchange
# authorization code for access token
from oauth2client.client import FlowExchangeError
# HTTP client library
import httplib2
# To convert in memory objects to json
import json
# make_response method used to convert returned value from function
# into real response object we can send of to the client
from flask import make_response
# it is a HTTP library
import requests


# create the instance of the Flask class
# with the name of the running application as argument
app = Flask(__name__)


# Connect to Database and create database session
engine = create_engine('sqlite:///propertieswithusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = scoped_session(DBSession)


# To Show All The Projects
# Below function gets executed when
# user enter any of below 2 routes in browser
@app.route('/')
@app.route('/projects/')
def showProjects():
    # To read everything from table Project
    projects = session.query(Project).all()
    if 'username' not in login_session:
        # Flask configures a template engine to store html code
        # pass html file name and variable/keyword
        return render_template('publicProjects.html', projects=projects)
    else:
        return render_template('showProjects.html', projects=projects)


# To Create a New Project
@app.route('/project/new', methods=['GET', 'POST'])
def newProject():
    # If user is not logged in redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newProject = Project(
            project_name=request.form[
                'newProjectName'], user_id=login_session['user_id'])
        session.add(newProject)
        session.commit()
        flash("New Project %s is Created! " % (newProject.project_name))
        return redirect(url_for('showProjects'))
    else:
        return render_template('newProject.html')


# To Edit a Project
# We are adding variable to the url i.e project_id
@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
def editProject(project_id):
    editProjectName = session.query(Project).filter_by(
        project_id=project_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editProjectName.user_id != login_session['user_id']:
        flash("You didn't add this Project, so you can't edit it. Sorry :-(")
        return redirect(url_for('showProjects'))
    if request.method == 'POST':
        if request.form['editedProjectName']:
            prev_name = editProjectName.project_name
            # Update with user entered ProjectName
            editProjectName.project_name = request.form['editedProjectName']
        session.add(editProjectName)
        session.commit()
        flash(
            "Project %s is Edited as %s " % (
                prev_name, editProjectName.project_name))
        return redirect(url_for('showProjects'))
    else:
        return render_template(
            'editProject.html', project_id=project_id, item=editProjectName
            )


# To Delete a Project
@app.route('/project/<int:project_id>/delete', methods=['GET', 'POST'])
def deleteProject(project_id):
    deleteProjectName = session.query(Project).filter_by(
        project_id=project_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if deleteProjectName.user_id != login_session['user_id']:
        flash("You didn't add this Project, so you can't Delete it. Sorry :-(")
        return redirect(url_for('showProjects'))
    if request.method == 'POST':
        pro_name = deleteProjectName.project_name
        session.delete(deleteProjectName)
        session.commit()
        flash("Project %s is Deleted! " % (pro_name))
        return redirect(url_for('showProjects'))
    else:
        return render_template(
            'deleteProject.html', project_id=project_id,
            item=deleteProjectName)


# To show all the Properties
@app.route('/project/<int:project_id>/')
@app.route('/project/<int:project_id>/menu')
def showProperties(project_id):
    project = session.query(Project).filter_by(project_id=project_id).one()
    creator = getUserInfo(project.user_id)
    properties = session.query(Property).filter_by(
        project_id=project.project_id)
    if (
        'username' not in login_session or
        creator.id != login_session['user_id']
    ):
        return render_template(
            'publicProperties.html', project=project,
            properties=properties, creator=creator)
    else:
        return render_template(
            'showProperties.html', project=project,
            properties=properties, creator=creator)


# To create a new Property Item
@app.route('/project/<int:project_id>/menu/new', methods=['GET', 'POST'])
def newPropertyItem(project_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newProperty = Property(
            property_name=request.form['name'], cost=request.form['cost'],
            property_type=request.form['type'],
            facilities=request.form['facilities'],
            project_id=project_id,
            user_id=login_session['user_id'])
        session.add(newProperty)
        session.commit()
        flash(
            "New Property Item %s is Created! " % (newProperty.property_name))
        return redirect(url_for('showProperties', project_id=project_id))
    else:
        return render_template('newPropertyItem.html', project_id=project_id)


# To Edit a Property Item
@app.route(
    '/project/<int:project_id>/menu/<int:property_id>/edit',
    methods=['GET', 'POST'])
def editPropertyItem(project_id, property_id):
    if 'username' not in login_session:
        return redirect('/login')
    options = [
        "Residential Rental", "Residential Sale",
        "Commercial Rental", "Commercial Sale", "Paying Guest"]
    editedItem = session.query(Property).filter_by(
        property_id=property_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.property_name = request.form['name']
        if request.form['cost']:
            editedItem.cost = request.form['cost']
        if request.form['type']:
            editedItem.property_type = request.form['type']
        if request.form['facilities']:
            editedItem.facilities = request.form['facilities']
        session.add(editedItem)
        session.commit()
        flash("Property Item %s is Edited! " % (editedItem.property_name))
        return redirect(url_for('showProperties', project_id=project_id))
    else:
        return render_template(
            'editPropertyItem.html', project_id=project_id,
            property_id=property_id, item=editedItem,
            options=options)


# To Delete a Property Item
@app.route(
    '/project/<int:project_id>/menu/<int:property_id>/delete',
    methods=['GET', 'POST'])
def deletePropertyItem(project_id, property_id):
    if 'username' not in login_session:
        return redirect('/login')
    deletedItem = session.query(
        Property).filter_by(property_id=property_id).one()
    if request.method == 'POST':
        # To delete the propertyItem
        session.delete(deletedItem)
        session.commit()
        flash("Property Item %s is Deleted! " % (deletedItem.property_name))
        return redirect(url_for('showProperties', project_id=project_id))
    else:
        return render_template(
            'deletePropertyItem.html', project_id=project_id,
            property_id=property_id, item=deletedItem)


# To Show the Projects which has properties of type Residenial Rental
@app.route('/projects/residential_rental')
def showResidentialRentalProjects():
    projects = session.query(
        Project).join(Property).filter(
            Property.property_type == 'Residential Rental').all()
    if 'username' not in login_session:
        return render_template('publicProjects.html', projects=projects)
    else:
        return render_template('showProjects.html', projects=projects)


# To Show the Projects which has properties of type Residenial Sale
@app.route('/projects/residential_sale')
def showResidentialSaleProjects():
    projects = session.query(
        Project).join(Property).filter(
            Property.property_type == 'Residential Sale').all()
    if 'username' not in login_session:
        return render_template('publicProjects.html', projects=projects)
    else:
        return render_template('showProjects.html', projects=projects)


# To Show the Projects which has properties of type Commercial Rental
@app.route('/projects/commercial_rental')
def showCommercialRentalProjects():
    projects = session.query(
        Project).join(Property).filter(
            Property.property_type == 'Commercial Rental').all()
    if 'username' not in login_session:
        return render_template('publicProjects.html', projects=projects)
    else:
        return render_template('showProjects.html', projects=projects)


# To Show the Projects which has properties of type Commercial Sale
@app.route('/projects/commercial_sale')
def showCommercialSaleProjects():
    projects = session.query(
        Project).join(Property).filter(
            Property.property_type == 'Commercial Sale').all()
    if 'username' not in login_session:
        return render_template('publicProjects.html', projects=projects)
    else:
        return render_template('showProjects.html', projects=projects)


# To Show the Projects which has properties of type Paying Guest
@app.route('/projects/paying_guest')
def showPayingGuestProjects():
    projects = session.query(
        Project).join(Property).filter(
            Property.property_type == 'Paying Guest').all()
    if 'username' not in login_session:
        return render_template('publicProjects.html', projects=projects)
    else:
        return render_template('showProjects.html', projects=projects)


# Create anti-forgery state token
# To check request is from the intended user not malicious script
@app.route('/login')
def showLogin():
    """Show the login screen to the user."""
    # state variable with 32 char long with upper case and letters 
    # which will be psaaing on to the client
    # which changes on refresh
    # Later we check for same value with user and login session 
    # when user tries to authenticate
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # state token is send to the client
    return render_template('login.html', STATE=state)


# To login using Facebook OAuth
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # Compare the state sent from client and in login session
    # To protect from Anti Forgery attack
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Exchange short lived token for the Long lived token
    access_token = request.data
    
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = ('https://graph.facebook.com/v2.8/me?'
           'access_token=%s&fields=name,id,email') % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = ('https://graph.facebook.com/v2.8/me/picture?'
           'access_token=%s&redirect=0&height=200&width=200') % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("Now logged in as %s" % login_session['username'])
    return output


# To logout using Facebook OAuth
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['facebook_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Performs app login via Google oauth."""
    # Validate state token sent from client and in login session
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Obtain authorization code(One time code)
    code = request.data

    try:
        # Upgrade the authorization code into get  a credentials object
        # which contains access token for my server
        # below line create Oauth flow object and add my clients secret key info into it
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        # One time code flow my server will be sending of
        oauth_flow.redirect_uri = 'postmessage'
        # initiate step 2 exchange function of flow class to
        # exchange authorization for credentials object from google
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    # Google API server will validate it using below url
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Create a JSON get request containing url and access token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    # Grab the id of the access token in credential object
    gplus_id = credentials.id_token['sub']
    # Compare id in credentials object with id in id from Google API server
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Get client id from client_secrets json file
    CLIENT_ID = json.loads(
        open('client_secrets.json', 'r').read())['web']['client_id']
    APPLICATION_NAME = "Properties Menu Application"

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
     
    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        # Successful authentication
        response = make_response(json.dumps(
            'Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info from google plus api
    # Send message to Google api with my access token 
    # Requesting user info allowed by my token scope and store in data
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    # store user id in login session
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# Take login session as input
def createUser(login_session):
    """Create a new user in the database."""
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    # To get only one result from table user with property email
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# To get user object
def getUserInfo(user_id):
    # Filter User table with property id and get only one result
    user = session.query(User).filter_by(id=user_id).one()
    return user


# To get User id based on email from the database
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke/reject a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    # We have no record of the user
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print result['status']
    
    # if 200 I had successfuly diconnected the user
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Generic  function that supports multiple OAuth providers to disconnect.
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        if login_session['provider'] == 'facebook':
            fbdisconnect()
        flash("You have successfully been logged out.")
        return redirect(url_for('showProjects'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showProjects'))


# JSON ENDPOINT To Show All Projects
@app.route('/projects/JSON')
def showProjectsJSON():
    projects = session.query(Project).all()
    return jsonify(Projects=[project.serialize for project in projects])


# JSON ENDPOINT To Show Specific Project
@app.route('/projects/<int:project_id>/JSON')
def projectItemJSON(project_id):
    projectItem = session.query(Project).filter_by(
        project_id=project_id).one()
    return jsonify(ProjectItem=projectItem.serialize)


# JSON ENDPOINT To Show All Properties of a Project
@app.route('/project/<int:project_id>/menu/JSON')
def showPropertiesJSON(project_id):
    project = session.query(Project).filter_by(project_id=project_id).one()
    properties = session.query(Property).filter_by(
        project_id=project.project_id)
    return jsonify(Properties=[properti.serialize for properti in properties])


# JSON ENDPOINT To Show Specific Property Item
@app.route('/project/<int:project_id>/menu/<int:property_id>/JSON')
def propertyItemJSON(project_id, property_id):
    propertyItem = session.query(Property).filter_by(
        property_id=property_id, project_id=project_id).one()
    return jsonify(PropertyItem=propertyItem.serialize)


# special variable name gets name as main
# if run by Python interpretor
if __name__ == '__main__':
    # Flask will use to create sessions for our users
    app.secret_key = 'super_secret_key'
    # Server will load itself each time code is changed
    app.debug = True
    # To run the local server with application
    app.run(host='0.0.0.0', port=5000)
