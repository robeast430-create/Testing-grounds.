import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import json
import pickle
import os

class VectorStore:
    def __init__(self, dimension=384):
        self.dimension = dimension
        self.vectors = []
        self.metadata = []
        self.ids = []
        self.next_id = 0
    
    def add(self, vectors, metadata=None):
        if isinstance(vectors, list):
            vectors = np.array(vectors)
        
        if len(vectors.shape) == 1:
            vectors = vectors.reshape(1, -1)
        
        for i, vec in enumerate(vectors):
            self.vectors.append(vec)
            self.metadata.append(metadata[i] if metadata else {})
            self.ids.append(self.next_id)
            self.next_id += 1
        
        return self.ids[-len(vectors):]
    
    def search(self, query_vector, k=5):
        if isinstance(query_vector, list):
            query_vector = np.array(query_vector)
        
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)
        
        similarities = []
        for vec in self.vectors:
            sim = self.cosine_similarity(query_vector[0], vec)
            similarities.append(sim)
        
        top_indices = np.argsort(similarities)[-k:][::-1]
        
        return [(self.ids[i], similarities[i], self.metadata[i]) for i in top_indices]
    
    def cosine_similarity(self, a, b):
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return dot / (norm_a * norm_b + 1e-10)
    
    def save(self, path):
        data = {
            "vectors": np.array(self.vectors),
            "metadata": self.metadata,
            "ids": self.ids,
            "dimension": self.dimension,
            "next_id": self.next_id
        }
        with open(path, "wb") as f:
            pickle.dump(data, f)
    
    def load(self, path):
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.vectors = list(data["vectors"])
        self.metadata = data["metadata"]
        self.ids = data["ids"]
        self.dimension = data["dimension"]
        self.next_id = data["next_id"]
    
    def count(self):
        return len(self.vectors)


class TextProcessor:
    def __init__(self):
        self.stopwords = set([
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'this', 'but', 'they', 'have',
            'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how'
        ])
    
    def tokenize(self, text):
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        return [t for t in tokens if t not in self.stopwords and len(t) > 2]
    
    def bag_of_words(self, text, vocab=None):
        tokens = self.tokenize(text)
        if vocab is None:
            vocab = set(tokens)
        
        bow = np.zeros(len(vocab))
        vocab_list = list(vocab)
        
        for i, word in enumerate(vocab_list):
            bow[i] = tokens.count(word)
        
        return bow, vocab_list
    
    def tf_idf(self, documents):
        import math
        
        N = len(documents)
        doc_tokens = [self.tokenize(d) for d in documents]
        
        vocab = set()
        for tokens in doc_tokens:
            vocab.update(tokens)
        
        vocab_list = list(vocab)
        tfidf_matrix = []
        
        for tokens in doc_tokens:
            tfidf = np.zeros(len(vocab))
            for i, word in enumerate(vocab_list):
                tf = tokens.count(word)
                if tf > 0:
                    df = sum(1 for t in doc_tokens if word in t)
                    idf = math.log(N / (df + 1))
                    tfidf[i] = tf * idf
            tfidf_matrix.append(tfidf)
        
        return np.array(tfidf_matrix), vocab_list
    
    def extract_keywords(self, text, top_n=10):
        tokens = self.tokenize(text)
        freq = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        
        sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return sorted_tokens[:top_n]
    
    def summarize(self, text, num_sentences=3):
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if len(sentences) <= num_sentences:
            return text
        
        words = self.tokenize(text)
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        scores = []
        for sentence in sentences:
            score = 0
            sentence_words = self.tokenize(sentence)
            for word in sentence_words:
                score += word_freq.get(word, 0)
            scores.append(score / len(sentence_words) if sentence_words else 0)
        
        ranked = sorted(zip(scores, sentences), reverse=True)
        summary = ' '.join([s for _, s in ranked[:num_sentences]])
        
        return summary


