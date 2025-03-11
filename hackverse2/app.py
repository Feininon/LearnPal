from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId
import os
import re
from dotenv import load_dotenv
from groq import Groq
import datetime
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

print("you got mail")
# Initialize Flask app
print("oh no not you")
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key')  # Use environment variable for secret key
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # Session expires after 30 minutes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting for API calls
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Load environment variables
load_dotenv()

# MongoDB setup
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(mongo_uri)
db = client['learnpal']
users_collection = db['users']
tests_collection = db['tests']
iq_tests_collection = db['iq_tests']
chat_collection = db['chats']
courses_collection = db['courses']

# Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Initialize Groq client
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Helper Functions
def clean_question(question):
    """Clean and format generated questions."""
    cleaned_question = " ".join(question.split())
    cleaned_question = re.sub(r'\d\.\s*', '', cleaned_question)
    return cleaned_question

def generate_unique_question(content):
    """Generate a unique question using Groq API."""
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="llama3-8b-8192",
        )
        question = response.choices[0].message.content

        # Add extra comments to the question
        question += "\n\n**Note:** This question is designed to test your understanding of the topic."
        return clean_question(question)
    except Exception as e:
        logger.error(f"Error generating question: {e}")
        return "Failed to generate question. Please try again."

def validate_email(email):
    """Validate email format."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validate_password(password):
    """Validate password strength."""
    return len(password) >= 8

# Routes
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login_register')
def login_register():
    return render_template('login_register.html')

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        age = request.form.get('age')
        grade = request.form.get('grade')

        # Validate inputs
        if not validate_email(email):
            return "Invalid email format", 400
        if not validate_password(password):
            return "Password must be at least 8 characters long", 400
        if password != confirm_password:
            return "Passwords do not match", 400

        # Check if user exists
        if users_collection.find_one({'email': email}):
            return "User already exists", 400

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create user document
        user_data = {
            'email': email,
            'username': username,
            'password': hashed_password,
            'name': '',
            'phone': '',
            'age': age,
            'grade': grade,
            'tests': [],
            'iq_tests': [],
            'chats': []
        }

        # Insert user into MongoDB
        try:
            users_collection.insert_one(user_data)
            return redirect(url_for('login_register'))
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return "An error occurred during registration. Please try again.", 500

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Find user in MongoDB
        user = users_collection.find_one({'email': email})

        # Validate user and password
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['user_name'] = user.get('name', '')
            session['user_email'] = user['email']
            session['user_phone'] = user.get('phone', '')
            session['user_grade'] = user.get('grade', '')
            session['user_age'] = user.get('age', '')

            # Log session data
            logger.info(f"Session data set for user: {session}")

            return redirect(url_for('profile'))
        else:
            return "Invalid email or password", 401

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login_register'))

    user_id = ObjectId(session['user_id'])
    user = users_collection.find_one({'_id': user_id})
    return render_template('profile.html', user=user)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login_register'))

    user_id = ObjectId(session['user_id'])
    update_data = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'grade': request.form.get('grade'),
        'age': request.form.get('age')
    }

    if password := request.form.get('password'):
        update_data['password'] = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        users_collection.update_one({'_id': user_id}, {'$set': update_data})
        session.update({k: v for k, v in update_data.items() if k.startswith('user_')})
        return redirect(url_for('profile'))
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        return "An error occurred. Please try again.", 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_register'))

@app.route('/iq_test', methods=['GET', 'POST'])
def iq_test():
    if request.method == 'POST':
        user_answers = request.form.getlist('answer')
        session['user_answers'] = user_answers

        user_id = ObjectId(session['user_id'])
        iq_test_data = {
            'user_id': user_id,
            'answers': user_answers,
            'timestamp': datetime.datetime.now()
        }
        iq_tests_collection.insert_one(iq_test_data)
        return redirect(url_for('iq_results'))

    iq_questions = [generate_unique_question("Give ONE IQ test question with 4 options (a, b, c, d). Only provide the question and the options without revealing the correct answer.") for _ in range(5)]
    return render_template('iqtest.html', questions=iq_questions)

@app.route('/iq_results', methods=['GET'])
def iq_results():
    user_answers = session.get('user_answers', [])
    return render_template('results.html', user_answers=user_answers)

@app.route('/test_setup', methods=['GET', 'POST'])
def test_setup():
    if 'user_id' not in session:
        return redirect(url_for('login_register'))

    if request.method == 'POST':
        # Fetch user's age and grade from the session or database
        user_id = ObjectId(session['user_id'])
        user = users_collection.find_one({'_id': user_id})
        age = user.get('age', '')
        grade = user.get('grade', '')

        session.update({
            'subject': request.form['subject'],
            'grade': grade,  # Use grade from the database
            'age': age,      # Use age from the database
            'num_questions': int(request.form['num_questions']),
            'questions': [],
            'user_answers': [],
            'explanations': []
        })

        # Log the session data after initialization
        logger.info(f"Session Data After Test Setup: {session}")

        return redirect(url_for('questions', q_num=1))

    return render_template('test_setup.html')

@app.route('/questions/<int:q_num>', methods=['GET', 'POST'])
def questions(q_num):
    if 'user_id' not in session:
        return redirect(url_for('login_register'))

    if request.method == 'POST':
        # Get the selected answer from the form
        selected_answer = request.form.get('answer')
        if not selected_answer:
            return "Please select an answer.", 400

        # Append the selected answer to the session
        session['user_answers'].append(selected_answer)

        # Generate an explanation for the current question
        current_question = session['questions'][-1]
        explanation = generate_unique_question(
            f"Explain why the correct answer for the following question is what it is: {current_question}"
        )
        session['explanations'].append(explanation)

        # Log the session data after updating
        logger.info(f"Session Data After Submission: {session}")

        # Ensure the session is saved
        session.modified = True

        if q_num < session['num_questions']:
            return redirect(url_for('questions', q_num=q_num + 1))
        else:
            # Save the test results to the database
            test_data = {
                'user_id': ObjectId(session['user_id']),
                'subject': session['subject'],
                'grade': session['grade'],
                'age': session['age'],
                'questions': session['questions'],
                'user_answers': session['user_answers'],
                'explanations': session['explanations'],
                'timestamp': datetime.datetime.now()
            }

            try:
                tests_collection.insert_one(test_data)
                logger.info("Test data inserted successfully.")
            except Exception as e:
                logger.error(f"Error inserting test data: {e}")
                return "An error occurred while saving the test results. Please try again.", 500

            return redirect(url_for('answers'))

    # Generate a new question for the current question number
    subject = session['subject']
    grade = session['grade']
    questions = session.get('questions', [])

    while True:
        new_question = generate_unique_question(
            f"Give ONE MCQ question with 4 options (a, b, c, d) on {subject} for grade {grade}. Only provide the question and the options without revealing the correct answer."
        )
        if new_question not in questions:
            questions.append(new_question)
            session['questions'] = questions
            break

    return render_template('test.html', question=new_question, q_num=q_num)

@app.route('/answers', methods=['GET'])
def answers():
    if 'user_id' not in session:
        return redirect(url_for('login_register'))

    # Fetch the questions, user answers, and explanations from the session
    questions = session.get('questions', [])
    user_answers = session.get('user_answers', [])
    explanations = session.get('explanations', [])

    # Log the data being passed to the template
    logger.info(f"Questions: {questions}")
    logger.info(f"User Answers: {user_answers}")
    logger.info(f"Explanations: {explanations}")

    return render_template('result.html', questions=questions, user_answers=user_answers, explanations=explanations)

@app.route('/stats')
def stats():
    if 'user_id' not in session:
        return redirect(url_for('login_register'))

    user_id = ObjectId(session['user_id'])
    user_tests = list(tests_collection.find({'user_id': user_id}))
    user_iq_tests = list(iq_tests_collection.find({'user_id': user_id}))
    return render_template('stats.html', user_tests=user_tests, user_iq_tests=user_iq_tests)

@app.route('/chatbot')
def chatbot():
    if 'user_id' not in session:
        return redirect(url_for('login_register'))

    user_id = ObjectId(session['user_id'])
    chat_history = list(chat_collection.find({'user_id': user_id}).sort('timestamp', 1))
    return render_template('chatbot.html', messages=chat_history)

@app.route('/get_response', methods=['POST'])
@limiter.limit("10 per minute")
def get_response():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    user_input = request.json['input']
    user_id = ObjectId(session['user_id'])
    user = users_collection.find_one({'_id': user_id})
    age = user.get('age', '')
    grade = user.get('grade', '')

    # Customize the prompt based on the user's age and grade
    prompt = (
        f"The user is {age} years old and in grade {grade}. "
        f"Provide a detailed explanation for the following question in a way that is easy for them to understand: {user_input}"
    )

    try:
        groq_response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        bot_response = groq_response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating chatbot response: {e}")
        bot_response = "Sorry, I couldn't generate a response. Please try again later."

    # Store the chat history
    user_message = {
        'user_id': user_id,
        'sender': 'user',
        'text': user_input,
        'timestamp': datetime.datetime.now()
    }
    bot_message = {
        'user_id': user_id,
        'sender': 'bot',
        'text': bot_response,
        'timestamp': datetime.datetime.now()
    }
    try:
        chat_collection.insert_many([user_message, bot_message])
        logger.info("Chat history updated successfully.")
    except Exception as e:
        logger.error(f"Error updating chat history: {e}")

    return jsonify({'response': bot_response})

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    user_id = ObjectId(session['user_id'])
    chat_collection.delete_many({'user_id': user_id})  # Delete all chat messages for the user
    return jsonify({'message': 'Chat history cleared successfully'})

@app.route('/course')
def course():
    if 'user_id' not in session:
        return redirect(url_for('login_register'))

    user_id = ObjectId(session['user_id'])
    user = users_collection.find_one({'_id': user_id})
    age = user.get('age', '')
    grade = user.get('grade', '')

    # Validate age and grade
    if not age or not grade:
        return render_template('course.html', courses=[], user=user, error="Please update your profile with age and grade to view recommended courses.")

    try:
        age = int(age)  # Convert age to integer
    except (ValueError, TypeError):
        return render_template('course.html', courses=[], user=user, error="Invalid age in profile. Please update your profile.")

    # Fetch courses based on the user's grade and age
    courses = list(courses_collection.find({
        'grade': grade,
        'age_range': {'$lte': age}  # Assuming age_range is a field in the course document
    }))

    return render_template('course.html', courses=courses, user=user)

# Main app runner
if __name__ == '__main__':
    app.run(debug=True)
