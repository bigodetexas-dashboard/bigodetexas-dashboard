import os
from flask import Flask, render_template, session, redirect, url_for
from discord_oauth import init_oauth, login_required

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
init_oauth(app)

# Import all routes from the original dashboard implementation
from web_dashboard import dashboard_bp

# Register the blueprint
app.register_blueprint(dashboard_bp)

if __name__ == '__main__':
    # Run the combined app
    app.run(host='0.0.0.0', port=5000, debug=False)