class MLModels:
    def __init__(self):
        self.models = {}
        self.history = {}
    
    def linear_regression(self, X, y):
        X = np.array(X)
        y = np.array(y)
        
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)
        
        X_b = np.c_[np.ones((X.shape[0], 1)), X]
        
        theta = np.linalg.lstsq(X_b, y, rcond=None)[0]
        
        model = {
            "type": "linear_regression",
            "theta": theta
        }
        
        return model
    
    def predict_linear(self, model, X):
        X = np.array(X)
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)
        X_b = np.c_[np.ones((X.shape[0], 1)), X]
        return X_b @ model["theta"]
    
    def logistic_regression(self, X, y, learning_rate=0.01, epochs=1000):
        X = np.array(X)
        y = np.array(y).reshape(-1, 1)
        
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)
        
        m, n = X.shape
        X_b = np.c_[np.ones((m, 1)), X]
        theta = np.zeros((n + 1, 1))
        
        for _ in range(epochs):
            linear = X_b @ theta
            sigmoid = 1 / (1 + np.exp(-np.clip(linear, -500, 500)))
            gradient = X_b.T @ (sigmoid - y) / m
            theta -= learning_rate * gradient
        
        model = {
            "type": "logistic_regression",
            "theta": theta
        }
        
        return model
    
    def predict_logistic(self, model, X):
        X = np.array(X)
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)
        m, n = X.shape
        X_b = np.c_[np.ones((m, 1)), X]
        linear = X_b @ model["theta"]
        sigmoid = 1 / (1 + np.exp(-np.clip(linear, -500, 500)))
        return (sigmoid >= 0.5).astype(int)
    
    def kmeans(self, X, k=3, max_iter=100):
        X = np.array(X)
        m = X.shape[0]
        
        indices = np.random.choice(m, k, replace=False)
        centroids = X[indices]
        
        for _ in range(max_iter):
            distances = np.zeros((m, k))
            for i in range(k):
                distances[:, i] = np.linalg.norm(X - centroids[i], axis=1)
            
            clusters = np.argmin(distances, axis=1)
            
            new_centroids = np.zeros_like(centroids)
            for i in range(k):
                if np.sum(clusters == i) > 0:
                    new_centroids[i] = X[clusters == i].mean(axis=0)
            
            if np.allclose(centroids, new_centroids):
                break
            
            centroids = new_centroids
        
        model = {
            "type": "kmeans",
            "centroids": centroids,
            "k": k
        }
        
        return model
    
    def predict_kmeans(self, model, X):
        X = np.array(X)
        distances = np.zeros((X.shape[0], model["k"]))
        for i in range(model["k"]):
            distances[:, i] = np.linalg.norm(X - model["centroids"][i], axis=1)
        return np.argmin(distances, axis=1)
    
    def decision_tree(self, X, y, max_depth=10):
        model = {
            "type": "decision_tree",
            "max_depth": max_depth,
            "root": self._build_tree(X, y, depth=0)
        }
        return model
    
    def _build_tree(self, X, y, depth):
        if depth >= self.max_depth or len(np.unique(y)) == 1:
            return {"leaf": np.bincount(y).argmax()}
        
        best_split = self._find_best_split(X, y)
        if best_split is None:
            return {"leaf": np.bincount(y).argmax()}
        
        left_mask = X[:, best_split["feature"]] <= best_split["threshold"]
        right_mask = ~left_mask
        
        return {
            "feature": best_split["feature"],
            "threshold": best_split["threshold"],
            "left": self._build_tree(X[left_mask], y[left_mask], depth + 1),
            "right": self._build_tree(X[right_mask], y[right_mask], depth + 1)
        }
    
    def _find_best_split(self, X, y):
        best_gini = float('inf')
        best_split = None
        
        for feature in range(X.shape[1]):
            thresholds = np.unique(X[:, feature])
            
            for threshold in thresholds[:-1]:
                left_mask = X[:, feature] <= threshold
                right_mask = ~left_mask
                
                if np.sum(left_mask) == 0 or np.sum(right_mask) == 0:
                    continue
                
                gini = self._gini(y[left_mask], y[right_mask])
                
                if gini < best_gini:
                    best_gini = gini
                    best_split = {"feature": feature, "threshold": threshold}
        
        return best_split
    
    def _gini(self, y_left, y_right):
        def gini_impurity(y):
            if len(y) == 0:
                return 0
            counts = np.bincount(y)
            probabilities = counts / len(y)
            return 1 - np.sum(probabilities ** 2)
        
        n = len(y_left) + len(y_right)
        return (len(y_left) / n) * gini_impurity(y_left) + (len(y_right) / n) * gini_impurity(y_right)
    
    def random_forest(self, X, y, n_trees=10, max_depth=10):
        trees = []
        m, n = X.shape
        sample_size = int(m * 0.8)
        
        for _ in range(n_trees):
            indices = np.random.choice(m, sample_size, replace=True)
            X_sample = X[indices]
            y_sample = y[indices]
            tree = self.decision_tree(X_sample, y_sample, max_depth)
            trees.append(tree)
        
        model = {
            "type": "random_forest",
            "trees": trees
        }
        
        return model
    
    def naive_bayes(self, X, y):
        classes = np.unique(y)
        model = {
            "type": "naive_bayes",
            "classes": classes,
            "priors": {},
            "means": {},
            "stds": {}
        }
        
        for c in classes:
            X_c = X[y == c]
            model["priors"][c] = len(X_c) / len(X)
            model["means"][c] = X_c.mean(axis=0)
            model["stds"][c] = X_c.std(axis=0) + 1e-10
        
        return model
    
    def predict_naive_bayes(self, model, X):
        predictions = []
        for x in X:
            best_class = None
            best_prob = -float('inf')
            
            for c in model["classes"]:
                log_prob = np.log(model["priors"][c])
                
                for i in range(len(x)):
                    exponent = -(x[i] - model["means"][c][i]) ** 2 / (2 * model["stds"][c][i] ** 2)
                    log_prob += exponent - np.log(model["stds"][c][i] * np.sqrt(2 * np.pi))
                
                if log_prob > best_prob:
                    best_prob = log_prob
                    best_class = c
            
            predictions.append(best_class)
        
        return np.array(predictions)
    
    def save_model(self, model, path):
        with open(path, "wb") as f:
            pickle.dump(model, f)
    
    def load_model(self, path):
        with open(path, "rb") as f:
            return pickle.load(f)


