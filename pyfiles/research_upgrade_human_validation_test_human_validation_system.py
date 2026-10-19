"""
test_human_validation_system.py
Comprehensive unit and integration test suite for the HinglishEval human evaluation platform (1,000-response study).
Tests:
1. Assignment Manifest Integrity (1,000 total, 500 each, 125 per model each, 0 overlap, category balance)
2. Token Authentication & Role Isolation
3. Item Blinding (Zero Model Identity Leakage)
4. Score Boundary Validation (1 to 5 integers)
5. Access Control (Cross-Annotator Submission Prevention)
6. Atomic Upsert & Audit Trail Recording
7. Next-Unanswered Index Navigation
8. Dataset Combination & Validation Export (combined_human_ratings_1000.csv)
9. Offline Bundle Export and Import
"""

import os
import sys
import json
import sqlite3
import pandas as pd
import unittest

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import db
import bundle_manager
import combine_and_validate_ratings

TEST_DB_PATH = os.path.join(BASE_DIR, "test_ratings_isolated.db")

class TestHumanValidationSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.orig_db_path = db.DB_PATH
        cls.orig_combine_db_path = getattr(combine_and_validate_ratings, "DB_PATH", db.DB_PATH)
        cls.orig_out_combined = combine_and_validate_ratings.OUTPUT_COMBINED_CSV
        cls.orig_out_a = combine_and_validate_ratings.OUTPUT_ANNOTATOR_A_CSV
        cls.orig_out_b = combine_and_validate_ratings.OUTPUT_ANNOTATOR_B_CSV
        cls.orig_out_report = combine_and_validate_ratings.OUTPUT_REPORT_MD

        db.DB_PATH = TEST_DB_PATH
        combine_and_validate_ratings.DB_PATH = TEST_DB_PATH
        combine_and_validate_ratings.OUTPUT_COMBINED_CSV = os.path.join(BASE_DIR, "test_combined_1000.csv")
        combine_and_validate_ratings.OUTPUT_ANNOTATOR_A_CSV = os.path.join(BASE_DIR, "test_annotator_A.csv")
        combine_and_validate_ratings.OUTPUT_ANNOTATOR_B_CSV = os.path.join(BASE_DIR, "test_annotator_B.csv")
        combine_and_validate_ratings.OUTPUT_REPORT_MD = os.path.join(BASE_DIR, "test_report.md")

        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass
        db.init_db()

    @classmethod
    def tearDownClass(cls):
        db.DB_PATH = cls.orig_db_path
        combine_and_validate_ratings.DB_PATH = cls.orig_combine_db_path
        combine_and_validate_ratings.OUTPUT_COMBINED_CSV = cls.orig_out_combined
        combine_and_validate_ratings.OUTPUT_ANNOTATOR_A_CSV = cls.orig_out_a
        combine_and_validate_ratings.OUTPUT_ANNOTATOR_B_CSV = cls.orig_out_b
        combine_and_validate_ratings.OUTPUT_REPORT_MD = cls.orig_out_report

        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass
        for f in ["test_combined_1000.csv", "test_annotator_A.csv", "test_annotator_B.csv", "test_report.md", "test_bundle_b.json"]:
            p = os.path.join(BASE_DIR, f)
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    def test_01_manifest_counts_and_balance(self):
        manifest_path = os.path.join(BASE_DIR, "assignment_manifest.csv")
        self.assertTrue(os.path.exists(manifest_path), "Manifest file must exist")
        df = pd.read_csv(manifest_path)

        self.assertEqual(len(df), 1000, "Manifest must contain exactly 1,000 total responses")

        df_a = df[df["annotator_id"] == "annotator_a"]
        df_b = df[df["annotator_id"] == "annotator_b"]

        self.assertEqual(len(df_a), 500, "Annotator A must have exactly 500 assignments")
        self.assertEqual(len(df_b), 500, "Annotator B must have exactly 500 assignments")

        set_a = set(df_a["response_id"])
        set_b = set(df_b["response_id"])

        overlap = set_a.intersection(set_b)
        self.assertEqual(len(overlap), 0, "Assignment overlap must be strictly 0")
        self.assertEqual(len(set_a.union(set_b)), 1000, "Union of assignments must cover 1,000 unique responses")

        # Verify 125 per model for each annotator and 250 total
        models = ["HingGPT", "Phi-3.5-mini", "Qwen2.5-3B", "Qwen2.5-7B"]
        for m in models:
            self.assertEqual((df_a["model"] == m).sum(), 125, f"Annotator A must have 125 of {m}")
            self.assertEqual((df_b["model"] == m).sum(), 125, f"Annotator B must have 125 of {m}")
            self.assertEqual((df["model"] == m).sum(), 250, f"Combined manifest must have 250 of {m}")

        # Verify category presence in both partitions
        self.assertGreaterEqual(len(df_a["category"].unique()), 7)
        self.assertGreaterEqual(len(df_b["category"].unique()), 7)

    def test_02_authentication_and_tokens(self):
        user_a = db.authenticate_token("eval_a_lead_2026")
        self.assertIsNotNone(user_a)
        self.assertEqual(user_a["annotator_id"], "annotator_a")

        user_b = db.authenticate_token("eval_b_partner_2026")
        self.assertIsNotNone(user_b)
        self.assertEqual(user_b["annotator_id"], "annotator_b")

        admin = db.authenticate_token("admin_hinglish_eval_master")
        self.assertIsNotNone(admin)
        self.assertEqual(admin["role"], "admin")

        self.assertIsNone(db.authenticate_token("invalid_random_token"))
        self.assertIsNone(db.authenticate_token(""))

    def test_03_item_blinding_safeguards(self):
        item = db.get_assignment_item("annotator_a", 1)
        self.assertIsNotNone(item)
        self.assertEqual(item["item_index"], 1)
        self.assertIn("prompt", item)
        self.assertIn("response", item)
        self.assertIn("category", item)

        # Critical: Model architecture name must NOT be leaked in client payload!
        self.assertNotIn("model", item, "Item payload must conceal model architecture name")

    def test_04_score_bounds_and_validation(self):
        # Invalid score 0
        ok, msg, _ = db.save_rating(
            annotator_id="annotator_a",
            assignment_id="A_0001",
            fluency=0, code_mixing_naturalness=4, hindi_grammar=4,
            prompt_adherence=4, spelling_consistency=4, overall=4
        )
        self.assertFalse(ok)
        self.assertIn("Invalid score", msg)

        # Invalid score 6
        ok, msg, _ = db.save_rating(
            annotator_id="annotator_a",
            assignment_id="A_0001",
            fluency=6, code_mixing_naturalness=4, hindi_grammar=4,
            prompt_adherence=4, spelling_consistency=4, overall=4
        )
        self.assertFalse(ok)
        self.assertIn("Invalid score", msg)

    def test_05_cross_annotator_access_control(self):
        # Annotator A attempts to rate Annotator B's assignment B_0001
        ok, msg, _ = db.save_rating(
            annotator_id="annotator_a",
            assignment_id="B_0001",
            fluency=4, code_mixing_naturalness=4, hindi_grammar=4,
            prompt_adherence=4, spelling_consistency=4, overall=4
        )
        self.assertFalse(ok, "Annotator A must not be permitted to submit ratings for Annotator B")
        self.assertIn("Access Denied", msg)

    def test_06_atomic_rating_save_and_update(self):
        # Valid rating submission
        ok, msg, prog = db.save_rating(
            annotator_id="annotator_a",
            assignment_id="A_0001",
            fluency=4, code_mixing_naturalness=5, hindi_grammar=4,
            prompt_adherence=5, spelling_consistency=4, overall=5,
            notes="Clean colloquial mixing"
        )
        self.assertTrue(ok)
        self.assertEqual(prog["total_completed"], 1)

        # Verify rating can be retrieved
        item = db.get_assignment_item("annotator_a", 1)
        self.assertTrue(item["is_rated"])
        self.assertEqual(item["current_ratings"]["code_mixing_naturalness"], 5)
        self.assertEqual(item["current_ratings"]["notes"], "Clean colloquial mixing")

        # Update rating (correction)
        ok_up, msg_up, _ = db.save_rating(
            annotator_id="annotator_a",
            assignment_id="A_0001",
            fluency=5, code_mixing_naturalness=5, hindi_grammar=5,
            prompt_adherence=5, spelling_consistency=5, overall=5,
            notes="Updated to perfect 5"
        )
        self.assertTrue(ok_up)

        # Verify audit trail
        conn = db.get_connection()
        cur = conn.execute("SELECT * FROM ratings_audit_trail WHERE annotator_id = 'annotator_a' ORDER BY audit_id DESC;")
        logs = cur.fetchall()
        conn.close()
        self.assertGreaterEqual(len(logs), 2, "Audit trail must log both insert and update")

    def test_07_next_unanswered_navigation(self):
        # Since item 1 is rated, next unanswered should be 2
        next_idx = db.get_next_unanswered_index("annotator_a", current_index=1)
        self.assertEqual(next_idx, 2, "Should jump to item 2 since item 1 is completed")

    def test_08_combine_and_validate_pipeline(self):
        res = combine_and_validate_ratings.combine_and_validate()
        self.assertEqual(res["total_manifest"], 1000)
        self.assertEqual(res["annotator_a_total"], 500)
        self.assertEqual(res["annotator_b_total"], 500)
        self.assertGreaterEqual(res["total_completed"], 1)

        combined_csv = os.path.join(BASE_DIR, "combined_human_ratings_1000.csv")
        report_md = os.path.join(BASE_DIR, "human_validation_report.md")
        self.assertTrue(os.path.exists(combined_csv))
        self.assertTrue(os.path.exists(report_md))

    def test_09_offline_bundle_export_and_import(self):
        # Rate an item for Annotator B
        ok, msg, _ = db.save_rating(
            annotator_id="annotator_b",
            assignment_id="B_0001",
            fluency=3, code_mixing_naturalness=3, hindi_grammar=3,
            prompt_adherence=4, spelling_consistency=3, overall=3,
            notes="Test bundle note"
        )
        self.assertTrue(ok)

        # Export bundle
        bundle_file = os.path.join(BASE_DIR, "test_bundle_b.json")
        bundle_manager.export_bundle("annotator_b", bundle_file)
        self.assertTrue(os.path.exists(bundle_file))

        # Test re-import
        imp_res = bundle_manager.import_bundle(bundle_file)
        self.assertGreaterEqual(imp_res["imported_count"] + imp_res["updated_count"], 1)

        if os.path.exists(bundle_file):
            os.remove(bundle_file)

if __name__ == "__main__":
    unittest.main()
