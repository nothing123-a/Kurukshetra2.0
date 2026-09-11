"""
Enhanced Typo Correction Service with Multiple AI Models
"""
import requests
import json
import re

class EnhancedTypoCorrector:
    def __init__(self, gemini_api_key=None):
        self.gemini_api_key = gemini_api_key or "AIzaSyDrYXOmHqiChayrg_yC0i-aGi-OqeJw1v4"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        
        # Initialize models (fallback to simple corrections if transformers not available)
        self.models_available = self._initialize_models()
        
    def _initialize_models(self):
        """Initialize AI models with fallback"""
        try:
            from transformers import pipeline
            
            # Try to load models
            self.spell_corrector = pipeline("text2text-generation", model="oliverguhr/spelling-correction-english-base")
            self.t5_spell = pipeline("text2text-generation", model="vennify/t5-base-grammar-correction")
            self.grammar_corrector = pipeline("text2text-generation", model="prithivida/grammar_error_correcter_v1")
            
            print("✅ All AI models loaded successfully")
            return True
        except Exception as e:
            print(f"⚠️ AI models not available, using fallback methods: {e}")
            return False
    
    def correct_with_gemini(self, text):
        """Use Gemini AI for text correction"""
        try:
            prompt = f"""Please correct any spelling, grammar, and punctuation errors in the following text. Return only the corrected text without any explanations:

Text: "{text}"

Corrected text:"""
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 1000
                }
            }
            
            response = requests.post(self.gemini_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    corrected = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    corrected = corrected.replace('"', '').strip()
                    return corrected
            
            return text
            
        except Exception as e:
            print(f"Gemini correction error: {e}")
            return text
    
    def correct_with_basic_spelling(self, text):
        """Basic spelling correction using AI model or fallback"""
        try:
            if self.models_available and hasattr(self, 'spell_corrector'):
                result = self.spell_corrector(text, max_length=100)
                return result[0]['generated_text']
            else:
                return self._fallback_spelling_correction(text)
        except Exception as e:
            print(f"Basic spelling error: {e}")
            return self._fallback_spelling_correction(text)
    
    def correct_with_advanced_spelling(self, text):
        """Advanced T5 spelling correction"""
        try:
            if self.models_available and hasattr(self, 't5_spell'):
                result = self.t5_spell(f"fix: {text}", max_length=100)
                return result[0]['generated_text']
            else:
                return self._fallback_spelling_correction(text)
        except Exception as e:
            print(f"T5 spelling error: {e}")
            return self._fallback_spelling_correction(text)
    
    def correct_with_grammar(self, text):
        """Grammar correction using AI model"""
        try:
            if self.models_available and hasattr(self, 'grammar_corrector'):
                result = self.grammar_corrector(text, max_length=100)
                return result[0]['generated_text']
            else:
                return self._fallback_grammar_correction(text)
        except Exception as e:
            print(f"Grammar correction error: {e}")
            return self._fallback_grammar_correction(text)
    
    def correct_with_spoken_typo(self, text):
        """Conversational typo correction"""
        try:
            # Use Gemini for conversational style
            prompt = f"""Fix this conversational text, keeping the casual tone but correcting typos and grammar:

"{text}"

Fixed:"""
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 1000
                }
            }
            
            response = requests.post(self.gemini_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    corrected = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    corrected = corrected.replace('"', '').strip()
                    return corrected
            
            return self._fallback_spelling_correction(text)
            
        except Exception as e:
            print(f"Spoken typo error: {e}")
            return self._fallback_spelling_correction(text)
    
    def _fallback_spelling_correction(self, text):
        """Simple fallback spelling correction"""
        corrections = {
            'teh': 'the', 'adn': 'and', 'taht': 'that', 'thier': 'their',
            'recieve': 'receive', 'seperate': 'separate', 'definately': 'definitely',
            'occured': 'occurred', 'begining': 'beginning', 'accomodate': 'accommodate',
            'sentnce': 'sentence', 'gramer': 'grammar', 'typo': 'typo',
            'diferent': 'different', 'methds': 'methods', 'comparsion': 'comparison'
        }
        
        words = text.split()
        corrected_words = []
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in corrections:
                corrected = corrections[clean_word]
                if word[0].isupper():
                    corrected = corrected.capitalize()
                punctuation = re.findall(r'[^\w]', word)
                if punctuation:
                    corrected += ''.join(punctuation)
                corrected_words.append(corrected)
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)
    
    def _fallback_grammar_correction(self, text):
        """Simple grammar correction"""
        # Basic grammar fixes
        text = re.sub(r'\bi\b', 'I', text)  # Capitalize I
        text = re.sub(r'([.!?])\s*([a-z])', lambda m: m.group(1) + ' ' + m.group(2).upper(), text)  # Capitalize after punctuation
        text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
        return text
    
    def get_best_correction(self, text):
        """Get the best correction using available methods"""
        try:
            # Try Gemini first
            gemini_result = self.correct_with_gemini(text)
            if gemini_result != text and len(gemini_result) > 0:
                return gemini_result, 'gemini'
        except:
            pass
        
        # Try advanced spelling
        try:
            advanced_result = self.correct_with_advanced_spelling(text)
            if advanced_result != text and len(advanced_result) > 0:
                return advanced_result, 'advanced_spelling'
        except:
            pass
        
        # Fallback to basic spelling
        basic_result = self.correct_with_basic_spelling(text)
        return basic_result, 'basic_spelling'
    
    def correct_text_comprehensive(self, text):
        """Comprehensive correction showing all methods"""
        results = {'original': text}
        
        # Gemini correction
        try:
            results['gemini'] = self.correct_with_gemini(text)
        except:
            results['gemini'] = text
        
        # Basic spelling
        results['basic_spelling'] = self.correct_with_basic_spelling(text)
        
        # Advanced spelling
        results['advanced_spelling'] = self.correct_with_advanced_spelling(text)
        
        # Grammar correction
        results['grammar'] = self.correct_with_grammar(text)
        
        # Spoken typo
        results['spoken_typo'] = self.correct_with_spoken_typo(text)
        
        return results
    
    def batch_correct(self, texts, method='best'):
        """Batch correct multiple texts"""
        results = []
        for text in texts:
            if method == 'best':
                corrected, method_used = self.get_best_correction(text)
                results.append({
                    'original': text,
                    'corrected': corrected,
                    'method_used': method_used
                })
            elif method == 'comprehensive':
                comprehensive_results = self.correct_text_comprehensive(text)
                results.append({
                    'original': text,
                    'results': comprehensive_results
                })
            else:
                if method == 'gemini':
                    corrected = self.correct_with_gemini(text)
                elif method == 'basic_spelling':
                    corrected = self.correct_with_basic_spelling(text)
                elif method == 'advanced_spelling':
                    corrected = self.correct_with_advanced_spelling(text)
                elif method == 'grammar':
                    corrected = self.correct_with_grammar(text)
                elif method == 'spoken_typo':
                    corrected = self.correct_with_spoken_typo(text)
                else:
                    corrected = self.correct_with_basic_spelling(text)
                
                results.append({
                    'original': text,
                    'corrected': corrected,
                    'method_used': method
                })
        return results