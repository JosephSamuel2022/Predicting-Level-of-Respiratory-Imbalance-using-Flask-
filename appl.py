from flask import Flask, session, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import pickle
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import base64
import io
from datetime import date
# plt.use('agg')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'predictingrespimbalance'
model = pickle.load(open('model.pkl', 'rb'))
app.secret_key = 'predictingrespimbalance'

# Connect to MongoDB Atlas
MONGODB_URI = "mongodb+srv://gowtham02:gowtham02@cluster0.u5laxtt.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_URI)
db = client['patients']


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # get the user's data from the signup form
        pid = request.form['pid']
        pfname = request.form['fname']
        plname = request.form['lname']
        dob = request.form['dob']
        dateobj = datetime.strptime(dob, '%Y-%m-%d')
        gender = request.form['gender']
        mno = request.form['mobileno']
        email = request.form['email']
        location = request.form['location']
        password = request.form['password']

        # Insert user's data into database
        db.patient_details.insert_one(
            {"pid": pid, "fname": pfname, "lname": plname, "dob": dateobj, "gender": gender, "mobileno": mno, "email": email, "location": location, "password": password})

        # redirect the user to login page
        return redirect(url_for('home'))

    # if the request method is GET,  render the signup page template
    return render_template('signup.html')

# Define a route for the index page


@app.route('/index')
def index():
    if 'pid' in session:
        return render_template('index.html')
    else:
        return redirect('/login')

# Defining a route for the login page


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Getting the patient data
        pid = request.form['pid']
        password = request.form['password']

        # checking if the patient's credentials are valid
        user = db.patient_details.find_one({'pid': pid, 'password': password})
        if user is not None:
            session['pid'] = pid

            # if credentials are valid, redirecting to index page
            return redirect(url_for('index'))
        else:
            # if credentials are invalid,showing an error message
            # return redirect("/signup")

            flash('Invalid Patient ID or Password. Please Try again.')
    # if the request method is GET, render the login page
    return render_template('login.html')

# For logout


@app.route('/logout')
def logout():
    session.pop('pid', None)
    # redirect to login page
    return redirect(url_for('login'))

# To use the predict button in our web-app


@app.route('/predict', methods=['POST'])
def predict():
    # For rendering results on HTML GUI
    int_features = [float(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    predictiona = model.predict(final_features)

    if request.method == 'POST':
        # get the user's data from the signup form
        tdate = date.today()
        today_str = tdate.strftime('%Y-%m-%d')
        pid = session['pid']
        Dehydration = request.form['Dehydration']
        Medicine_Overdose = request.form['Medicine_Overdose']
        Acidious = request.form['Acidious']
        Cold = request.form['Cold']
        Cough = request.form['Cough']
        Temperature = request.form['Temperature']
        Heart_Rate = request.form['Heart_Rate']
        Pulse = request.form['Pulse']
        BPSYS = request.form['BPSYS']
        BPDIA = request.form['BPDIA']
        Respiratory_Rate = request.form['Respiratory_Rate']
        Oxygen_Saturation = request.form['Oxygen_Saturation']
        PH = request.form['PH']

        prediction = np.array_str(predictiona)
        prediction = prediction[2:-2]
        # Insert user's data into database
        db.medicalhistory.insert_one(
            {"tdate": today_str, "pid": pid, "Dehydration": Dehydration, "Medicine_Overdose": Medicine_Overdose, "Acidious": Acidious, "Cold": Cold, "Cough": Cough, "Temperature": Temperature, "Heart_Rate": Heart_Rate, "Pulse": Pulse, "BPSYS": BPSYS, "BPDIA": BPDIA, "Respiratory_Rate": Respiratory_Rate, "Oxygen_Saturation": Oxygen_Saturation, "PH": PH, "Prediction": prediction})

        # redirect the user to login page
        # return redirect(url_for('home'))

    # if the request method is GET,  render the signup page template


# Generate some random data
    x = []
    # Iterate over the documents returned by the query
    cursor = db.medicalhistory.find({}, {'Temperature': 1, '_id': 0})
    for doc in cursor:
        # Extract the desired attribute and add it to the array
        x.append(doc["Temperature"])

    y = []
    # Iterate over the documents returned by the query
    cursor = db.medicalhistory.find({}, {'Respiratory_Rate': 1, '_id': 0})
    for doc in cursor:
        # Extract the desired attribute and add it to the array
        y.append(doc["Respiratory_Rate"])

    # Set the color for the selected point and the rest of the points
    selected_color = 'r'
    rest_color = 'b'

    # Create a list of colors for each point in the plot
    colors = [selected_color if i == len(
        x)-1 else rest_color for i in range(len(x))]

    # Create the plot
    fig, ax = plt.subplots()
    ax.scatter(x, y, c=colors)

    # Show the plot

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode memory buffer to base64 string and pass to template
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')

    symptoms = ['Dehydration', 'Medicine_Overdose',
                'Acidious', 'Cold', 'Cough']
    c = []
    for i in symptoms:
        co = 0
        cursor = db.medicalhistory.find({i: "1"})
        for doc in cursor:
            co += 1
        c.append(co)
        # Extract the desired attribute and add it to the array

    fig, ax2 = plt.subplots(figsize=(8, 6))
    ax2.bar(symptoms, c)
    plt.xlabel('Symptoms')
    plt.ylabel('Frequency')
    plt.title('Frequency of Symptoms')

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode memory buffer to base64 string and pass to template
    bar_data = base64.b64encode(buffer.read()).decode('utf-8')

    # Iterate over the documents returned by the query

    # line chart

    cursor = db.medicalhistory.find({"pid": pid})
    dates = []
    heart_rates = []
    # Extract the date and heart rate from each document and add them to the arrays
    for doc in cursor:
        dates.append(doc["tdate"])
        heart_rates.append(doc["Heart_Rate"])

    # Create a new figure and axis object
    fig, ax3 = plt.subplots(figsize=(8, 6))

    # Plot the heart rate data as a line chart
    ax3.plot(dates, heart_rates, color='blue', marker='o')

    # Add labels and title to the plot
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Heart Rate')
    ax3.set_title('Patient Heart Rate over Time')

    # Save the plot to a buffer and convert it to a base64 string
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    heart_rate_data = base64.b64encode(buffer.read()).decode('utf-8')

    # word cloud

    diagnosis_list = []
    cursor = db.medicalhistory.find()
    for doc in cursor:
        diagnosis_list.append(doc['Prediction'])

    # Create a dictionary with the frequency of each diagnosis
    freq_dict = {}
    for diagnosis in diagnosis_list:
        freq_dict[diagnosis] = freq_dict.get(diagnosis, 0) + 1

    # Create a WordCloud object with the frequencies of each diagnosis
    wordcloud = WordCloud(
        width=800, height=600, background_color='white').generate_from_frequencies(freq_dict)

    # Create a matplotlib figure and axis for the WordCloud object
    fig, ax4 = plt.subplots(figsize=(8, 6))
    ax4.imshow(wordcloud, interpolation='bilinear')
    ax4.axis('off')

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode memory buffer to base64 string and pass to template
    wordcloud_data = base64.b64encode(buffer.read()).decode('utf-8')

    cursor = db.patient_details.find_one({"pid": pid})
    name = cursor['fname']+" "+cursor['lname']
    return render_template('home.html', wordcloud_data=wordcloud_data, user=name, heart_rate_data=heart_rate_data, bar_data=bar_data, plot_data=plot_data, prediction_text='{}'.format(prediction))


if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
   # app.run(debug=True)
