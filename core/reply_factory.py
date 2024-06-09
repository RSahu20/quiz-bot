
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")

    # Check if a question is currently active
    if current_question_id is None:
        # If not, send the welcome message
        bot_responses.append(BOT_WELCOME_MESSAGE)
        # Set the current_question_id to start from the first question
        session["current_question_id"] = 0
        session.save()
        # Fetch the first question and its options
        next_question, next_question_id = get_next_question(0)
        question_data = PYTHON_QUESTION_LIST[0]
        options = "\n".join([f"{i+1}. {option}" for i, option in enumerate(question_data['options'])])
        bot_responses.append(f"{next_question}\nOptions:\n{options}")
        return bot_responses

    # If the user inputs "/reset", reset the session
    if message.strip() == '/reset':
        session["current_question_id"] = None
        session['answers'] = {}
        session.save()
        bot_responses.append("Quiz has been reset. Ask me anything to start again.")
        return bot_responses

    # Record the user's answer for the current question
    success, error = record_current_answer(message, current_question_id, session)
    if not success:
        return [error]

    # Get the next question
    next_question, next_question_id = get_next_question(current_question_id)
    
    # If there is a next question, add it to the responses along with its options
    if next_question:
        question_data = PYTHON_QUESTION_LIST[next_question_id]
        options = "\n".join([f"{i+1}. {option}" for i, option in enumerate(question_data['options'])])
        bot_responses.append(f"{next_question}\nOptions:\n{options}")
    else:
        # If there are no more questions, generate the final response
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    if current_question_id is None:
        return False, "No question is currently active."

    question = PYTHON_QUESTION_LIST[current_question_id]

    # Check if the provided answer is one of the options for the current question
    if answer not in question['options']:
        return False, "Invalid answer option selected."

    # Store the user's answer in the session
    session['answers'] = session.get('answers', {})
    session['answers'][current_question_id] = answer
    session.save()
    return True, ""

def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    next_question_id = current_question_id + 1
    if next_question_id < len(PYTHON_QUESTION_LIST):
        return PYTHON_QUESTION_LIST[next_question_id]['question_text'], next_question_id
    else:
        return None, -1



def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    answers = session.get('answers', {})
    correct_answers = 0

    for i, question in enumerate(PYTHON_QUESTION_LIST):
        if str(i) in answers and answers[str(i)] == question['answer']:
            correct_answers += 1

    total_questions = len(PYTHON_QUESTION_LIST)
    score_percentage = (correct_answers / total_questions) * 100

    return f"You scored {correct_answers}/{total_questions} ({score_percentage:.2f}%) in the Python quiz."

