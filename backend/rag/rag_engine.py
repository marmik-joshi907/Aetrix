"""
Engine for the SatIntel chatbot.

Uses native google.generativeai SDK for generating answers grounded in
both static knowledge and live pipeline data. Since Gemini has a massive 
context window, we feed the context directly without vector retrieval, 
avoiding embedding rate limits.
"""
import logging
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from typing import Optional

logger = logging.getLogger(__name__)

# Global engine singleton
_engine = None


class RAGEngine:
    """Chat engine using direct context injection."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.llm = None
        self.pipeline = None
        self._initialized = False
        self._knowledge_text = ""

    def initialize(self):
        """Initialize the LLM and build knowledge text."""
        try:
            from rag.knowledge_docs import KNOWLEDGE_DOCUMENTS

            logger.info("Initializing native Chat engine...")

            # Configure API key
            genai.configure(api_key=self.api_key)

            # 1. Initialize the generative model
            self.llm = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                system_instruction=(
                    "You are SatIntel AI Assistant, embedded in a Satellite Environmental "
                    "Intelligence Platform. You help users understand environmental data "
                    "for Indian cities including temperature, vegetation (NDVI), "
                    "air pollution (AQI), and soil moisture. "
                    "Be concise, factual, and helpful. When referencing data values, "
                    "cite the specific numbers. If you don't know something, say so. "
                    "Keep answers under 200 words unless detail is required. "
                    "Format nicely with bullets if needed."
                )
            )

            # 2. Build knowledge text
            self._knowledge_text = "\n\n".join([
                f"## {kd['title']}\n{kd['content']}"
                for kd in KNOWLEDGE_DOCUMENTS
            ])

            self._initialized = True
            logger.info("✅ Chatbot engine initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Chat engine: {e}")
            self._initialized = False

    def set_pipeline(self, pipeline):
        """Set the data pipeline reference for live context."""
        self.pipeline = pipeline

    def _build_live_context(self, city: str, week: int) -> str:
        """Pull live stats from the pipeline to enrich chatbot answers."""
        if self.pipeline is None or not self.pipeline.is_loaded:
            return "Live data is not currently available."

        import config

        if city not in self.pipeline.data:
            return f"No data loaded for city: {city}"

        data = self.pipeline.get_data(city)
        meta = self.pipeline.get_metadata(city)

        if data is None or meta is None:
            return f"No data available for {city}."

        lines = [f"=== Live Environmental Data for {city} (Week {week}) ==="]

        import numpy as np

        for param in ["temperature", "ndvi", "pollution", "soil_moisture"]:
            param_data = data.get(param)
            if param_data is None:
                continue
            if param_data.ndim == 3:
                grid = param_data[week] if 0 <= week < param_data.shape[0] else param_data[-1]
            else:
                grid = param_data

            mean_val = float(np.nanmean(grid))
            min_val = float(np.nanmin(grid))
            max_val = float(np.nanmax(grid))
            unit = meta.get("parameters", {}).get(param, {}).get("unit", "")

            lines.append(
                f"  {param}: mean={mean_val:.2f}{unit}, "
                f"min={min_val:.2f}{unit}, max={max_val:.2f}{unit}"
            )

        lines.append(f"  Grid: {meta.get('grid_size', 50)}x{meta.get('grid_size', 50)} "
                      f"@ {meta.get('resolution_km', 0.5)}km resolution")
        lines.append(f"  Center: ({meta.get('center_lat', 'N/A')}, {meta.get('center_lon', 'N/A')})")
        lines.append(f"  Available cities: {', '.join(config.CITIES.keys())}")

        return "\n".join(lines)

    def ask(self, question: str, city: str = "Ahmedabad", week: int = -1) -> dict:
        """
        Answer a user question using the LLM with direct context injection.
        """
        if not self._initialized or self.llm is None:
            return {
                "reply": "The chatbot is still starting up. Please try again in a few seconds.",
                "sources": [],
            }

        try:
            # 1. Use full knowledge text
            knowledge_context = self._knowledge_text
            sources = ["SatIntel Knowledge Base"]

            # 2. Build live context
            live_context = self._build_live_context(city, week)

            # 3. Compose prompt
            prompt = (
                f"--- KNOWLEDGE CONTEXT ---\n{knowledge_context}\n\n"
                f"--- LIVE DATA ---\n{live_context}\n\n"
                f"--- USER QUESTION ---\n{question}"
            )

            # 4. Call native Gemini with automatic exponential backoff retry
            import time
            max_retries = 4
            base_delay = 2
            
            for attempt in range(max_retries):
                try:
                    response = self.llm.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.3,
                            max_output_tokens=1024,
                        )
                    )
                    return {
                        "reply": response.text,
                        "sources": sources,
                    }
                except Exception as e:
                    error_msg = str(e).lower()
                    if "429" in error_msg or "resourceexhausted" in error_msg or "quota" in error_msg:
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)  # 2s, 4s, 8s
                            logger.warning(f"Rate limited. Retrying in {delay}s...")
                            time.sleep(delay)
                            continue
                    
                    # If we run out of retries or hit a different error, break
                    raise e

        except Exception as e:
            logger.error(f"RAG query error: {e}")
            error_msg = str(e)
            if "429" in error_msg or "ResourceExhausted" in error_msg or "quota" in error_msg.lower():
                return {
                    "reply": "⏳ The AI is temporarily rate-limited (free tier). Please wait ~30 seconds and try again.",
                    "sources": [],
                }
            return {
                "reply": f"I encountered an error. Please try again shortly. ({str(e)[:80]})",
                "sources": [],
            }


def get_engine() -> Optional[RAGEngine]:
    """Get the global RAG engine instance."""
    return _engine


def init_engine(api_key: str) -> RAGEngine:
    """Initialize and return the global RAG engine."""
    global _engine
    _engine = RAGEngine(api_key)
    _engine.initialize()
    return _engine
