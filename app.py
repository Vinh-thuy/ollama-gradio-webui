import gradio as gr
import ollama
import json
import base64
import copy

# Récupère la liste des modèles Ollama disponibles
model_list = ollama.list()
model_names = [model['model'] for model in model_list['models']]
PROMPT_LIST = []
VL_CHAT_LIST = []

# Charge les invites à partir du fichier prompt.json
with open("prompt.json", "r", encoding="utf-8") as f:
    PROMPT_DICT = json.load(f)
    for key in PROMPT_DICT:
        PROMPT_LIST.append(key)

def init():
    """
    Initialise la liste de conversation en la vidant.
    
    Cette fonction est utilisée pour réinitialiser l'état de la conversation.
    """
    VL_CHAT_LIST.clear()

def contains_chinese(string):
    """
    Vérifie si une chaîne de caractères contient des caractères chinois.
    
    Args:
        string (str): La chaîne de caractères à vérifier.
    
    Returns:
        bool: True si la chaîne contient des caractères chinois, False sinon.
    """
    for char in string:
        if '\u4e00' <= char <= '\u9fa5':
            return True
    return False

def ollama_chat(message, history, model_name, history_flag):
    """
    Génère une réponse de chat en utilisant un modèle Ollama.
    
    Args:
        message (str): Le message de l'utilisateur.
        history (list): Historique précédent de la conversation.
        model_name (str): Nom du modèle Ollama à utiliser.
        history_flag (bool): Indique s'il faut inclure l'historique précédent.
    
    Yields:
        str: Réponse partielle générée par le modèle.
    """
    messages = []
    chat_message = {
        'role': 'user', 
        'content': message
    }
    
    if history_flag and len(history) > 0:
        for element in history:  
            history_user_message = {
                'role': 'user', 
                'content': element[0]
            }
            history_assistant_message = {
                'role': 'assistant', 
                'content': element[1]
            }
            messages.append(history_user_message)
            messages.append(history_assistant_message)   
    
    messages.append(chat_message)
    stream = ollama.chat(
        model=model_name,
        messages=messages,
        stream=True
    )
    
    partial_message = ""
    for chunk in stream:
        if len(chunk['message']['content']) != 0:
            partial_message = partial_message + chunk['message']['content']
            yield partial_message

def ollama_prompt(message, history, model_name, prompt_info):
    """
    Génère une réponse basée sur un prompt prédéfini.
    
    Args:
        message (str): Le message de l'utilisateur.
        history (list): Historique précédent de la conversation.
        model_name (str): Nom du modèle Ollama à utiliser.
        prompt_info (str): Clé du prompt prédéfini à utiliser.
    
    Yields:
        str: Réponse partielle générée par le modèle.
    """
    messages = []
    system_message = {
        'role': 'system', 
        'content': PROMPT_DICT[prompt_info]
    }
    user_message = {
        'role': 'user', 
        'content': message
    }
    messages.append(system_message)
    messages.append(user_message)
    
    stream = ollama.chat(
        model=model_name,
        messages=messages,       
        stream=True
    )
    
    partial_message = ""
    for chunk in stream:
        if len(chunk['message']['content']) != 0:
            partial_message = partial_message + chunk['message']['content']
            yield partial_message

def vl_image_upload(image_path, chat_history):
    """
    Télécharge une image dans l'historique de conversation.
    
    Args:
        image_path (str): Chemin vers l'image téléchargée.
        chat_history (list): Historique actuel de la conversation.
    
    Returns:
        tuple: None et l'historique de conversation mis à jour.
    """
    message = {
        "type": "image",
        "content": image_path
    }
    chat_history.append(((image_path,), None))
    VL_CHAT_LIST.append(message)
    return None, chat_history

def vl_submit_message(message, chat_history):
    """
    Soumet un message de l'utilisateur à l'historique de conversation.
    
    Args:
        message (str): Message de l'utilisateur.
        chat_history (list): Historique actuel de la conversation.
    
    Returns:
        tuple: Message vide et historique de conversation mis à jour.
    """
    message_obj = {
        "type": "user",
        "content": message
    }
    chat_history.append((message, None))
    VL_CHAT_LIST.append(message_obj)
    return "", chat_history