class DataProcessor:
    def __init__(self):
        self.scaler_mean = None
        self.scaler_std = None
    
    def normalize(self, X):
        if self.scaler_mean is None:
            self.scaler_mean = np.mean(X, axis=0)
            self.scaler_std = np.std(X, axis=0) + 1e-10
        
        return (X - self.scaler_mean) / self.scaler_std
    
    def min_max_scale(self, X, min_val=0, max_val=1):
        X_min = np.min(X, axis=0)
        X_max = np.max(X, axis=0)
        X_range = X_max - X_min + 1e-10
        
        return min_val + (X - X_min) / X_range * (max_val - min_val)
    
    def train_test_split(self, X, y, test_size=0.2):
        m = len(X)
        indices = np.random.permutation(m)
        test_count = int(m * test_size)
        
        test_indices = indices[:test_count]
        train_indices = indices[test_count:]
        
        return X[train_indices], X[test_indices], y[train_indices], y[test_indices]
    
    def cross_validate(self, X, y, model_fn, k=5):
        m = len(X)
        indices = np.random.permutation(m)
        fold_size = m // k
        
        scores = []
        
        for i in range(k):
            val_start = i * fold_size
            val_end = (i + 1) * fold_size if i < k - 1 else m
            
            val_indices = indices[val_start:val_end]
            train_indices = np.concatenate([indices[:val_start], indices[val_end:]])
            
            X_train, X_val = X[train_indices], X[val_indices]
            y_train, y_val = y[train_indices], y[val_indices]
            
            model = model_fn(X_train, y_train)
            scores.append(self.score(model, X_val, y_val))
        
        return np.mean(scores), np.std(scores)
    
    def score(self, model, X, y):
        if model["type"] == "linear_regression":
            y_pred = self.predict_linear(model, X)
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            return 1 - ss_res / (ss_tot + 1e-10)
        
        elif model["type"] == "logistic_regression":
            y_pred = self.predict_logistic(model, X)
            return np.mean(y_pred.flatten() == y)
        
        return 0.0
    
    def accuracy(self, y_true, y_pred):
        return np.mean(y_true == y_pred)
    
    def precision(self, y_true, y_pred, positive_class=1):
        tp = np.sum((y_true == positive_class) & (y_pred == positive_class))
        fp = np.sum((y_true != positive_class) & (y_pred == positive_class))
        return tp / (tp + fp + 1e-10)
    
    def recall(self, y_true, y_pred, positive_class=1):
        tp = np.sum((y_true == positive_class) & (y_pred == positive_class))
        fn = np.sum((y_true == positive_class) & (y_pred != positive_class))
        return tp / (tp + fn + 1e-10)
    
    def f1_score(self, y_true, y_pred, positive_class=1):
        p = self.precision(y_true, y_pred, positive_class)
        r = self.recall(y_true, y_pred, positive_class)
        return 2 * p * r / (p + r + 1e-10)
    
    def confusion_matrix(self, y_true, y_pred):
        classes = np.unique(np.concatenate([y_true, y_pred]))
        n = len(classes)
        matrix = np.zeros((n, n), dtype=int)
        
        for i, c1 in enumerate(classes):
            for j, c2 in enumerate(classes):
                matrix[i, j] = np.sum((y_true == c1) & (y_pred == c2))
        
        return matrix


