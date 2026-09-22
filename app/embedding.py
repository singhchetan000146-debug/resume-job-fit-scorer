import os
import threading
import numpy as np

class EmbeddingError(RuntimeError):
    pass

class Embedder:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.lock = threading.Lock()

    def embed(self, texts):
        try:
            with self.lock:
                if self.model is None:
                    from fastembed import TextEmbedding
                    self.model = TextEmbedding(self.config.model_name,
                        cache_dir=os.getenv('FIT_MODEL_CACHE', '.model_cache'), threads=2)
                vectors = np.asarray(list(self.model.embed(texts, batch_size=self.config.batch_size)), dtype=float)
            if vectors.ndim != 2 or vectors.shape[0] != len(texts) or not np.isfinite(vectors).all():
                raise ValueError('Invalid embedding output')
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            if (norms < 1e-12).any():
                raise ValueError('Zero embedding')
            return vectors / norms
        except Exception as exc:
            raise EmbeddingError('Embedding model unavailable. Check the first-run download, cache and dependencies, then retry.') from exc