def vl_retry(chat_history):
    """
    Annule la dernière réponse de l'assistant si possible.
    
    Args:
        chat_history (list): Historique actuel de la conversation.
    
    Returns:
        list: Historique de conversation mis à jour.
    """
    if len(VL_CHAT_LIST) > 1:
        if VL_CHAT_LIST[len(VL_CHAT_LIST)-1]['type'] == "assistant":
            VL_CHAT_LIST.pop()
            chat_history.pop()
    return chat_history

def vl_undo(chat_history):
    """
    Annule le dernier message ou réponse de la conversation.
    
    Args:
        chat_history (list): Historique actuel de la conversation.
    
    Returns:
        tuple: Message annulé et historique de conversation mis à jour.
    """
    message = ""
    chat_list = copy.deepcopy(VL_CHAT_LIST)
    if len(chat_list) > 1:
        if chat_list[len(chat_list)-1]['type'] == "assistant":
            message = chat_list[len(chat_list)-2]['content']
            VL_CHAT_LIST.pop()
            VL_CHAT_LIST.pop()
            chat_history.pop()
            chat_history.pop()
        elif chat_list[len(chat_list)-1]['type'] == "user":
            message = chat_list[len(chat_list)-1]['content']
            VL_CHAT_LIST.pop()
            chat_history.pop()
    return message, chat_history

def vl_clear():
    """
    Efface complètement l'historique de conversation.
    
    Returns:
        tuple: None, chaîne vide et liste vide.
    """
    VL_CHAT_LIST.clear()
    return None, "", []

def vl_submit(history_flag, chinese_flag, chat_history):
    """
    Soumet la conversation pour obtenir une réponse de l'assistant.
    
    Args:
        history_flag (bool): Indique s'il faut inclure l'historique.
        chinese_flag (bool): Indique si la réponse doit être en chinois.
        chat_history (list): Historique actuel de la conversation.
    
    Returns:
        list: Historique de conversation mis à jour avec la réponse.
    """
    if len(VL_CHAT_LIST) > 1:
        messages = get_vl_message(history_flag, chinese_flag)
        response = ollama.chat(
            model="llava:7b-v1.6",
            messages=messages
        )
        result = response["message"]["content"]
        output = {
            "type": "assistant",
            "content": result
        }
        chat_history.append((None, result))
        VL_CHAT_LIST.append(output)
    else:
        gr.Warning('Erreur lors de la récupération du résultat')
    return chat_history

def get_vl_message(history_flag, chinese_flag):
    """
    Prépare les messages pour la conversation visuelle.
    
    Args:
        history_flag (bool): Indique s'il faut inclure l'historique complet.
        chinese_flag (bool): Indique si un message système en chinois doit être ajouté.
    
    Returns:
        list: Liste de messages formatés pour Ollama.
    """
    messages = []
    if history_flag:
        i = 0
        while i < len(VL_CHAT_LIST):
            if VL_CHAT_LIST[i]['type'] == "image" and VL_CHAT_LIST[i+1]['type'] == "user":
                image_path = VL_CHAT_LIST[i]["content"]
                with open(image_path, "rb") as image_file:
                    image_data = image_file.read()
                base64_string = base64.b64encode(image_data).decode("utf-8")
                content = VL_CHAT_LIST[i+1]["content"]
                chat_message = {
                    'role': 'user', 
                    'content': content,
                    'images': [base64_string]
                }
                messages.append(chat_message)
                i += 2
            elif VL_CHAT_LIST[i]['type'] == "assistant":
                assistant_message = {
                    "role": "assistant",
                    "content": VL_CHAT_LIST[i]['content']
                }
                messages.append(assistant_message)
                i += 1
            elif VL_CHAT_LIST[i]['type'] == "user":
                user_message = {
                    "role": "user",
                    "content": VL_CHAT_LIST[i]['content']
                }
                messages.append(user_message)
                i += 1
            else:
                i += 1
    else:
        if VL_CHAT_LIST[0]['type'] == "image" and VL_CHAT_LIST[-1]['type'] == "user":
            image_path = VL_CHAT_LIST[0]["content"]
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            base64_string = base64.b64encode(image_data).decode("utf-8")
            content = VL_CHAT_LIST[-1]["content"]
            chat_message = {
                'role': 'user', 
                'content': content,
                'images': [base64_string]
            }
            messages.append(chat_message)
    
    if chinese_flag:
        system_message = {
            'role': 'system', 
            'content': 'Vous êtes un Assistant Utile. Veuillez répondre à la question en français.'
        }
        messages.insert(0, system_message)
    
    return messages

