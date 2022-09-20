import sys
sys.path.insert(0, "flaskr")  # adding the parent directory to the path to import app

from flaskr.app import app

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(debug=False)

