"""
Gemini AI handler for generating summaries
"""

import logging
from typing import Optional
import google.generativeai as genai


class GeminiHandler:
    """Handles Gemini AI operations for content summarization"""
    
    def __init__(self, api_key: str):
        """Initialize Gemini handler with API key"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.logger = logging.getLogger(__name__)
    
    def summarize_video(self, transcript: str, video_title: str, channel_name: str) -> Optional[str]:
        """
        Generate a summary of a video transcript
        
        Args:
            transcript: Full video transcript text
            video_title: Title of the video
            channel_name: Name of the YouTube channel
        
        Returns:
            Summary text or None if failed
        """
        try:
            self.logger.info(f"Generating summary for: {video_title}")
            
            prompt = f"""
            Eres un especialista en crear resúmenes concisos de videos financieros y económicos.
            
            CANAL: {channel_name}
            TÍTULO: {video_title}
            
            Crea un resumen estructurado del siguiente video:
            
            TRANSCRIPCIÓN:
            {transcript}
            
            FORMATO REQUERIDO:
            
            🎯 **TEMA PRINCIPAL**
            [Describe en 1-2 líneas el tema central]
            
            📋 **PUNTOS CLAVE**
            • [Punto importante 1]
            • [Punto importante 2]
            • [Punto importante 3]
            • [Máximo 5 puntos]
            
            💡 **CONCLUSIÓN**
            [Takeaway principal en 1-2 líneas]
            
            INSTRUCCIONES:
            - Sé conciso pero informativo
            - Lenguaje profesional pero accesible
            - Máximo 2000 caracteres
            - Enfócate en información financiera/económica
            """
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                self.logger.info(f"Summary generated: {len(response.text)} characters")
                return response.text
            else:
                self.logger.error("Empty response from Gemini")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return None


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    logging.basicConfig(level=logging.INFO)
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Set GEMINI_API_KEY in .env file")
        exit(1)
    
    gemini = GeminiHandler(api_key)
    
    # Test with sample text
    test_transcript = "Hoy hablamos sobre el mercado de valores y las predicciones económicas para 2025..."
    summary = gemini.summarize_video(test_transcript, "Test Video", "Test Channel")
    
    if summary:
        print("Summary generated:")
        print(summary)
    else:
        print("Failed to generate summary")