with gr.Blocks(title="Ollama WebUI", fill_height=True) as demo:
    with gr.Tab("Chat"):
        with gr.Row():
            with gr.Column(scale=1):
                model_info = gr.Dropdown(model_names, value="", allow_custom_value=True, label="Sélection du modèle")
                history_flag = gr.Checkbox(label="Activer le contexte")
            with gr.Column(scale=4):
                chat_bot = gr.Chatbot(height=600, render=False)
                text_box = gr.Textbox(scale=4, render=False)
                gr.ChatInterface(
                    fn=ollama_chat,
                    chatbot=chat_bot,
                    textbox=text_box,
                    additional_inputs=[model_info, history_flag],
                    submit_btn="Soumettre",
                    retry_btn=" Réessayer",
                    undo_btn=" Annuler",
                    clear_btn=" Effacer",
                    fill_height=True
                )
    with gr.Tab("Assistant"):
        with gr.Row():
            with gr.Column(scale=1):
                prompt_model_info = gr.Dropdown(model_names, value="", allow_custom_value=True, label="Sélection du modèle")
                prompt_info = gr.Dropdown(choices=PROMPT_LIST, value=PROMPT_LIST[0], label="Sélection de l'assistant", interactive=True)
            with gr.Column(scale=4):
                prompt_chat_bot = gr.Chatbot(height=600, render=False)
                prompt_text_box = gr.Textbox(scale=4, render=False)
                gr.ChatInterface(
                    fn=ollama_prompt,
                    chatbot=prompt_chat_bot,
                    textbox=prompt_text_box,
                    additional_inputs=[prompt_model_info, prompt_info],
                    submit_btn="Soumettre",
                    retry_btn=" Réessayer",
                    undo_btn=" Annuler",
                    clear_btn=" Effacer",
                    fill_height=True
                )
    with gr.Tab("Assistant visuel"):
        with gr.Row():
            with gr.Column(scale=1):
                history_flag = gr.Checkbox(label="Activer le contexte")
                chinese_flag = gr.Checkbox(value=True, label="Forcer la réponse en français")
                image = gr.Image(type="filepath")
            with gr.Column(scale=4):
                chat_bot = gr.Chatbot(height=600)
                with gr.Row():
                    retry_btn = gr.Button(" Réessayer")
                    undo_btn = gr.Button(" Annuler")
                    clear_btn = gr.Button(" Effacer")
                with gr.Row():
                    message = gr.Textbox(show_label=False, container=False, scale=5)
                    submit_btn = gr.Button("Soumettre", variant="primary", scale=1)
        image.upload(fn=vl_image_upload, inputs=[image, chat_bot], outputs=[image, chat_bot])
        submit_btn.click(fn=vl_submit_message, inputs=[message, chat_bot], outputs=[message, chat_bot]).then(fn=vl_submit, inputs=[history_flag, chinese_flag, chat_bot], outputs=[chat_bot])
        retry_btn.click(fn=vl_retry, inputs=[chat_bot], outputs=[chat_bot]).then(fn=vl_submit, inputs=[history_flag, chinese_flag, chat_bot], outputs=[chat_bot])
        undo_btn.click(fn=vl_undo, inputs=[chat_bot], outputs=[message, chat_bot])
        clear_btn.click(fn=vl_clear, inputs=[], outputs=[image, message, chat_bot])
    demo.load(fn=init)
if __name__ == "__main__":
    demo.launch(share=False)