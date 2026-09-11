import os
import google.generativeai as genai
from transformers import pipeline, T5ForConditionalGeneration, AutoTokenizer, T5Tokenizer
import warnings
warnings.filterwarnings('ignore')

class TypoCorrector:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key="AIzaSyDrYXOmHqiChayrg_yC0i-aGi-OqeJw1v4")
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # Initialize models (lazy loading)
        self.models = {}
        
    def _load_model(self, model_name):
        """Lazy load models to save memory"""
        if model_name not in self.models:
            try:
                if model_name == "spelling-basic":
                    self.models[model_name] = pipeline("text2text-generation", 
                                                     model="oliverguhr/spelling-correction-english-base")
                elif model_name == "t5-spell":
                    tokenizer = AutoTokenizer.from_pretrained("ai-forever/T5-large-spell")
                    model = T5ForConditionalGeneration.from_pretrained("ai-forever/T5-large-spell")
                    self.models[model_name] = {"tokenizer": tokenizer, "model": model}
                elif model_name == "spoken-typo":
                    tokenizer = T5Tokenizer.from_pretrained("willwade/t5-small-spoken-typo")
                    model = T5ForConditionalGeneration.from_pretrained("willwade/t5-small-spoken-typo")
                    self.models[model_name] = {"tokenizer": tokenizer, "model": model}
            except Exception as e:
                print(f"Error loading {model_name}: {e}")
                return None
        return self.models.get(model_name)
    
    def correct_with_gemini(self, text):
        """Use Gemini API for grammar correction"""
        try:
            prompt = f"Please correct the grammar, spelling, and punctuation in this text. Return only the corrected text without any explanations: {text}"
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def correct_spelling_basic(self, text):
        """Basic spelling correction"""
        model = self._load_model("spelling-basic")
        if model:
            try:
                result = model(text, max_length=2048)
                return result[0]['generated_text']
            except Exception as e:
                return f"Error: {str(e)}"
        return "Model not available"
    
    def correct_t5_spell(self, text):
        """T5 large spell correction"""
        model_data = self._load_model("t5-spell")
        if model_data:
            try:
                tokenizer = model_data["tokenizer"]
                model = model_data["model"]
                input_text = f"grammar: {text}"
                inputs = tokenizer(input_text, return_tensors="pt")
                outputs = model.generate(**inputs, max_length=512)
                return tokenizer.decode(outputs[0], skip_special_tokens=True)
            except Exception as e:
                return f"Error: {str(e)}"
        return "Model not available"
    
    def correct_spoken_typo(self, text):
        """Correct conversational typos"""
        model_data = self._load_model("spoken-typo")
        if model_data:
            try:
                tokenizer = model_data["tokenizer"]
                model = model_data["model"]
                input_text = f"grammar: {text}"
                inputs = tokenizer(input_text, return_tensors="pt")
                output = model.generate(**inputs, num_beams=5, min_length=1, max_new_tokens=50)
                return tokenizer.decode(output[0], skip_special_tokens=True)
            except Exception as e:
                return f"Error: {str(e)}"
        return "Model not available"
    
    def correct_all_methods(self, text):
        """Get corrections from all available methods"""
        results = {
            "original": text,
            "gemini": self.correct_with_gemini(text),
            "basic_spelling": self.correct_spelling_basic(text),
            "t5_spell": self.correct_t5_spell(text),
            "spoken_typo": self.correct_spoken_typo(text)
        }
        return results

# Global instance
typo_corrector = TypoCorrector()