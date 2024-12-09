from flask import Flask, render_template, request
import google.generativeai as genai
import logging
import justiceAI_prompt as jp

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)

# User-specific details
ai_name = "Flivo AI"

# Configure API key
api_key = "AIzaSyDgc78PnoUQUau0m4QbAUJtYIv9BKNbHhU"
genai.configure(api_key=api_key)

# Initialize the model outside of the function
model = genai.GenerativeModel('gemini-pro')

# Initialize conversation history log
conversation_log = []


def summarize_response(ai_response):
    """Summarizes AI responses to less than 100 characters."""
    summary_prompt = f"""
    Please summarize the following response in less than 100 characters:
    "{ai_response}"
    """
    try:
        summary_response = model.generate_content(summary_prompt)
        return summary_response.text.strip()
    except Exception as e:
        logging.error(f"Error summarizing response: {e}")
        return "Summary could not be generated."


def save_conversation(question, ai_response):
    """Saves the conversation by summarizing and logging it."""
    summarized_response = summarize_response(ai_response)
    conversation_log.append({'question': question, 'response_summary': summarized_response})


def generate_prompt(Question_input):
    """Generates the prompt for the AI model."""
    summary = "\n".join(
        [f"User asked: '{log['question']}', AI responded: '{log['response_summary']}'"
         for log in conversation_log]
    ) if conversation_log else "No previous conversation history yet."

    # Instruct the model to generate a detailed response
    instruction = "\nPlease provide a detailed and coherent response of approximately 1000 words."

    prompt = jp.prompt + "\nNow the question is: " + Question_input + "\nAnd the previous conversation was this: " + summary + instruction
    return prompt


def generate_ai_response(prompt):
    """Generates a detailed response from the AI."""
    try:
        # Using the default parameters for content generation
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return f"An error occurred: {e}"


@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the index page and handle user input."""
    response = ""
    if request.method == 'POST':
        user_input = request.form['user_input'].strip()

        if user_input.lower() == "exit":
            return render_template('index.html', ai_name=ai_name, response="Goodbye!", conversation_log=conversation_log)

        if not user_input:
            response = "Input cannot be empty. Please try again."
        else:
            question = generate_prompt(user_input)

            if not question.strip():
                response = "Generated prompt is empty. Please check your input."
            else:
                logging.debug(f"Generated Question: {question}")

                response = generate_ai_response(question)
                save_conversation(user_input, response)

    return render_template('index.html', ai_name=ai_name, response=response, conversation_log=conversation_log)


if __name__ == '__main__':
    app.run(debug=True)
