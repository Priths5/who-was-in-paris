from flask import Flask, render_template, request, redirect, session, url_for, g
from markupsafe import Markup
import markdown
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

is_first_run = True
chat_history = []

# API Setup (Groq and Pinecone)
from groq import Groq
from pinecone import Pinecone

client = Groq(api_key="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")
pc = Pinecone(api_key="7bdbcb82-975c-4396-b472-b65b6ae19bf9")
index = pc.Index("who-was-in-paris")

@app.route('/', methods=['GET', 'POST'])
#@app.route('/', methods=['GET', 'POST'])
def chat_app():
    global is_first_run
    if is_first_run:
        session.pop('chat_messages',None)
        is_first_run = False
        messages=({"role" : "system", "content":"You are a chatbot focused on helping users understand and implement industrial sustainability practices. Your goal is to provide information, guidance, and recommendations on how industries can reduce their environmental impact, improve resource efficiency, and adopt eco-friendly technologies. The user will ask a query, and you will respond to it. If any additional context for the query is found, you will be provided with it."})
        chat_history.append(messages)

    # If the API key is not in session, request it
    if 'api_key' not in session:
        if request.method == 'POST':
            # Store the API key in session and redirect to the chat
            session['api_key'] = request.form['api_key']
            return redirect(url_for('chat_app'))
        return render_template('api_key.html')
    
    chat_messages = session.get('chat_messages',[])
    
    # Initialize chat messages if they don't exist in the session

    if request.method == 'POST':
        # Get the user's message from the form
        user_message = request.form['message']
        chat_messages.append(f"**You**: {user_message}")
        session['chat_messages']=chat_messages
        session.modified = True
        chat_history.append({"role" : "user" , "content" : user_message})

        try:
            # Assuming you're sending the message to Groq and receiving a response
            groq_response = client.chat.completions.create(messages=chat_history, model = "llama3-8b-8192",temperature=1.2)
            session['chat_messages'].append(f"**SusInd.AI**: {groq_response.choices[0].message.content}")
            chat_history.append({"role" : "assistant", "content" : groq_response.choices[0].message.content})
        except Exception as e:
            session['chat_messages'].append(f"Error: {str(e)}")
    rendered_messages = [Markup(markdown.markdown(msg)) for msg in session.get('chat_messages',[])]
    # Render the chat interface with the current chat messages
    return render_template('chat.html', messages=rendered_messages)


if __name__ == "__main__":
    app.run(debug=True)

