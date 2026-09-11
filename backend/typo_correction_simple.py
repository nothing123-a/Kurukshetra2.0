"""
Simple Typo Correction Service - Fallback Implementation
"""
import re
import requests
import json

class SimpleTypoCorrector:
    def __init__(self):
        self.gemini_api_key = "AIzaSyDrYXOmHqiChayrg_yC0i-aGi-OqeJw1v4"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        
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
                    # Clean up the response
                    corrected = corrected.replace('"', '').strip()
                    return corrected
            
            return text  # Return original if API fails
            
        except Exception as e:
            print(f"Gemini correction error: {e}")
            return text
    
    def correct_with_basic_spelling(self, text):
        """Basic spelling correction using simple rules"""
        # Common typo corrections
        corrections = {
            'teh': 'the',
            'adn': 'and',
            'taht': 'that',
            'thier': 'their',
            'recieve': 'receive',
            'seperate': 'separate',
            'definately': 'definitely',
            'occured': 'occurred',
            'begining': 'beginning',
            'accomodate': 'accommodate'
        }
        
        words = text.split()
        corrected_words = []
        
        for word in words:
            # Remove punctuation for checking
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in corrections:
                # Replace while preserving case and punctuation
                corrected = corrections[clean_word]
                if word[0].isupper():
                    corrected = corrected.capitalize()
                # Preserve punctuation
                punctuation = re.findall(r'[^\w]', word)
                if punctuation:
                    corrected += ''.join(punctuation)
                corrected_words.append(corrected)
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)
    
    def get_best_correction(self, text):
        """Get the best correction using available methods"""
        try:
            # Try Gemini first
            gemini_result = self.correct_with_gemini(text)
            if gemini_result != text:
                return gemini_result, 'gemini'
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
            else:
                if method == 'gemini':
                    corrected = self.correct_with_gemini(text)
                else:
                    corrected = self.correct_with_basic_spelling(text)
                results.append({
                    'original': text,
                    'corrected': corrected,
                    'method_used': method
                })
        return results

# Create global instance
typo_corrector = SimpleTypoCorrector()