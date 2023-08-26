from llama_cpp import Llama


llm = Llama(model_path="C:\\Users\\Adithya\\Documents\\Coding\\AI\\privateGPT\\models\\ggml-vic13b-q5_1.bin")

user_input = input("Enter some question:")
response = llm(user_input)
response_text = response['choices'][0]['text']
print(response_text)
#return str(response_text)