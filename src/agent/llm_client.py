import requests


class OllamaClient:
    """A thin client for calling a local Ollama model.

    Args:
        None

    Returns:
        None
    """

    def __init__(self, model: str = "llama3.1:8b", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host

    def generate(self, prompt: str) -> str:
        """Send a prompt to the local Ollama model and return its response.

        Args:
            prompt: The full text prompt to send to the model.

        Returns:
            The model's text response.
        """
        response = requests.post(
            f"{self.host}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=300,
        )
        response.raise_for_status()
        return response.json()["response"]