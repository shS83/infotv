from FlaskTV import app

if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', static_files={'/static': './FlaskTV/static'})    # public
    app.run(debug=True, static_files={'/static': './FlaskTV/static'})     # localhost

