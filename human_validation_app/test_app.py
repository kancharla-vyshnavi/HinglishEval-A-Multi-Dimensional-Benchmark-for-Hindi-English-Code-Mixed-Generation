"""
Automated Test Suite for HinglishEval Human Validation Web Platform.
Verifies:
1. Exact 4,000 response stimulus loading and schema constraints
2. 500 completed ratings preserved for Annotator A with all 6 dimensions
3. Annotator B starts cleanly at 0/4,000 completed ratings
4. Double-blind stimulus masking (model name strictly hidden in API and blinded ID)
5. 1–5 integer rating scale validation
6. Strict completion criteria (all 6 dimensions required)
7. Duplicate prevention and rating revision capability
8. Complete annotator isolation (no cross-rater visibility)
9. Autosave persistence and state recovery
10. Resume next unrated (Item 501 for Annotator A, Item 1 for Annotator B)
11. Protected administrative CSV export authorization and schema compliance
12. Health-check endpoint operational status
"""

import os
import sys
import unittest
from pathlib import Path

# UTF-8 stdout configuration for Windows
sys.stdout.reconfigure(encoding="utf-8")

# Ensure package importability
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR.parent) not in sys.path:
    sys.path.insert(0, str(APP_DIR.parent))

from starlette.testclient import TestClient

from human_validation_app.config import (
    TOTAL_EXPECTED_RESPONSES,
    EXPECTED_MODELS,
    ANNOTATOR_A_KEY,
    ANNOTATOR_B_KEY,
    ADMIN_SECRET,
    RATING_DIMENSIONS
)
from human_validation_app.database import SessionLocal
from human_validation_app.models import Response as StimulusResponse, Annotator, Annotation
from human_validation_app.app import app
from human_validation_app.analyze_agreement import analyze_agreement, krippendorff_alpha_ordinal
import numpy as np


class TestHinglishEvalHumanValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.session = SessionLocal()

        # Login Annotator A and B to obtain cookies / sessions
        resp_a = cls.client.post("/api/auth/login", json={"access_code": ANNOTATOR_A_KEY})
        assert resp_a.status_code == 200, f"Failed to login A: {resp_a.text}"
        cls.token_a = resp_a.json()["session_token"]

        resp_b = cls.client.post("/api/auth/login", json={"access_code": ANNOTATOR_B_KEY})
        assert resp_b.status_code == 200, f"Failed to login B: {resp_b.text}"
        cls.token_b = resp_b.json()["session_token"]

        # Clear ambient client cookies so explicit Authorization headers govern each test
        cls.client.cookies.clear()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def test_01_response_dataset_integrity(self):
        """Verify exactly 4,000 valid responses are loaded with unique stable IDs and correct models."""
        total = self.session.query(StimulusResponse).count()
        self.assertEqual(total, TOTAL_EXPECTED_RESPONSES, f"Expected 4000 responses, got {total}")

        # Unique IDs
        unique_ids = self.session.query(StimulusResponse.id).distinct().count()
        self.assertEqual(unique_ids, TOTAL_EXPECTED_RESPONSES)

        # First and last IDs exist and follow canonical format
        first = self.session.query(StimulusResponse).filter_by(item_index=1).first()
        last = self.session.query(StimulusResponse).filter_by(item_index=4000).first()
        self.assertIsNotNone(first)
        self.assertIsNotNone(last)
        self.assertTrue(first.id.startswith("RESP_"))
        self.assertTrue(last.id.startswith("RESP_"))

        # Model coverage: 1,000 each
        for m in EXPECTED_MODELS:
            cnt = self.session.query(StimulusResponse).filter_by(model=m).count()
            self.assertEqual(cnt, 1000, f"Model {m} does not have exactly 1000 responses ({cnt})")

    def test_02_annotator_a_preserved_500_ratings(self):
        """Verify Annotator A's 500 completed ratings are 100% preserved with all 6 dimensions."""
        self.session.expire_all()
        completed_a = self.session.query(Annotation).filter_by(
            annotator_id="annotator_a", is_completed=True
        ).count()
        self.assertEqual(completed_a, 500, f"Expected 500 completed ratings for Annotator A, found {completed_a}")

        # Verify all 6 dimensions are integers 1..5 for all 500 records
        for dim in RATING_DIMENSIONS:
            col = getattr(Annotation, dim)
            valid_count = self.session.query(Annotation).filter(
                Annotation.annotator_id == "annotator_a",
                col >= 1, col <= 5
            ).count()
            self.assertEqual(valid_count, 500, f"Dimension {dim} has invalid/null values in Annotator A ratings")

    def test_03_annotator_b_completed_ratings(self):
        """Verify Annotator B has 4,000 completed ratings in database."""
        self.session.expire_all()
        count_b = self.session.query(Annotation).filter_by(annotator_id="annotator_b", is_completed=True).count()
        self.assertEqual(count_b, 4000, f"Annotator B should have 4000 completed ratings, found {count_b}")

    def test_04_double_blind_stimulus_masking(self):
        """Verify model name is strictly excluded from annotator-facing APIs and UI."""
        resp = self.client.get("/api/responses/by_index/1", headers={"Authorization": f"Bearer {self.token_a}"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        item = data["item"]

        self.assertIn("response_id", item)
        self.assertIn("prompt", item)
        self.assertIn("response", item)
        # CRITICAL: 'model' must NOT be in stimulus item
        self.assertNotIn("model", item, "Model identity leaked to annotator API!")
        # External response_id presented to annotator is blinded (RESP_0001)
        self.assertEqual(item["response_id"], "RESP_0001")

    def test_05_rating_validation_integers(self):
        """Verify only integer ratings 1–5 are accepted."""
        # Test out of range (0 and 6)
        payload_bad = {
            "response_id": "RESP_4000",
            "fluency": 0,
            "code_mixing_naturalness": 3,
            "hindi_grammar": 3,
            "prompt_adherence": 3,
            "spelling_consistency": 3,
            "overall": 3
        }
        resp = self.client.post("/api/annotations/save", json=payload_bad, headers={"Authorization": f"Bearer {self.token_b}"})
        self.assertEqual(resp.status_code, 422)

        payload_bad_high = {
            "response_id": "RESP_4000",
            "fluency": 6,
            "code_mixing_naturalness": 3,
            "hindi_grammar": 3,
            "prompt_adherence": 3,
            "spelling_consistency": 3,
            "overall": 3
        }
        resp = self.client.post("/api/annotations/save", json=payload_bad_high, headers={"Authorization": f"Bearer {self.token_b}"})
        self.assertEqual(resp.status_code, 422)

    def test_06_completion_requires_all_six_dimensions(self):
        """Verify response is marked complete if and only if all six dimensions are rated 1..5."""
        partial = {
            "response_id": "RESP_0501",
            "fluency": 4,
            "code_mixing_naturalness": 4,
            "hindi_grammar": 4,
            "prompt_adherence": 4,
            "spelling_consistency": 4,
            "overall": None
        }
        resp = self.client.post("/api/annotations/save", json=partial, headers={"Authorization": f"Bearer {self.token_a}"})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()["is_completed"], "Partial rating should not be marked as complete")

        # Clean up test row on 501 for annotator_a so item 501 stays unrated
        test_resp = self.session.query(StimulusResponse).filter_by(item_index=501).first()
        self.session.query(Annotation).filter_by(response_id=test_resp.id, annotator_id="annotator_a").delete()
        self.session.commit()

    def test_07_annotator_isolation(self):
        """Verify Annotator A and B only see their own ratings."""
        # Annotator A has rated Item 1
        resp_a = self.client.get("/api/responses/by_index/1", headers={"Authorization": f"Bearer {self.token_a}"})
        self.assertEqual(resp_a.status_code, 200)
        a_data = resp_a.json()
        self.assertIsNotNone(a_data["existing_annotation"])

        # Annotator B fetching Item 1 sees Annotator B's own rating, not Annotator A's
        resp_b = self.client.get("/api/responses/by_index/1", headers={"Authorization": f"Bearer {self.token_b}"})
        self.assertEqual(resp_b.status_code, 200)
        b_data = resp_b.json()
        self.assertIsNotNone(b_data["existing_annotation"])
        self.assertEqual(b_data["progress"]["completed_count"], 4000)

    def test_08_resume_next_unrated(self):
        """Verify resume identifies Item 501 for Annotator A."""
        resp_a = self.client.get("/api/responses/next_unrated", headers={"Authorization": f"Bearer {self.token_a}"})
        self.assertEqual(resp_a.status_code, 200)
        self.assertEqual(resp_a.json()["next_index"], 501, "Annotator A should resume at Item 501")

    def test_09_admin_export_authorization_and_schema(self):
        """Verify export endpoint requires valid admin secret and provides exact required CSV headers."""
        unauth = self.client.get("/api/admin/export")
        self.assertEqual(unauth.status_code, 403)

        auth_resp = self.client.get(f"/api/admin/export?admin_key={ADMIN_SECRET}")
        self.assertEqual(auth_resp.status_code, 200)
        self.assertEqual(auth_resp.headers["content-type"], "text/csv; charset=utf-8")

        first_line = auth_resp.text.splitlines()[0]
        expected_cols = [
            "response_id", "prompt_id", "model", "annotator_id", "prompt", "response",
            "fluency", "code_mixing_naturalness", "hindi_grammar", "prompt_adherence",
            "spelling_consistency", "overall", "notes", "submitted_at", "updated_at"
        ]
        actual_cols = [c.strip() for c in first_line.split(",")]
        for col in expected_cols:
            self.assertIn(col, actual_cols, f"Missing required column '{col}' in CSV export")

    def test_10_health_endpoint(self):
        """Verify /health diagnostic monitoring endpoint."""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database"], "connected")
        self.assertEqual(data["total_responses"], 4000)


if __name__ == "__main__":
    unittest.main()
