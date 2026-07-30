"""
Query Preprocessing Pipeline for Typesense Search.

This module implements intelligent query preprocessing to improve search quality:
- Unicode normalization (accents, special characters)
- Stop-word removal (configurable per language)
- Token normalization
- Typo detection and correction hints
- Whitespace and punctuation cleanup
"""

import logging
import re
import unicodedata

logger = logging.getLogger(__name__)


# French stop-words - common words that don't contribute to search relevance
FRENCH_STOP_WORDS = {
    # Articles
    "le",
    "la",
    "les",
    "un",
    "une",
    "des",
    "du",
    "de",
    "au",
    "aux",
    # Conjonctions
    "et",
    "ou",
    "mais",
    "donc",
    "or",
    "ni",
    "car",
    # Prepositions
    "à",
    "dans",
    "sur",
    "pour",
    "par",
    "en",
    "avec",
    "sans",
    "sous",
    "entre",
    "vers",
    "chez",
    "contre",
    "pendant",
    "depuis",
    # Pronoms
    "je",
    "tu",
    "il",
    "elle",
    "on",
    "nous",
    "vous",
    "ils",
    "elles",
    "ce",
    "cet",
    "cette",
    "ces",
    "mon",
    "ma",
    "mes",
    "ton",
    "ta",
    "tes",
    "son",
    "sa",
    "ses",
    "notre",
    "nos",
    "votre",
    "vos",
    "leur",
    "leurs",
    "qui",
    "que",
    "quoi",
    "dont",
    "où",
    "lequel",
    "laquelle",
    "lesquels",
    # Adverbes courants
    "ne",
    "pas",
    "plus",
    "moins",
    "très",
    "trop",
    "bien",
    "mal",
    "encore",
    "aussi",
    "si",
    "quand",
    "comment",
    "pourquoi",
    # Autres
    "est",
    "sont",
    "a",
    "ont",
    "être",
    "avoir",
    "fait",
    "faire",
    "tout",
    "tous",
    "toute",
    "toutes",
    "autre",
    "autres",
    "même",
    "se",
    "s'",
    "c'",
    "d'",
    "n'",
    "qu'",
    "l'",
    "j'",
}

# English stop-words
ENGLISH_STOP_WORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "by",
    "from",
    "as",
    "is",
    "was",
    "are",
    "were",
    "been",
    "be",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "must",
    "shall",
    "can",
    "need",
    "it",
    "its",
    "this",
    "that",
    "these",
    "those",
    "he",
    "she",
    "they",
    "we",
    "you",
    "i",
    "me",
    "him",
    "her",
    "us",
    "them",
    "my",
    "your",
    "his",
    "our",
    "their",
    "what",
    "which",
    "who",
    "whom",
    "where",
    "when",
    "why",
    "how",
    "all",
    "each",
    "every",
    "both",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "not",
    "only",
    "same",
    "so",
    "than",
    "too",
    "very",
    "just",
    "also",
    "now",
    "here",
    "there",
}

# Academic domain-specific terms to preserve (never remove as stop-words)
ACADEMIC_PRESERVE_WORDS = {
    "algorithme",
    "base",
    "bases",
    "données",
    "data",
    "réseau",
    "reseaux",
    "network",
    "système",
    "systeme",
    "system",
    "systems",
    "programmation",
    "programming",
    "java",
    "python",
    "sql",
    "html",
    "css",
    "javascript",
    "automate",
    "automates",
    "instrumentation",
    "mesure",
    "mesures",
    "mathématiques",
    "mathematique",
    "math",
    "maths",
    "physique",
    "chimie",
    "biologie",
    "informatique",
    "computer",
    "électronique",
    "electronique",
    "electronic",
    "télécommunication",
    "telecommunication",
}