class ImageFeatures:
    def __init__(self):
        self.target_size = (128, 128)
    
    def extract_histogram(self, image):
        if len(image.shape) == 3:
            hist = []
            for i in range(3):
                h = np.histogram(image[:, :, i], bins=256, range=(0, 256))[0]
                hist.extend(h / h.sum())
            return np.array(hist)
        else:
            hist = np.histogram(image, bins=256, range=(0, 256))[0]
            return hist / hist.sum()
    
    def extract_edges(self, image):
        if len(image.shape) == 3:
            image = np.mean(image, axis=2)
        
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        
        edges_x = self._convolve(image, sobel_x)
        edges_y = self._convolve(image, sobel_y)
        
        edges = np.sqrt(edges_x ** 2 + edges_y ** 2)
        return edges / edges.max()
    
    def extract_texture(self, image):
        if len(image.shape) == 3:
            image = np.mean(image, axis=2)
        
        texture = []
        
        for i in range(0, image.shape[0] - 2, 2):
            for j in range(0, image.shape[1] - 2, 2):
                patch = image[i:i+3, j:j+3]
                texture.append(patch.std())
        
        return np.array(texture)
    
    def _convolve(self, image, kernel):
        kh, kw = kernel.shape
        ih, iw = image.shape
        result = np.zeros((ih - kh + 1, iw - kw + 1))
        
        for i in range(result.shape[0]):
            for j in range(result.shape[1]):
                result[i, j] = np.sum(image[i:i+kh, j:j+kw] * kernel)
        
        return result
    
    def extract_color_moments(self, image):
        if len(image.shape) != 3:
            return None
        
        moments = []
        for i in range(3):
            channel = image[:, :, i].flatten()
            mean = np.mean(channel)
            std = np.std(channel)
            skew = np.mean((channel - mean) ** 3) ** (1/3)
            moments.extend([mean, std, skew])
        
        return np.array(moments)
    
    def resize_image(self, image, size):
        h, w = image.shape[:2]
        target_h, target_w = size
        
        result = np.zeros((target_h, target_w, 3) if len(image.shape) == 3 else (target_h, target_w))
        
        h_scale = h / target_h
        w_scale = w / target_w
        
        for i in range(target_h):
            for j in range(target_w):
                src_i = int(i * h_scale)
                src_j = int(j * w_scale)
                src_i = min(src_i, h - 1)
                src_j = min(src_j, w - 1)
                result[i, j] = image[src_i, src_j]
        
        return result.astype(np.uint8)


