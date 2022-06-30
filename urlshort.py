from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, jsonify, Blueprint
import json
import os.path
from werkzeug.utils import secure_filename  # Checks uploaded files to make sure they're safe
import tkinter
from tkinter import messagebox

bp = Blueprint('urlshort', __name__)

# At some point you'll need a file that creates a flask app, which we'll do here.
# This is commented out in favor of utilizing the __init__.py file, and applying "blueprinting" to the project
"""
app = Flask(__name__)
# Secret key allows messages to be flashed to the user without concern for outside influence.
app.secret_key = 'abcdefg'
"""

# The simple slash means that we're setting this route to respond to someone accessing the home URL
@bp.route('/')
def home():
    # You can return a simple string like the line below.
    # return "Hello Flask"

    # Of you can return a more intelligent file such as this line
    return render_template('home.html', codes=session.keys())  # the name variable is declared and sent as a variable sent to home.html


# Changing the rout parameter changes what URL it responds to. In this case, an about page. (Commented out because
# we don't need an about page... but this is an example.
# """
@bp.route('/about')
def about():
    return "This is a URL shortener"
# """


# Create a your URL function to act as a results page for the user.
# We're allowing get and post as methods/params so that flask will allow the use of both.
@bp.route('/your-url', methods=['GET', 'POST'])
def your_url():
    if request.method == 'POST':
        # Create dict to save information that the user has passed in. Code that the user has passed will be the key,
        # the URL that that code will get to will be the value.
        urls = {}

        # if the JSON file already exists, load all of the JSON data into the dictionary
        if os.path.exists('../urls.json'):
            with open('../urls.json') as urls_file:
                urls = json.load(urls_file)

        # If the shortened "code" input by the user has already been used, flash a warning message.
        if request.form['code'] in urls.keys():
            flash('That short name has already been taken. Please select another name.')
            return redirect(url_for('urlshort.home'))

        # Check if file upload or url
        # if the input is a url
        if 'url' in request.form.keys():
            urls[request.form['code']] = {'url': request.form['url']}
        # if the input is a file
        else:
            f = request.files["file"]
            full_name = request.form['code'] + secure_filename(f.filename)
            f.save("/Users/cjdel/OneDrive/Desktop/url-shortener/static/urlshort/user_files/" + full_name)
            urls[request.form['code']] = {'file': full_name}

        # Add the user's input into a JSON storage file
        # urls[request.form['code']] = {'url':request.form['url']}  # Adding items from the HTML via request.form
        with open('../urls.json', 'w') as urls_file:
            json.dump(urls, urls_file)
            # Save inputs as cookies
            session[request.form['code']] = True
        return render_template('your_url.html', code=request.form['code'])  # When using a post type, we use request.form rather than args
    else:
        # return 'This is not valid' Rather than giving a message when someone access the page incorrectly, render the home page.
        return redirect(url_for('urlshort.home'))


# Redirect to a specific URL based on user input and file type.
@bp.route('/<string:code>')
def redirect_to_url(code):
    if os.path.exists('../urls.json'):
        with open('../urls.json') as urls_file:
            urls = json.load(urls_file)
            if code in urls.keys():
                if 'url' in urls[code].keys():
                    return redirect(urls[code]['url'])
                else:
                    return redirect(url_for('static', filename='user_files/' + urls[code]['file']))

    return abort(404)


# Create route for custom error pages.
@bp.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


# Add a JSON API to the page.
@bp.route('/api')
def session_api():
    return jsonify(list(session.keys()))