class QueryPreprocessor:
    """
    Preprocesses user search queries before sending to Typesense.

    The preprocessing pipeline includes:
    1. Unicode normalization (NFKC)
    2. Accent removal for fuzzy matching
    3. Lowercase normalization
    4. Punctuation cleanup
    5. Stop-word removal
    6. Duplicate whitespace removal
    7. Token analysis for fuzzy search hints
    """

    def __init__(
        self,
        remove_stop_words: bool = True,
        min_token_length: int = 2,
        preserve_academic_terms: bool = True,
    ):
        self.remove_stop_words = remove_stop_words
        self.min_token_length = min_token_length
        self.preserve_academic_terms = preserve_academic_terms
        self.stop_words = FRENCH_STOP_WORDS | ENGLISH_STOP_WORDS

    def preprocess(self, query: str) -> tuple[str, dict]:
        """
        Preprocess a search query and return the normalized query
        along with metadata about the preprocessing.

        Returns:
            Tuple of (normalized_query, metadata_dict)
        """
        if not query or not query.strip():
            return "", {"original": "", "tokens_removed": 0}

        original_query = query
        metadata = {
            "original": original_query,
            "tokens_removed": 0,
            "normalized_tokens": [],
            "removed_tokens": [],
        }

        # Step 1: Unicode normalization
        query = self._normalize_unicode(query)

        # Step 2: Lowercase
        query = query.lower()

        # Step 3: Remove punctuation but preserve alphanumeric and spaces
        query = self._clean_punctuation(query)

        # Step 4: Split into tokens
        tokens = query.split()

        # Step 5: Remove stop-words and short tokens
        filtered_tokens = []
        for token in tokens:
            if self._should_remove_token(token):
                metadata["removed_tokens"].append(token)
                metadata["tokens_removed"] += 1
            else:
                filtered_tokens.append(token)
                metadata["normalized_tokens"].append(token)

        # Step 6: Join back
        normalized_query = " ".join(filtered_tokens)

        return normalized_query, metadata

    def _normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters: NFKC then remove accents."""
        text = unicodedata.normalize("NFKC", text)
        return self._remove_accents(text)

    def _remove_accents(self, text: str) -> str:
        """Remove combining diacritical marks (accents) from text."""
        nfkd = unicodedata.normalize("NFKD", text)
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    def _clean_punctuation(self, text: str) -> str:
        """Remove punctuation and normalize whitespace."""
        # Replace common punctuation with space
        text = re.sub(r"[^\w\s\-]", " ", text)
        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _should_remove_token(self, token: str) -> bool:
        """Determine if a token should be removed."""
        # Remove very short tokens (but preserve numbers)
        if len(token) < self.min_token_length and not token.isdigit():
            return True

        # Preserve academic terms
        if self.preserve_academic_terms and token.lower() in ACADEMIC_PRESERVE_WORDS:
            return False

        # Check stop words
        return bool(self.remove_stop_words and token.lower() in self.stop_words)

    def suggest_typos(self, token: str) -> list[str]:
        """
        Generate typo-tolerant variants of a token.
        Useful for 'Did you mean...' suggestions.
        """
        suggestions = []

        # Common typos patterns
        # Double letters: "instrumentaation" -> "instrumentation"
        if re.search(r"(\w)\1\1", token):
            corrected = re.sub(r"(\w)\1\1", r"\1\1", token)
            suggestions.append(corrected)

        # Missing double letters: "intrumentation" -> "instrumentation"
        # This is complex, would need a dictionary

        # i/y confusion: "phisyque" -> "physique"
        token_iy = token.replace("i", "y").replace("y", "i")
        if token_iy != token:
            suggestions.append(token_iy)

        return suggestions


class TypoAnalyzer:
    """
    Analyzes tokens to determine optimal typo tolerance settings.

    Typesense's num_typos parameter should be adjusted based on token length:
    - Short tokens (3-4 chars): 1 typo max
    - Medium tokens (5-7 chars): 2 typos
    - Long tokens (8+ chars): 2-3 typos
    """

    @staticmethod
    def get_num_typos_for_token(token: str) -> int:
        """Calculate optimal num_typos for a given token."""
        length = len(token)
        if length <= 4:
            return 1
        elif length <= 7:
            return 2
        else:
            return 2  # Typesense max is 2

    @staticmethod
    def analyze_query(query: str) -> dict:
        """
        Analyze a full query and return optimal typo settings.

        Returns:
            Dict with 'num_typos' (min across tokens), 'drop_tokens_threshold', etc.
        """
        tokens = query.split()
        if not tokens:
            return {"num_typos": 0, "drop_tokens_threshold": 0}

        # Use the minimum num_typos across all tokens to be safe
        num_typos_values = [TypoAnalyzer.get_num_typos_for_token(t) for t in tokens]
        min_typos = min(num_typos_values) if num_typos_values else 2

        # Calculate drop_tokens_threshold based on number of tokens
        # More tokens = higher threshold (allow more to be dropped)
        token_count = len(tokens)
        if token_count <= 2:
            drop_threshold = 0  # Don't drop any tokens for short queries
        elif token_count <= 4:
            drop_threshold = token_count - 2  # Allow dropping 1-2 tokens
        else:
            drop_threshold = token_count // 2  # Allow dropping up to half

        return {
            "num_typos": min_typos,
            "drop_tokens_threshold": drop_threshold,
            "token_count": token_count,
            "avg_token_length": (
                sum(len(t) for t in tokens) / token_count if tokens else 0
            ),
        }
