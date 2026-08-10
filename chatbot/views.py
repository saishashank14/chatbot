import os
import requests
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

def get_chatbot_response(userinput):
    api_key = "AQ.Ab8RN6LmNXBanXNvGLe_juJ81rPL0vfWNfmF3KQtwMWiA6Elsg"
    URL2 = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": userinput}]
        }],
    }
    
    try:
        response2 = requests.post(URL2, json=payload).json()
        text_output = response2["candidates"][0]["content"]["parts"][0]["text"]
        return text_output
    except Exception as e:
        return f"Error retrieving response: {e}"

@csrf_exempt
def chatbot_view(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                user_message = data.get('message', '').strip()
            except json.JSONDecodeError:
                user_message = ''
            
            if not user_message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            bot_response = get_chatbot_response(user_message)
            return JsonResponse({'response': bot_response})
        else:
            user_message = request.POST.get('message', '').strip()
            if user_message:
                bot_response = get_chatbot_response(user_message)
                chat_history = request.session['chat_history']
                chat_history.append({
                    'question': user_message,
                    'response': bot_response
                })
                request.session['chat_history'] = chat_history
                request.session.modified = True
            return redirect('chatbot')
        
    elif request.method == 'GET':
        if request.GET.get('clear') == 'true':
            request.session['chat_history'] = []
            request.session.modified = True
            return redirect('chatbot')

        user_message = request.GET.get('message', '').strip()
        if user_message:
            bot_response = get_chatbot_response(user_message)
            return JsonResponse({'response': bot_response})
            
        # Return the HTML interface
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CHATBOT</title>
    <!-- Google Font -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-color: #f1f5f9;
            --chat-bg: #ffffff;
            --primary-color: #0f172a;
            --primary-hover: #1e293b;
            --accent-color: #6366f1;
            --text-dark: #0f172a;
            --text-light: #64748b;
            --user-bubble: #6366f1;
            --user-text: #ffffff;
            --bot-bubble: #f8fafc;
            --bot-text: #334155;
            --border-color: #e2e8f0;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-dark);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .chat-container {
            width: 100%;
            max-width: 680px;
            height: 85vh;
            background-color: var(--chat-bg);
            border-radius: 20px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }

        .chat-header {
            padding: 24px;
            background-color: var(--chat-bg);
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
        }

        .chat-header-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .chat-status-dot {
            width: 8px;
            height: 8px;
            background-color: #22c55e;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px #22c55e;
        }

        .chat-title {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: var(--text-dark);
        }

        .clear-btn {
            background-color: #f1f5f9;
            color: #475569;
            border: none;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s ease;
        }

        .clear-btn:hover {
            background-color: #e2e8f0;
            color: var(--text-dark);
        }

        .chat-messages {
            flex-grow: 1;
            padding: 24px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
            background-color: #fafcfd;
            scroll-behavior: smooth;
        }

        .message-group {
            display: flex;
            flex-direction: column;
            max-width: 85%;
        }

        .message-group.user {
            align-self: flex-end;
            align-items: flex-end;
        }

        .message-group.bot {
            align-self: flex-start;
            align-items: flex-start;
        }

        .message-sender {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-light);
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .message-bubble {
            padding: 14px 18px;
            border-radius: 16px;
            font-size: 0.95rem;
            line-height: 1.6;
            word-break: break-word;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02);
        }

        .message-group.user .message-bubble {
            background-color: var(--user-bubble);
            color: var(--user-text);
            border-bottom-right-radius: 4px;
        }

        .message-group.bot .message-bubble {
            background-color: var(--bot-bubble);
            color: var(--bot-text);
            border-bottom-left-radius: 4px;
            border: 1px solid var(--border-color);
        }

        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            text-align: center;
            padding: 40px;
            color: var(--text-light);
            gap: 12px;
        }

        .empty-state-icon {
            font-size: 2.5rem;
            margin-bottom: 8px;
        }

        .empty-state h3 {
            color: var(--text-dark);
            font-size: 1.25rem;
            font-weight: 600;
        }

        .empty-state p {
            font-size: 0.95rem;
            max-width: 320px;
            line-height: 1.5;
        }

        .chat-input-area {
            padding: 20px 24px;
            border-top: 1px solid var(--border-color);
            background-color: var(--chat-bg);
        }

        .chat-form {
            display: flex;
            gap: 12px;
        }

        .chat-input {
            flex-grow: 1;
            padding: 14px 18px;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            font-size: 0.95rem;
            font-family: inherit;
            outline: none;
            background-color: #f8fafc;
            color: var(--text-dark);
            transition: all 0.2s ease;
        }

        .chat-input:focus {
            border-color: var(--accent-color);
            background-color: var(--chat-bg);
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
        }

        .send-btn {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 0 28px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.95rem;
            font-family: inherit;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .send-btn:hover {
            background-color: var(--primary-hover);
        }

        .send-btn:active {
            transform: scale(0.98);
        }

        /* Scrollbar Styling */
        .chat-messages::-webkit-scrollbar {
            width: 6px;
        }
        .chat-messages::-webkit-scrollbar-track {
            background: transparent;
        }
        .chat-messages::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 3px;
        }
        .chat-messages::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
    </style>
</head>
<body>

    <div class="chat-container">
        <!-- Header -->
        <div class="chat-header">
            <div class="chat-header-info">
                <span class="chat-status-dot"></span>
                <span class="chat-title">CHATBOT</span>
            </div>
            {% if chat_history %}
                <a href="?clear=true" class="clear-btn">Clear Chat</a>
            {% endif %}
        </div>

        <!-- Chat messages history -->
        <div class="chat-messages" id="chat-messages">
            {% if chat_history %}
                {% for chat in chat_history %}
                    <!-- User Question -->
                    <div class="message-group user">
                        <span class="message-sender">You</span>
                        <div class="message-bubble">{{ chat.question }}</div>
                    </div>
                    
                    <!-- Bot Response -->
                    <div class="message-group bot">
                        <span class="message-sender">CHATBOT</span>
                        <div class="message-bubble">{{ chat.response|linebreaksbr }}</div>
                    </div>
                {% endfor %}
            {% else %}
                <div class="empty-state">
                    <div class="empty-state-icon">🤖</div>
                    <h3>Say Hello!</h3>
                    <p>Ask a question below, and I'll generate a response for you.</p>
                </div>
            {% endif %}
        </div>

        <!-- Chat input area -->
        <div class="chat-input-area">
            <form action="." method="POST" class="chat-form" id="chat-form">
                {% csrf_token %}
                <input type="text" name="message" id="message-input" class="chat-input" placeholder="Ask CHATBOT a question..." required autocomplete="off">
                <button type="submit" class="send-btn">Send</button>
            </form>
        </div>
    </div>

    <script>
        // Auto-scroll the messages container to the bottom on load
        window.addEventListener('DOMContentLoaded', () => {
            const chatMessages = document.getElementById('chat-messages');
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Auto focus on the input field
            const messageInput = document.getElementById('message-input');
            if (messageInput) {
                messageInput.focus();
            }
        });
    </script>
</body>
</html>"""
        from django.template import Template, RequestContext
        return HttpResponse(Template(html_content).render(RequestContext(request, {
            'chat_history': request.session['chat_history']
        })))

if __name__ == "__main__":
    userinput = input("please enter your question: ")
    print(get_chatbot_response(userinput))

