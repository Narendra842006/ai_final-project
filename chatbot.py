"""
AI Medical Chatbot for Patient Assistance
Rule-based conversational AI to help patients describe symptoms
"""

import streamlit as st
from typing import List, Tuple
import utils
import config

class MedicalChatbot:
    """Simple rule-based medical chatbot for symptom assistance"""
    
    def __init__(self, language: str = 'English'):
        self.language = language
        self.conversation_history = []
        
    def get_response(self, user_input: str) -> str:
        """Generate response based on user input"""
        user_input_lower = user_input.lower()
        
        # Greeting patterns
        if any(word in user_input_lower for word in ['hello', 'hi', 'hey', 'hola', 'namaste']):
            return self._translate_response('greeting')
        
        # Emergency keywords
        if any(word in user_input_lower for word in ['emergency', 'severe', 'critical', 'can\'t breathe', 'unconscious']):
            return self._translate_response('emergency')
        
        # Chest pain
        if 'chest' in user_input_lower and ('pain' in user_input_lower or 'hurt' in user_input_lower):
            return self._translate_response('chest_pain')
        
        # Fever
        if any(word in user_input_lower for word in ['fever', 'hot', 'temperature', 'fiebre', 'बुखार']):
            return self._translate_response('fever')
        
        # Breathing issues
        if any(word in user_input_lower for word in ['breath', 'breathing', 'respirar', 'सांस']):
            return self._translate_response('breathing')
        
        # Headache
        if any(word in user_input_lower for word in ['head', 'headache', 'cabeza', 'सिर']):
            return self._translate_response('headache')
        
        # Cough
        if any(word in user_input_lower for word in ['cough', 'tos', 'खांसी']):
            return self._translate_response('cough')
        
        # Stomach issues
        if any(word in user_input_lower for word in ['stomach', 'abdominal', 'nausea', 'vomit', 'estómago', 'पेट']):
            return self._translate_response('stomach')
        
        # General symptom inquiry
        if any(word in user_input_lower for word in ['symptom', 'sick', 'ill', 'síntoma', 'लक्षण']):
            return self._translate_response('symptom_list')
        
        # Default response
        return self._translate_response('default')
    
    def _translate_response(self, response_key: str) -> str:
        """Get translated response based on key"""
        responses = {
            'English': {
                'greeting': "Hello! I'm here to help you describe your symptoms. How are you feeling today?",
                'emergency': "🚨 This sounds serious! Please call emergency services (911) immediately or go to the nearest emergency room. Your health is the priority!",
                'chest_pain': "Chest pain can be serious. Are you also experiencing: shortness of breath, sweating, or radiating pain to your arm or jaw? If yes, please seek immediate medical attention. I'll note chest pain in your symptoms.",
                'fever': "I understand you have a fever. How high is your temperature? Are you experiencing any other symptoms like chills, body aches, or sweating? Fever can indicate infection or inflammation.",
                'breathing': "Difficulty breathing requires attention. Is it constant or only with exertion? Do you have any chest tightness? I'll note this symptom for the medical team.",
                'headache': "Headaches can have many causes. Is it a sharp pain, throbbing, or pressure? Is it accompanied by nausea, sensitivity to light, or vision changes?",
                'cough': "Tell me more about your cough. Is it dry or producing mucus? Any wheezing or chest tightness? How long have you had it?",
                'stomach': "Stomach issues can be uncomfortable. Are you experiencing nausea, vomiting, diarrhea, or pain? When did it start?",
                'symptom_list': "Common symptoms I can help with include:\n• Fever\n• Cough\n• Chest Pain\n• Headache\n• Shortness of Breath\n• Abdominal Pain\n• Nausea/Vomiting\n\nPlease describe what you're experiencing.",
                'default': "I understand. Can you tell me more about your symptoms? When did they start? How severe are they on a scale of 1-10?"
            },
            'Spanish': {
                'greeting': "¡Hola! Estoy aquí para ayudarte a describir tus síntomas. ¿Cómo te sientes hoy?",
                'emergency': "🚨 ¡Esto suena grave! Llame a los servicios de emergencia (911) inmediatamente o vaya a la sala de emergencias más cercana. ¡Tu salud es la prioridad!",
                'chest_pain': "El dolor de pecho puede ser grave. ¿También experimenta: falta de aire, sudoración o dolor que se irradia al brazo o la mandíbula? Si es así, busque atención médica inmediata.",
                'fever': "Entiendo que tienes fiebre. ¿Qué tan alta es tu temperatura? ¿Experimentas otros síntomas como escalofríos, dolores corporales o sudoración?",
                'breathing': "La dificultad para respirar requiere atención. ¿Es constante o solo con esfuerzo? ¿Tiene opresión en el pecho?",
                'headache': "Los dolores de cabeza pueden tener muchas causas. ¿Es un dolor agudo, pulsátil o de presión? ¿Se acompaña de náuseas o sensibilidad a la luz?",
                'cough': "Cuéntame más sobre tu tos. ¿Es seca o produce moco? ¿Alguna sibilancia o opresión en el pecho?",
                'stomach': "Los problemas estomacales pueden ser incómodos. ¿Experimentas náuseas, vómitos, diarrea o dolor?",
                'symptom_list': "Los síntomas comunes con los que puedo ayudar incluyen:\n• Fiebre\n• Tos\n• Dolor de Pecho\n• Dolor de Cabeza\n• Dificultad para Respirar\n• Dolor Abdominal\n• Náuseas/Vómitos",
                'default': "Entiendo. ¿Puedes contarme más sobre tus síntomas? ¿Cuándo comenzaron? ¿Qué tan graves son en una escala del 1 al 10?"
            },
            'Hindi': {
                'greeting': "नमस्ते! मैं आपके लक्षणों का वर्णन करने में मदद के लिए यहां हूं। आज आप कैसा महसूस कर रहे हैं?",
                'emergency': "🚨 यह गंभीर लगता है! कृपया तुरंत आपातकालीन सेवाओं को कॉल करें या निकटतम आपातकालीन कक्ष में जाएं। आपका स्वास्थ्य प्राथमिकता है!",
                'chest_pain': "छाती में दर्द गंभीर हो सकता है। क्या आप सांस लेने में कठिनाई, पसीना, या बांह या जबड़े में दर्द का अनुभव कर रहे हैं? यदि हां, तो कृपया तत्काल चिकित्सा सहायता लें।",
                'fever': "मैं समझता हूं कि आपको बुखार है। आपका तापमान कितना अधिक है? क्या आप कंपकंपी, शरीर में दर्द, या पसीना जैसे अन्य लक्षणों का अनुभव कर रहे हैं?",
                'breathing': "सांस लेने में कठिनाई पर ध्यान देने की आवश्यकता है। क्या यह लगातार है या केवल परिश्रम के साथ? क्या आपको छाती में जकड़न है?",
                'headache': "सिरदर्द के कई कारण हो सकते हैं। क्या यह तेज दर्द, धड़कन या दबाव है? क्या यह मतली या प्रकाश के प्रति संवेदनशीलता के साथ है?",
                'cough': "मुझे अपनी खांसी के बारे में और बताएं। क्या यह सूखी है या बलगम पैदा कर रही है? कोई घरघराहट या छाती में जकड़न?",
                'stomach': "पेट की समस्याएं असहज हो सकती हैं। क्या आप मतली, उल्टी, दस्त या दर्द का अनुभव कर रहे हैं?",
                'symptom_list': "सामान्य लक्षण जिनमें मैं मदद कर सकता हूं:\n• बुखार\n• खांसी\n• छाती में दर्द\n• सिरदर्द\n• सांस लेने में कठिनाई\n• पेट दर्द\n• जी मिचलाना/उल्टी",
                'default': "मैं समझता हूं। क्या आप मुझे अपने लक्षणों के बारे में और बता सकते हैं? वे कब शुरू हुए? 1-10 के पैमाने पर वे कितने गंभीर हैं?"
            },
            'Tamil': {
                'greeting': "வணக்கம்! உங்கள் அறிகுறிகளை விவரிக்க நான் இங்கே இருக்கிறேன். இன்று நீங்கள் எப்படி உணர்கிறீர்கள்?",
                'emergency': "🚨 இது கவலைகரமானதாக தேர்கிறது! தயவு செய்து உடனடியாக அவசர சேவைகளை (911) அழைக்கவும் அல்லது அருகிலுள்ள அவசர அறைக்கு செல்லவும்!",
                'chest_pain': "மார்பு வலி கவலைகரமானதாக இருக்கலாம். மூச்சு திணறல், வியர்வை, கை அல்லது தாடையையும் பரவும் வலியை நீங்கள் அனுபவிக்கிறீர்களா? ஆமா எனில், தயவு செய்து உடனடி மருத்துவ உதவியை பெறவும்.",
                'fever': "உங்களுக்கு காய்ச்சல் இருக்கிறது என்று நான் புரிந்துகொள்கிறேன். உங்கள் வெப்பநிலை என்ன? நடுக்கம், உடல் வலி, வியர்வை போன்ற மற்ற அறிகுறிகள் இருக்கின்றனவா?",
                'breathing': "மூச்சு திணறலில் சிரமம் கவனம் தேவை. இது தொடர்ந்ததா அல்லது உழைப்பின் போது மட்டும் என்று உணருங்களா? மார்பு இறுக்கம் இருக்கிறதா?",
                'headache': "தலைவலிக்கு பல காரணங்கள் இருக்கலாம். இது குத்தும் வலி, துடிப்பு, அல்லது அழுத்தமா? கண் கலங்கம் அல்லது வெளிச்ச நுணர்வு இருக்கிறதா?",
                'cough': "உங்கள் இருமலை பற்றி மேலும் சொல்லுங்கள். இது வரண்ட இருமலா அல்லது சலியை உறுவிக்கிறதா? மார்பு இறுக்கம் இருக்கிறதா?",
                'stomach': "வயிறு பிரச்சினைகள் அசவர்த்தியாக இருக்கலாம். கண் கலங்கம், வாந்தி, வயிற்று போக்கு, அல்லது வலி உணருங்களா?",
                'symptom_list': "நான் உதவ செய்ய கூடிய பொது அறிகுறிகள்:\n• காய்ச்சல்\n• இருமல்\n• மார்பு வலி\n• தலைவலி\n• மூச்சு திணறல்\n• வயிறு வலி\n\nநீங்கள் அனுபவிப்பதை விவரிக்கவும்.",
                'default': "நான் புரிந்துகொள்கிறேன். உங்கள் அறிகுறிகளை பற்றி மேலும் சொல்ல முடியுமா? அவை எப்போது தொடங்கின? 1-10 அளவில் என்ன தீவிரம்?"
            },
            'Telugu': {
                'greeting': "నమస్కారం! మీ లక్షణాలను వివరించడంలో సహాయం చేయడానికి నేను ఇక్కడ ఉన్నాను. ఈ రోజు మీరు ఎలా ఉన్నారు?",
                'emergency': "🚨 ఇది తీవ్రంగా ఉంది! దయచేసి వెంటనే అవసర సేవలు (911)కు కాల్ చేయండి లేదా సమీపంలోని అవసర క్షేత్రంలోకి వెళ్ళండి!",
                'chest_pain': "వక్షస్సు నోపి తీవ్రంగా ఉంటుంది. మీరు కూడా ఈ క్రింది అనుభవిస్తున్నారా: ఊరుదినకురా, చెమట్లు, లేదా చెవి లేదా తాడిబందకు వ్యాపించే నోపి? అవును అంటే, దయచేసి వైద్య సహాయం పొందండి.",
                'fever': "మీకు జ్వరం ఉందని నేను అర్థం చేసుకున్నాను. మీ ఉష్ణోగ్రత ఎంత? మీరు విపరీతం, శరీర నోపులు, చెమటలు వంటి ఇతర లక్షణాలను అనుభవిస్తున్నారా?",
                'breathing': "ఊరుదినకురలో కష్టాలు తీర్వ్రంగా ఉంటాయి. ఇది నిరంతరంగా ఉందా లేదా శ్రమ చేస్తే ఉందా? వక్షస్సు కినుకు బిగిన అనుభూతి ఉందా?",
                'headache': "తల నోపికి అనేక కారణాలు ఉంటాయి. ఇది తీవ్ర నోపి, కూల్చివి అనుభూతి, లేదా నేమి నోపినా? వాంతి, వెలుగు సంవేదనశీలత లేదా దృష్టి మార్పులు ఉన్నాయా?",
                'cough': "మీ దెప్ప గురించి మరిన్త చెప్పండి. ఇది మొరగిన దెప్పనా లేదా కఫం తో ఉందా? హిస్ వ్రాయడం లేదా వక్షస్సు కినుకు బిగిన ఉందా?",
                'stomach': "కడుపు సమస్యలు అసౌకర్యంగా ఉంటాయి. మీరు వాంతి, వోమిటింగ్, బడిజిపులు, లేదా నోపిని అనుభవిస్తున్నారా?",
                'symptom_list': "నేను సహాయం చేయగల సాధారణ లక్షణాలు:\n• జ్వరం\n• దెప్ప\n• వక్షస్సు నోపి\n• తల నోపి\n• ఊరుదినకురలు\n• కడుపు నోపి\n\nమీరు ఏమి అనుభవిస్తున్నారో వివరించండి.",
                'default': "నేను అర్థం చేసుకున్నాను. మీ లక్షణాల గురించి కూడా మరిన్త చెప్పగలరా? అవి ఎప్పుడు ప్రారంభమయ్యాయి? 1-10 స్కేల్లో ఎంత తీవ్రంగా ఉన్నాయి?"
            }
        }
        
        return responses.get(self.language, responses['English']).get(response_key, responses['English']['default'])


def render_chatbot(language: str = 'English'):
    """Render chatbot interface in Streamlit sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"🤖 {utils.translate('chat_assistant', language)}")
    st.sidebar.caption(utils.translate('medical_disclaimer', language))
    
    # Initialize chatbot in session state
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = MedicalChatbot(language)
        st.session_state.chat_history = []
    
    # Update language if changed
    if st.session_state.chatbot.language != language:
        st.session_state.chatbot.language = language
    
    # Display chat history
    chat_container = st.sidebar.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f'<div class="chat-message user-message">👤 {message["content"]}</div>', 
                          unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message bot-message">🤖 {message["content"]}</div>', 
                          unsafe_allow_html=True)
    
    # Chat input
    user_input = st.sidebar.text_input(
        utils.translate('chat_placeholder', language),
        key='chat_input',
        label_visibility='collapsed'
    )
    
    if st.sidebar.button("Send", key='chat_send'):
        if user_input:
            # Add user message
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Get bot response
            response = st.session_state.chatbot.get_response(user_input)
            st.session_state.chat_history.append({
                'role': 'bot',
                'content': response
            })
            
            st.rerun()
