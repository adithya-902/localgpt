from fastapi import FastAPI, Request
from constants import CHROMA_SETTINGS
from fastapi.responses import HTMLResponse
from langchain.llms import LlamaCpp
from langchain.chains import RetrievalQA
import argparse
from dotenv import load_dotenv
import os
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.vectorstores import Chroma





app = FastAPI()



@app.get("/")
async def home(request: Request):
    content = """
   <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />

    <style>
      * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
      }

      body {
        background-color: rgb(85, 86, 88);
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
      }

      .nav {
        width: 100%;
        height: 70px;
        background-color: rgb(50, 50, 49);
        color: rgb(101, 101, 101);
        display: flex;
        justify-content: center;
        align-items: center;
      }

      .responses {
        z-index: 0;
        height: 100vh;
        align-items: flex-start;
        width: 100%;
        display: flex;
        flex-direction: column;
      }

      .main-body {
        display: flex;
        justify-content: center;
        z-index: -1;
        align-items: flex-start;
        width: 100%;
        height: 83vh;
        background-color: rgb(87, 87, 87);
        overflow-y: scroll;
      }

      .query {
        display: inline;
        
        background-color: rgb(50, 50, 49);
        width: 100%;
        height: 60px;
      }

      #query-text {
        width: 85%;
        color: aliceblue;
        height: 40px;
        border-radius: 20px;
        background-color: rgb(35, 34, 34);
        border: 1px solid black;
        margin-left: 40px;
        margin-right: 15px;
        padding: 20px;
        min-width: auto;  
      }

      #query-text:focus {
        outline: none;
      }

      .usr {
        width: 100%;
        height: auto;
        display: flex;
        align-items: center;
        justify-content: right;
      }

      .bot {
        width: 100%;
        height: auto;
        display: flex;
        align-items: center;
        justify-content: left;
      }

      .time {
        font-size: 10px;
      }

      p {
        font-family: Verdana, Geneva, Tahoma, sans-serif;
      }

      .bubble-usr {
        width: auto;
        color: #fff;
        max-width: 40%;
        height: auto;
        background-color: #d80286;
        overflow-y: hidden;
        padding: 10px;
        border-radius: 20px 20px 0px 20px;
        margin-right: 20px;
        margin-top: 5px;
        margin-bottom: 5px;
      }

      .bubble-bot {
        width: auto;
        max-width: 40%;
        height: auto;
        background-color: rgb(50, 50, 49);
        overflow-y: hidden;
        padding: 10px;
        color: #fff;
        border-radius: 20px 20px 20px 0px;
        margin: 20px;
      }

      span {
        background-color: #d80286;
        border-radius: 5px;
        color: #fff;
        padding: 2px;
      }

      .submit {
        color: #fff;
        border: 2px solid rgb(216, 2, 134);
        border-radius: 10px;
        padding: 18px 36px;
        background-color: rgb(50, 50, 49);
        display: inline-block;
        font-family: "Lucida Console", Monaco, monospace;
        font-size: 14px;
        letter-spacing: 1px;
        cursor: pointer;
        text-align: center;
        margin-left: 5px;
        box-shadow: inset 0 0 0 0 #d80286;
        -webkit-transition: ease-out 0.4s;
        -moz-transition: ease-out 0.4s;
        transition: ease-out 0.4s;
        width: 10%;
        min-width: auto;
      }
      .submit:hover {
        box-shadow: inset 0 0 0 50px #d80286;
      }
      .submit:active {
        opacity: 0.3;
      }
    </style>

    <title></title>
  </head>
  <body>
    <div class="nav">
      <h1 class="title"><span>Chat</span>Bot</h1>
    </div>
    <div class="main-body">
      <div class="responses" id="responses">
        <div class="bot">
          <div class="bubble-bot">
            <br class="bot-p">Ask me anything :)</p>
          </div>
        </div>
      </div>
    </div>
    <div class="query">
      <form  class="chat-form">
        <input
          type="text"
          name="query-text"
          id="query-text"
          placeholder="Enter message..."
        />
        <button type="submit" class="submit" name="submit">
          Send
        </button>
      </form>
    </div>
  </body>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js">
      const msgerForm = document.querySelector(".chat-form");
      const msgerInput = document.querySelector("#query-text");
      const msgerChat = document.querySelector(".responses");
    

    function chatting() {
      forms.addEventListener("submit",(e)=>{
        e.preventDefault();
        const msgText = msgerInput.value;
        if (!msgText) return;

        appendMessage("usr", msgText);
        msgerInput.value = "";
        botResponse(msgText);
      })
    }

    function appendMessage(side, text) {
      const currentTime = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
        const msgHTML = `
        <div class="${side}">
          <div class="bubble-${side}" >
            <p>${text} "</br></br> <span class = 'time'>${currentTime}</span>"</p>
          </div>
        </div>
      `;

        msgerChat.insertAdjacentHTML("beforeend", msgHTML);
        msgerChat.scrollTop += 500;
      }

    function botResponse(rawText) {
        // Bot Response
        $.get("/get", { msg: rawText }).done(function (data) {
          $.get("/get", { msg: rawText }).done(function (data) {
          const msgText = data.response;
          appendMessage("bot", msgText);
        });
        });
      }

    function formatDate(date) {
      const h = "0" + date.getHours();
      const m = "0" + date.getMinutes();

      return `${h.slice(-2)}:${m.slice(-2)}`;
    }
  </script>
</html>


    """

    return HTMLResponse(content=content)

    


@app.get("/get")
async def get_bot_response(request: Request, msg: str):
    def parse_arguments():
        parser = argparse.ArgumentParser(
            description='privateGPT: Ask questions to your documents without an internet connection, using the power of LLMs.')
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

    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS)
    retriever = db.as_retriever()
    callbacks = [] if args.mute_stream else [StreamingStdOutCallbackHandler()]
    llm = LlamaCpp(model_path=model_path, n_ctx=model_n_ctx, callbacks=callbacks, verbose=False)
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=not args.hide_source)

    query = msg
    print(query)

    res = qa(query)
    answer = res['result']
    return answer


if __name__ == "__main__":
    
    import uvicorn

    uvicorn.run(app, port=7070)
