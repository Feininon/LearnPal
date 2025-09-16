Demo Video: 
https://drive.google.com/file/d/1MnJVXaFqnmbIS6Ppg3uUdpN9M3LG663N/view?usp=sharing 

https://drive.google.com/file/d/12Yt-Jtb580xVkwJ_BHeFj8FFsiSnH0mf/view?usp=sharing


# LearnPal - An Interactive Learning Platform

LearnPal is an interactive learning platform designed to help students enhance their knowledge through quizzes, IQ tests, and personalized chatbot assistance. The platform is built using Flask, MongoDB, and the Groq API for AI-powered question generation and chatbot responses.

## Features

1. **User Authentication**:
   - Users can register and log in with their email and password.
   - Passwords are securely hashed using Bcrypt.
   - Session management ensures users remain logged in for 30 minutes.

2. **Profile Management**:
   - Users can update their profile information, including name, email, phone number, age, and grade.
   - Profile data is stored in MongoDB.

3. **IQ Tests**:
   - Users can take IQ tests with dynamically generated questions.
   - Test results are saved in the database for future reference.

4. **Custom Quizzes**:
   - Users can set up custom quizzes based on their grade, age, and subject of interest.
   - Questions are generated using the Groq API.
   - Users receive explanations for each question after submission.

5. **Chatbot Assistance**:
   - A chatbot powered by the Groq API provides detailed explanations for user queries.
   - Chat history is stored in MongoDB and can be cleared by the user.

6. **Course Recommendations**:
   - Users receive personalized course recommendations based on their age and grade.
   - Courses are fetched from the MongoDB database.

7. **Statistics**:
   - Users can view their quiz and IQ test history.
   - Detailed statistics are displayed on the stats page.

8. **Rate Limiting**:
   - API calls to the chatbot are rate-limited to prevent abuse.

## Technologies Used

- **Flask**: A lightweight web framework for Python.
- **MongoDB**: A NoSQL database for storing user data, test results, and chat history.
- **Bcrypt**: A library for hashing passwords.
- **Groq API**: An AI-powered API for generating questions and chatbot responses.
- **Flask-Limiter**: A library for rate-limiting API requests.
- **Dotenv**: A library for managing environment variables.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/learnpal.git
   cd learnpal
   ```

2. **Set Up Environment Variables**:
   Create a `.env` file in the root directory and add the following variables:
   ```plaintext
   FLASK_SECRET_KEY=your_secret_key
   MONGO_URI=mongodb://localhost:27017/
   GROQ_API_KEY=your_groq_api_key
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```

5. **Access the Application**:
   Open your browser and navigate to `http://localhost:5000`.

## Usage

1. **Registration and Login**:
   - Navigate to the login/register page to create a new account or log in with existing credentials.

2. **Profile Management**:
   - After logging in, users can update their profile information on the profile page.

3. **Taking an IQ Test**:
   - Users can take an IQ test by navigating to the IQ test page. The test consists of dynamically generated questions.

4. **Setting Up a Quiz**:
   - Users can set up a custom quiz by selecting a subject, grade, and number of questions. The quiz questions are generated using the Groq API.

5. **Chatbot Assistance**:
   - Users can interact with the chatbot to get detailed explanations for their queries. The chat history is saved and can be cleared.

6. **Course Recommendations**:
   - Users can view personalized course recommendations based on their age and grade.

7. **Viewing Statistics**:
   - Users can view their quiz and IQ test history on the stats page.

## API Endpoints

- **GET `/`**: Home page.
- **GET `/login_register`**: Login and registration page.
- **POST `/register`**: Register a new user.
- **POST `/login`**: Log in an existing user.
- **GET `/profile`**: User profile page.
- **POST `/update_profile`**: Update user profile information.
- **GET `/logout`**: Log out the user.
- **GET `/iq_test`**: IQ test page.
- **POST `/iq_test`**: Submit IQ test answers.
- **GET `/iq_results`**: View IQ test results.
- **GET `/test_setup`**: Quiz setup page.
- **POST `/test_setup`**: Set up a custom quiz.
- **GET `/questions/<int:q_num>`**: Quiz questions page.
- **POST `/questions/<int:q_num>`**: Submit quiz answers.
- **GET `/answers`**: View quiz results.
- **GET `/stats`**: View user statistics.
- **GET `/chatbot`**: Chatbot page.
- **POST `/get_response`**: Get chatbot response.
- **POST `/clear_chat`**: Clear chat history.
- **GET `/course`**: Course recommendations page.

## Rate Limiting

- The chatbot API is rate-limited to 10 requests per minute to prevent abuse.

## Logging

- The application logs important events such as user registration, login, and errors to help with debugging and monitoring.

## Future Enhancements

- **Multi-language Support**: Add support for multiple languages.
- **Gamification**: Introduce badges and rewards for completing quizzes and tests.
- **Social Features**: Allow users to share their progress and achievements on social media.
- **Mobile App**: Develop a mobile app for easier access.

## Acknowledgments

- **Flask**: For providing a simple and flexible web framework.
- **MongoDB**: For offering a scalable and efficient database solution.
- **Groq API**: For enabling AI-powered question generation and chatbot responses.
- **Bcrypt**: For ensuring secure password hashing.
- **Flask-Limiter**: For implementing rate limiting.

---

## TEAM

-Gokulramanan V, 
 GitHub: [ @Feininon](https://github.com/Feininon)

 -Hanush M, 
 GitHub: [ @Hanush0112](https://github.com/Hanush0112)

-Sai Vignesh Raj M, 
 GitHub: [ @SaiVignesh45](https://github.com/SaiVignesh45)

 -Pragati Sangari S R, 
 GitHub: [ @](https://github.com/)