class NLPProcessor:
    def __init__(self):
        self.vocab = {}
        self.vocab_size = 0
    
    def build_vocab(self, texts, min_freq=2):
        freq = {}
        for text in texts:
            tokens = text.lower().split()
            for token in tokens:
                freq[token] = freq.get(token, 0) + 1
        
        self.vocab = {"<PAD>": 0, "<UNK>": 1}
        idx = 2
        for word, count in freq.items():
            if count >= min_freq:
                self.vocab[word] = idx
                idx += 1
        
        self.vocab_size = len(self.vocab)
        return self.vocab_size
    
    def text_to_sequence(self, text, max_len=None):
        tokens = text.lower().split()
        seq = [self.vocab.get(t, self.vocab["<UNK>"]) for t in tokens]
        
        if max_len:
            if len(seq) > max_len:
                seq = seq[:max_len]
            else:
                seq = seq + [self.vocab["<PAD>"]] * (max_len - len(seq))
        
        return seq
    
    def sequence_to_text(self, seq):
        idx_to_word = {v: k for k, v in self.vocab.items()}
        return [idx_to_word.get(i, "<UNK>") for i in seq]
    
    def ngrams(self, text, n=2):
        tokens = text.lower().split()
        return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
    
    def sentiment_score(self, text):
        positive = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'best', 'awesome', 'fantastic', 'happy']
        negative = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'poor', 'sad', 'angry', 'disappointed']
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive if w in text_lower)
        neg_count = sum(1 for w in negative if w in text_lower)
        
        score = (pos_count - neg_count) / (pos_count + neg_count + 1)
        return score
    
    def extract_entities(self, text):
        import re
        entities = []
        
        patterns = {
            'email': r'[\w.-]+@[\w.-]+\.\w+',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'url': r'https?://\S+',
            'date': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            'money': r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
            'hashtag': r'#\w+',
            'mention': r'@\w+'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                entities.append({'type': entity_type, 'value': match})
        
        return entities


class FeatureEngineering:
    def __init__(self):
        pass
    
    def polynomial_features(self, X, degree=2):
        m, n = X.shape
        poly_features = [np.ones(m)]
        
        for d in range(1, degree + 1):
            for i in range(n):
                poly_features.append(X[:, i] ** d)
        
        for d in range(2, degree + 1):
            for i in range(n):
                for j in range(i + 1, n):
                    poly_features.append((X[:, i] * X[:, j]) ** (d - 1))
        
        return np.column_stack(poly_features)
    
    def interaction_features(self, X, feature_names=None):
        m, n = X.shape
        interactions = []
        
        for i in range(n):
            for j in range(i + 1, n):
                interactions.append(X[:, i] * X[:, j])
        
        if feature_names and len(feature_names) == n:
            names = []
            for i in range(n):
                for j in range(i + 1, n):
                    names.append(f"{feature_names[i]}_x_{feature_names[j]}")
            return np.column_stack(interactions), names
        
        return np.column_stack(interactions)
    
    def binning(self, X, n_bins=5, strategy='uniform'):
        if strategy == 'uniform':
            bins = np.linspace(X.min(), X.max(), n_bins + 1)
        else:
            bins = np.percentile(X, [i * 100 / n_bins for i in range(n_bins + 1)])
        
        return np.digitize(X, bins[1:-1])
    
    def one_hot_encode(self, X, num_classes=None):
        if num_classes is None:
            num_classes = int(X.max()) + 1
        
        m = len(X)
        one_hot = np.zeros((m, num_classes))
        one_hot[np.arange(m), X.astype(int)] = 1
        
        return one_hot
    
    def target_encoding(self, X, y, smoothing=1):
        categories = np.unique(X)
        global_mean = np.mean(y)
        
        encoded = []
        for cat in X:
            mask = X == cat
            cat_mean = np.mean(y[mask])
            n = np.sum(mask)
            encoded_val = (cat_mean * n + global_mean * smoothing) / (n + smoothing)
            encoded.append(encoded_val)
        
        return np.array(encoded)


class EnsembleMethods:
    def __init__(self):
        self.models = []
        self.model_type = None
    
    def bagging(self, X, y, base_model_fn, n_models=10, sample_ratio=0.8):
        m = len(X)
        sample_size = int(m * sample_ratio)
        
        models = []
        for _ in range(n_models):
            indices = np.random.choice(m, sample_size, replace=True)
            X_sample, y_sample = X[indices], y[indices]
            model = base_model_fn(X_sample, y_sample)
            models.append(model)
        
        self.models = models
        return models
    
    def voting_classify(self, predictions):
        votes = np.sum(predictions, axis=0)
        return (votes >= len(predictions) / 2).astype(int)
    
    def voting_regress(self, predictions):
        return np.mean(predictions, axis=0)
    
    def stacking(self, X_train, y_train, X_val, base_model_fns, meta_model_fn):
        meta_features = []
        
        for model_fn in base_model_fns:
            model = model_fn(X_train, y_train)
            preds = self._get_predictions(model, X_val)
            meta_features.append(preds)
        
        meta_X = np.column_stack(meta_features)
        meta_model = meta_model_fn(meta_X, y_train)
        
        return meta_model
    
    def _get_predictions(self, model, X):
        if model.get("type") == "linear_regression":
            return self.predict_linear(model, X)
        elif model.get("type") == "logistic_regression":
            return self.predict_logistic(model, X)
        return np.zeros(len(X))
    
    def predict_linear(self, model, X):
        X = np.array(X)
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)
        X_b = np.c_[np.ones((X.shape[0], 1)), X]
        return X_b @ model["theta"]
    
    def predict_logistic(self, model, X):
        X = np.array(X)
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)
        m, n = X.shape
        X_b = np.c_[np.ones((m, 1)), X]
        linear = X_b @ model["theta"]
        sigmoid = 1 / (1 + np.exp(-np.clip(linear, -500, 500)))
        return (sigmoid >= 0.5).astype(int)