"""Unit tests for query preprocessing and typo analysis."""

from django.test import SimpleTestCase

from services.search.preprocessing import QueryPreprocessor, TypoAnalyzer


class QueryPreprocessorTests(SimpleTestCase):
    """Test the query normalization pipeline."""

    def setUp(self):
        self.preprocessor = QueryPreprocessor(
            remove_stop_words=True,
            min_token_length=2,
            preserve_academic_terms=True,
        )

    # ----------------------------------------------------------------
    # Stop-word removal
    # ----------------------------------------------------------------

    def test_removes_french_article_et(self):
        normalized, meta = self.preprocessor.preprocess("ET INSTRUMENTATIiO")
        self.assertNotIn("et", normalized.split())
        self.assertIn("instrumentatiio", normalized)
        self.assertIn("et", meta["removed_tokens"])

    def test_removes_french_articles_le_la_les(self):
        normalized, _meta = self.preprocessor.preprocess("le réseau informatique")
        self.assertIn("reseau", normalized)
        self.assertIn("informatique", normalized)
        self.assertNotIn("le", normalized.split())

    def test_removes_multiple_stop_words(self):
        normalized, _meta = self.preprocessor.preprocess(
            "Algorithmique ET Structures de Données"
        )
        tokens = normalized.split()
        self.assertIn("algorithmique", tokens)
        self.assertIn("structures", tokens)
        self.assertIn("donnees", tokens)
        self.assertNotIn("et", tokens)
        self.assertNotIn("de", tokens)

    def test_preserves_academic_terms(self):
        """'automates' is in ACADEMIC_PRESERVE_WORDS and must survive."""
        normalized, _meta = self.preprocessor.preprocess("AUTOMATESs")
        self.assertIn("automatess", normalized)

    def test_removes_short_tokens_below_min_length(self):
        preprocessor = QueryPreprocessor(min_token_length=3)
        normalized, _meta = preprocessor.preprocess("a bc def")
        # "a" (len 1) and "bc" (len 2) should be removed
        tokens = normalized.split()
        self.assertNotIn("a", tokens)
        self.assertNotIn("bc", tokens)

    # ----------------------------------------------------------------
    # Accent folding
    # ----------------------------------------------------------------

    def test_folds_accents(self):
        normalized, _ = self.preprocessor.preprocess("réseau électronique")
        self.assertIn("reseau", normalized)
        self.assertIn("electronique", normalized)

    def test_folds_cedilla(self):
        normalized, _ = self.preprocessor.preprocess("façon")
        self.assertIn("facon", normalized)

    # ----------------------------------------------------------------
    # Edge cases
    # ----------------------------------------------------------------

    def test_empty_query(self):
        normalized, meta = self.preprocessor.preprocess("")
        self.assertEqual(normalized, "")
        self.assertEqual(meta["original"], "")

    def test_whitespace_only(self):
        normalized, _ = self.preprocessor.preprocess("   ")
        self.assertEqual(normalized, "")

    def test_numeric_tokens_preserved(self):
        normalized, _ = self.preprocessor.preprocess("math 101")
        self.assertIn("101", normalized.split())

    def test_metadata_tracks_removed_tokens(self):
        _, meta = self.preprocessor.preprocess("le ET un test")
        self.assertGreater(meta["tokens_removed"], 0)
        self.assertEqual(len(meta["normalized_tokens"]), 1)  # only "test"


class TypoAnalyzerTests(SimpleTestCase):
    """Test the typo-tolerance analysis."""

    def test_short_token_one_typo(self):
        self.assertEqual(TypoAnalyzer.get_num_typos_for_token("abc"), 1)
        self.assertEqual(TypoAnalyzer.get_num_typos_for_token("word"), 1)

    def test_medium_token_two_typos(self):
        self.assertEqual(TypoAnalyzer.get_num_typos_for_token("hello"), 2)
        self.assertEqual(TypoAnalyzer.get_num_typos_for_token("example"), 2)

    def test_long_token_two_typos_max(self):
        self.assertEqual(
            TypoAnalyzer.get_num_typos_for_token("instrumentation"),
            2,
        )

    def test_analyze_query_single_token(self):
        analysis = TypoAnalyzer.analyze_query("automatess")
        self.assertEqual(analysis["num_typos"], 2)
        self.assertEqual(analysis["token_count"], 1)
        self.assertGreater(analysis["avg_token_length"], 0)

    def test_analyze_query_multi_token(self):
        analysis = TypoAnalyzer.analyze_query("administration amenagemen")
        self.assertEqual(analysis["token_count"], 2)
        # drop_tokens_threshold for 2 tokens = 0
        self.assertEqual(analysis["drop_tokens_threshold"], 0)

    def test_analyze_query_many_tokens(self):
        analysis = TypoAnalyzer.analyze_query("un deux trois quatre cinq")
        self.assertEqual(analysis["token_count"], 5)
        # For >4 tokens: token_count // 2 = 2
        self.assertEqual(analysis["drop_tokens_threshold"], 2)

    def test_analyze_empty_query(self):
        analysis = TypoAnalyzer.analyze_query("")
        self.assertEqual(analysis["num_typos"], 0)


class TypoDistanceTests(SimpleTestCase):
    """Tests for the Levenshtein-based typo-distance helpers in SearchService."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from services.search.service import SearchService

        cls.service = SearchService

    def test_exact_match_zero_distance(self):
        self.assertTrue(self.service._within_typo_distance("instrument", "instrument"))

    def test_one_char_difference(self):
        self.assertTrue(self.service._within_typo_distance("automatess", "automates"))

    def test_two_char_difference_long_word(self):
        # "instrumentatiio" → "instrumentation": 2 diffs (extra 'i', missing 'n')
        self.assertTrue(
            self.service._within_typo_distance("instrumentatiio", "instrumentation")
        )

    def test_three_char_difference_fails(self):
        self.assertFalse(
            self.service._within_typo_distance("automatessss", "automates")
        )

    def test_length_difference_too_large(self):
        self.assertFalse(self.service._within_typo_distance("a", "automates"))

    def test_levenshtein_distance_known(self):
        dist = self.service._levenshtein_distance("kitten", "sitting", 10)
        self.assertEqual(dist, 3)

    def test_levenshtein_stops_at_threshold(self):
        dist = self.service._levenshtein_distance("abcdef", "xyz", 2)
        self.assertGreater(dist, 2)
