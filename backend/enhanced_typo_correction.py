#!/usr/bin/env python3
"""
Enhanced Typo Correction with Hugging Face Models and Gemini API
Supports multiple correction methods for better accuracy
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from transformers import pipeline, T5ForConditionalGeneration, AutoTokenizer, T5Tokenizer
import google.generativeai as genai
from happytransformer import HappyTextToText, TTSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedTypoCorrector:
    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize the enhanced typo corrector with multiple specialized models"""
        self.models = {}
        self.gemini_api_key = gemini_api_key
        self.gemini_model = None
        
        # Model specializations
        self.model_purposes = {
            'spelling_basic': 'Basic spelling and typo correction for simple errors',
            'spelling_advanced': 'Advanced spelling correction with context awareness',
            'grammar_correction': 'Grammar structure and sentence formation correction',
            'spoken_typo': 'Conversational text and missing spaces correction',
            'gemini': 'Comprehensive grammar, style, and contextual correction'
        }
        
        # Initialize Gemini if API key is provided
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("✅ Gemini API initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini API: {e}")
        
        self._load_models()
    
    def _load_models(self):
        """Load all Hugging Face models"""
        model_configs = {
            'spelling_basic': {
                'type': 'pipeline',
                'model': 'oliverguhr/spelling-correction-english-base',
                'task': 'text2text-generation'
            },
            'spelling_advanced': {
                'type': 't5_auto',
                'model': 'ai-forever/T5-large-spell'
            },
            'grammar_correction': {
                'type': 'happy_transformer',
                'model': 'vennify/t5-base-grammar-correction'
            },
            'spoken_typo': {
                'type': 't5_tokenizer',
                'model': 'willwade/t5-small-spoken-typo'
            }
        }
        
        for name, config in model_configs.items():
            try:
                if config['type'] == 'pipeline':
                    self.models[name] = pipeline(config['task'], model=config['model'])
                elif config['type'] == 't5_auto':
                    tokenizer = AutoTokenizer.from_pretrained(config['model'])
                    model = T5ForConditionalGeneration.from_pretrained(config['model'])
                    self.models[name] = {'tokenizer': tokenizer, 'model': model}
                elif config['type'] == 'happy_transformer':
                    self.models[name] = HappyTextToText("T5", config['model'])
                elif config['type'] == 't5_tokenizer':
                    tokenizer = T5Tokenizer.from_pretrained(config['model'])
                    model = T5ForConditionalGeneration.from_pretrained(config['model'])
                    self.models[name] = {'tokenizer': tokenizer, 'model': model}
                
                logger.info(f"✅ Loaded model: {name}")
            except Exception as e:
                logger.error(f"❌ Failed to load model {name}: {e}")
    
    def correct_with_basic_spelling(self, text: str) -> str:
        """Correct text using basic spelling correction model"""
        try:
            if 'spelling_basic' in self.models:
                result = self.models['spelling_basic'](text, max_length=2048)
                return result[0]['generated_text']
        except Exception as e:
            logger.error(f"Basic spelling correction failed: {e}")
        return text
    
    def correct_with_advanced_spelling(self, text: str) -> str:
        """Correct text using advanced T5 spelling model"""
        try:
            if 'spelling_advanced' in self.models:
                model_data = self.models['spelling_advanced']
                input_text = f"grammar: {text}"
                inputs = model_data['tokenizer'](input_text, return_tensors="pt")
                outputs = model_data['model'].generate(**inputs)
                return model_data['tokenizer'].decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Advanced spelling correction failed: {e}")
        return text
    
    def correct_with_grammar(self, text: str) -> str:
        """Correct text using grammar correction model"""
        try:
            if 'grammar_correction' in self.models:
                args = TTSettings(num_beams=5, min_length=1)
                result = self.models['grammar_correction'].generate_text(f"grammar: {text}", args=args)
                return result.text
        except Exception as e:
            logger.error(f"Grammar correction failed: {e}")
        return text
    
    def correct_with_spoken_typo(self, text: str) -> str:
        """Correct text using spoken typo model"""
        try:
            if 'spoken_typo' in self.models:
                model_data = self.models['spoken_typo']
                input_text = f"grammar: {text}"
                inputs = model_data['tokenizer'](input_text, return_tensors="pt")
                output = model_data['model'].generate(**inputs, num_beams=5, min_length=1, max_new_tokens=50)
                return model_data['tokenizer'].decode(output[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Spoken typo correction failed: {e}")
        return text
    
    def correct_with_gemini(self, text: str, correction_type: str = 'comprehensive') -> str:
        """Correct text using Gemini API with specialized prompts"""
        try:
            if self.gemini_model:
                prompts = {
                    'comprehensive': f"""You are an expert English language editor. Please correct the following text for:
1. Spelling errors
2. Grammar mistakes
3. Punctuation errors
4. Sentence structure issues
5. Word choice improvements

Return ONLY the corrected text without any explanations, comments, or formatting:

Text: {text}""",
                    'grammar_only': f"""Focus only on correcting grammatical errors in this text. Fix:
- Subject-verb agreement
- Tense consistency
- Sentence structure
- Word order

Return ONLY the corrected text:

Text: {text}""",
                    'spelling_only': f"""Correct only spelling errors in this text. Do not change grammar or sentence structure.

Return ONLY the corrected text:

Text: {text}"""
                }
                
                prompt = prompts.get(correction_type, prompts['comprehensive'])
                response = self.gemini_model.generate_content(prompt)
                return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini correction failed: {e}")
        return text
    
    def correct_text_comprehensive(self, text: str, methods: List[str] = None) -> Dict[str, str]:
        """
        Correct text using multiple methods and return all results
        
        Args:
            text: Input text to correct
            methods: List of methods to use. If None, uses all available methods.
        
        Returns:
            Dictionary with method names as keys and corrected text as values
        """
        if methods is None:
            methods = ['basic_spelling', 'advanced_spelling', 'grammar', 'spoken_typo', 'gemini']
        
        results = {'original': text}
        
        method_map = {
            'basic_spelling': self.correct_with_basic_spelling,
            'advanced_spelling': self.correct_with_advanced_spelling,
            'grammar': self.correct_with_grammar,
            'spoken_typo': self.correct_with_spoken_typo,
            'gemini': lambda x: self.correct_with_gemini(x, 'comprehensive')
        }
        
        for method in methods:
            if method in method_map:
                try:
                    corrected = method_map[method](text)
                    results[method] = corrected
                    logger.info(f"✅ {method}: '{text}' -> '{corrected}'")
                except Exception as e:
                    logger.error(f"❌ {method} failed: {e}")
                    results[method] = text
        
        return results
    
    def get_best_correction(self, text: str) -> Tuple[str, str, Dict[str, str]]:
        """
        Get the best correction by analyzing text type and choosing optimal method
        
        Returns:
            Tuple of (best_corrected_text, method_used, all_results)
        """
        results = self.correct_text_comprehensive(text)
        
        # Analyze text characteristics to choose best method
        text_analysis = self._analyze_text_type(text)
        
        # Choose method based on text analysis
        if text_analysis['has_grammar_issues'] and 'gemini' in results:
            return results['gemini'], 'gemini', results
        elif text_analysis['has_grammar_issues'] and 'grammar' in results:
            return results['grammar'], 'grammar', results
        elif text_analysis['has_spacing_issues'] and 'spoken_typo' in results:
            return results['spoken_typo'], 'spoken_typo', results
        elif text_analysis['has_spelling_errors']:
            if 'advanced_spelling' in results:
                return results['advanced_spelling'], 'advanced_spelling', results
            elif 'basic_spelling' in results:
                return results['basic_spelling'], 'basic_spelling', results
        
        # Fallback to priority order
        priority_order = ['gemini', 'grammar', 'advanced_spelling', 'basic_spelling', 'spoken_typo']
        
        for method in priority_order:
            if method in results and results[method] != text:
                return results[method], method, results
        
        return text, 'original', results
    
    def _analyze_text_type(self, text: str) -> Dict[str, bool]:
        """Analyze text to determine what type of corrections are needed"""
        analysis = {
            'has_spelling_errors': False,
            'has_grammar_issues': False,
            'has_spacing_issues': False,
            'is_conversational': False
        }
        
        # Simple heuristics for text analysis
        words = text.split()
        
        # Check for spacing issues (words stuck together)
        for word in words:
            if len(word) > 15 and word.islower():  # Likely concatenated words
                analysis['has_spacing_issues'] = True
                break
        
        # Check for conversational patterns
        conversational_patterns = ['hihoware', 'howru', 'whatsup', 'gonna', 'wanna']
        if any(pattern in text.lower() for pattern in conversational_patterns):
            analysis['is_conversational'] = True
        
        # Check for grammar issues (simple heuristics)
        grammar_indicators = ['has has', 'are is', 'was were', 'don\'t doesn\'t']
        if any(indicator in text.lower() for indicator in grammar_indicators):
            analysis['has_grammar_issues'] = True
        
        # Check for spelling errors (simple heuristics)
        common_misspellings = ['teh', 'recieve', 'seperate', 'occured', 'definately']
        if any(misspelling in text.lower() for misspelling in common_misspellings):
            analysis['has_spelling_errors'] = True
        
        return analysis
    
    def batch_correct(self, texts: List[str], method: str = 'best') -> List[Dict[str, str]]:
        """
        Correct multiple texts in batch
        
        Args:
            texts: List of texts to correct
            method: Method to use ('best', 'comprehensive', or specific method name)
        
        Returns:
            List of correction results
        """
        results = []
        
        for text in texts:
            if method == 'best':
                corrected, method_used = self.get_best_correction(text)
                results.append({
                    'original': text,
                    'corrected': corrected,
                    'method': method_used
                })
            elif method == 'comprehensive':
                comprehensive_results = self.correct_text_comprehensive(text)
                results.append(comprehensive_results)
            else:
                # Use specific method
                method_map = {
                    'basic_spelling': self.correct_with_basic_spelling,
                    'advanced_spelling': self.correct_with_advanced_spelling,
                    'grammar': self.correct_with_grammar,
                    'spoken_typo': self.correct_with_spoken_typo,
                    'gemini': lambda x: self.correct_with_gemini(x, 'comprehensive')
                }
                
                if method in method_map:
                    corrected = method_map[method](text)
                    results.append({
                        'original': text,
                        'corrected': corrected,
                        'method': method
                    })
                else:
                    results.append({
                        'original': text,
                        'corrected': text,
                        'method': 'none'
                    })
        
        return results

def main():
    """Test the enhanced typo corrector"""
    # Test with Gemini API key
    gemini_key = "AIzaSyDrYXOmHqiChayrg_yC0i-aGi-OqeJw1v4"
    corrector = EnhancedTypoCorrector(gemini_api_key=gemini_key)
    
    # Test texts
    test_texts = [
        "lets do a comparsion",
        "If you bought something goregous, you well be very happy.",
        "This sentences has has bads grammar.",
        "Hihowareyoudoingtaday?",
        "I am writting a leter to my frend about the importent meeting tommorow."
    ]
    
    print("🚀 Testing Enhanced Typo Correction\n")
    print("=" * 80)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: '{text}'")
        print("-" * 60)
        
        # Get comprehensive results
        results = corrector.correct_text_comprehensive(text)
        
        for method, corrected in results.items():
            if method != 'original':
                print(f"{method:20}: {corrected}")
        
        # Get best correction
        best_correction, best_method, all_results = corrector.get_best_correction(text)
        print(f"\n🏆 Best correction ({best_method}): {best_correction}")
        print(f"📊 Method purpose: {corrector.model_purposes.get(best_method, 'Unknown')}")
        print("=" * 80)

if __name__ == "__main__":
    main()