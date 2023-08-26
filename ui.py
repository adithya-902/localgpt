import flask
from flask import Flask
from constants import CHROMA_SETTINGS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import LlamaCpp
from langchain.chains import RetrievalQA
import argparse
import sys
from dotenv import load_dotenv

from multiprocessing import Pool
from tqdm import tqdm
import os
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
import glob
from typing import List

# Initialize Flask app
app = Flask(__name__)



@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>

<head>
  <meta charset="UTF-8">
  <h1>Chatbot</h1>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <link rel="stylesheet" href="{{ url_for('static', filename='styles/style.css') }}">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
  <style>
    body {
      background-image: url('https://wallpapers.com/images/hd/light-color-background-vmkuihk29pi1xq65.jpg');
    }
  </style>
</head>

<body>
  <!-- partial:index.partial.html -->
  <section class="msger">
    <header class="msger-header">
      <div class="msger-header-title">
        <i class="fas fa-bug"></i> Chatbot <i class="fas fa-bug"></i>
      </div>
    </header>

    <main class="msger-chat">
      <div class="msg left-msg">
        <div class="msg-img" style="background-image: url('https://pbs.twimg.com/media/E2z6WrjWUAEconS.png')"></div>

        <div class="msg-bubble">
          <div class="msg-info">
            <div class="msg-info-name">Chatbot</div>
            <div class="msg-info-time">12:45</div>
          </div>

          <div class="msg-text">
            Hi, welcome to ChatBot! Go ahead and send me a message. 🕺
          </div>
        </div>
      </div>

    </main>

    <form class="msger-inputarea" method="POST">
      <input type="text" class="msger-input" id="textInput" placeholder="Enter your message...">
      <button type="submit" class="msger-send-btn">Send</button>
    </form>
  </section>
  <!-- partial -->
  <script>
    const msgerForm = document.querySelector(".msger-inputarea");
    const msgerInput = document.querySelector(".msger-input");
    const msgerChat = document.querySelector(".msger-chat");

    // Icons
    const BOT_IMG = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTuNkig3aFVhlPkAeUZILBQEzYjoL5AO1u7ng&usqp=CAU";
    const PERSON_IMG = "https://image.flaticon.com/icons/svg/145/145867.svg";
    const BOT_NAME = "ChatBot";
    const PERSON_NAME = "You";

    msgerForm.addEventListener("submit", event => {
      event.preventDefault();

      const msgText = msgerInput.value;
      if (!msgText) return;

      appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText);
      msgerInput.value = "";
      botResponse(msgText);
    });

    function appendMessage(name, img, side, text) {
      const msgHTML = `
        <div class="msg ${side}-msg">
          <div class="msg-img" style="background-image: url('${img}')"></div>
          <div class="msg-bubble">
            <div class="msg-info">
              <div class="msg-info-name">${name}</div>
              <div class="msg-info-time">${formatDate(new Date())}</div>
            </div>
            <div class="msg-text">${text}</div>
          </div>
        </div>
      `;

      msgerChat.insertAdjacentHTML("beforeend", msgHTML);
      msgerChat.scrollTop += 500;
    }

    function botResponse(rawText) {
      // Bot Response
      $.get("/get", { msg: rawText }).done(function (data) {
        const msgText = data;
        appendMessage(BOT_NAME, BOT_IMG, "left", msgText);
      });
    }

    function formatDate(date) {
      const h = "0" + date.getHours();
      const m = "0" + date.getMinutes();

      return `${h.slice(-2)}:${m.slice(-2)}`;
    }
  </script>
</body>

</html>


"""

@app.route("/get")
def get_bot_response():
    """user_input = flask.request.args.get("msg")

    # Generate response from the model
    response = llm(user_input)
    response_text = response['choices'][0]['text']
    print(response_text)
    return str(response_text)"""

    def parse_arguments():
        parser = argparse.ArgumentParser(description='privateGPT: Ask questions to your documents without an internet connection, using the power of LLMs.')
        parser.add_argument("--hide-source", "-S", action='store_true',
                            help='Use this flag to disable printing of source documents used for answers.')

        parser.add_argument("--mute-stream", "-M",
                            action='store_true',
                            help='Use this flag to disable the streaming StdOut callback for LLMs.')

        return parser.parse_args()

    

    
    load_dotenv()

    embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME")
    persist_directory = os.environ.get('PERSIST_DIRECTORY')

    model_type = os.environ.get('MODEL_TYPE')
    model_path = os.environ.get('MODEL_PATH')
    model_n_ctx = os.environ.get('MODEL_N_CTX')

    print("Loading model...")
    args = parse_arguments()

     # Parse the command line arguments
    args = parse_arguments()
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS)
    retriever = db.as_retriever()
    # activate/deactivate the streaming StdOut callback for LLMs
    callbacks = [] if args.mute_stream else [StreamingStdOutCallbackHandler()]
    # Prepare the LLM

    llm = LlamaCpp(model_path=model_path, n_ctx=model_n_ctx, callbacks=callbacks, verbose=False)
    
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents= not args.hide_source)
    # Interactive questions and answers
    
    query = flask.request.args.get("msg")
    print(query)
    if query == "exit":
        sys.exit(0)

    # Get the answer from the chain
    res = qa(query)
    answer = res['result']
    return answer


# Run the app
if __name__ == "__main__":
    app.run(port=7070)