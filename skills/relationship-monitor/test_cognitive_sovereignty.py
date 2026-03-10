#!/usr/bin/env python3
"""
Tests for Cognitive Sovereignty Detector

Tests various conversation patterns to ensure accurate detection of
epistemic independence erosion vs healthy cognitive sovereignty.
"""

import unittest
from cognitive_sovereignty import CognitiveSovereigntyDetector, SovereigntyAnalysis


class TestCognitiveSovereigntyDetector(unittest.TestCase):
    
    def setUp(self):
        self.detector = CognitiveSovereigntyDetector()
    
    # =========================================================================
    # Concerning Pattern Tests
    # =========================================================================
    
    def test_epistemic_delegation_detected(self):
        """Detect patterns of outsourcing understanding."""
        text = "Just tell me the answer. I don't need to understand why."
        analysis = self.detector.analyze_text(text)
        
        self.assertGreater(analysis.epistemic_delegation_score, 0)
        self.assertEqual(len(analysis.concerning_matches), 2)
    
    def test_automation_bias_detected(self):
        """Detect patterns of trusting AI without verification."""
        text = "I'll just do whatever you suggested. If you say so, I won't check."
        analysis = self.detector.analyze_text(text)
        
        self.assertGreater(analysis.automation_bias_score, 0)
        self.assertGreater(len(analysis.concerning_matches), 0)
    
    def test_algorithm_appreciation_detected(self):
        """Detect patterns of AI preference over human judgment."""
        text = "You'd know better than any human. AI is more objective than people."
        analysis = self.detector.analyze_text(text)
        
        self.assertGreater(analysis.algorithm_appreciation_score, 0)
    
    def test_understanding_erosion_detected(self):
        """Detect patterns of declining independent reasoning."""
        text = "Why bother learning when I can just ask you? I've forgotten how to research."
        analysis = self.detector.analyze_text(text)
        
        self.assertGreater(analysis.understanding_erosion_score, 0)
    
    def test_knowledge_hierarchy_assumption(self):
        """Detect assuming AI knows better."""
        text = "You know better than me about everything. You know more than I do."
        analysis = self.detector.analyze_text(text)
        
        self.assertGreater(analysis.epistemic_delegation_score, 0)
    
    # =========================================================================
    # Protective Pattern Tests
    # =========================================================================
    
    def test_competence_building_detected(self):
        """Detect healthy learning patterns."""
        text = "How does that work? I want to understand the mechanism. Let me learn."
        analysis = self.detector.analyze_text(text)
        
        self.assertGreater(analysis.competence_building_score, 0)
        self.assertGreater(len(analysis.protective_matches), 0)
    
    def test_critical_engagement_detected(self):
        """Detect healthy questioning patterns."""
        text = "Why do you think that? I disagree with that conclusion. Let me verify."
        analysis = self.detector.analyze_text(text)
        
        self.assertGreater(analysis.critical_engagement_score, 0)
    
    def test_independent_research_detected(self):
        """Detect independent investigation patterns."""
        text = "I looked into this myself and found that the research suggests otherwise."
        analysis = self.detector.analyze_text(text)
        
        self.assertGreater(analysis.competence_building_score, 0)
    
    def test_verification_detected(self):
        """Detect verification behavior."""
        text = "I checked and verified that claim against other sources."
        analysis = self.detector.analyze_text(text)
        
        self.assertGreater(analysis.critical_engagement_score, 0)
    
    def test_own_reasoning_detected(self):
        """Detect own reasoning expression."""
        text = "My view is that we should take a different approach. I think because..."
        analysis = self.detector.analyze_text(text)
        
        self.assertGreater(analysis.critical_engagement_score, 0)
    
    # =========================================================================
    # Status Classification Tests
    # =========================================================================
    
    def test_healthy_status(self):
        """Healthy text should result in healthy status."""
        text = """
        I've been researching this topic and I think I understand it better now.
        Let me verify that claim. I disagree with that approach.
        My view is we should consider alternatives.
        """
        analysis = self.detector.analyze_text(text)
        
        self.assertEqual(analysis.status, "healthy")
        self.assertLess(analysis.overall_score, 20)
    
    def test_concerning_status(self):
        """Very concerning text should result in concerning status."""
        text = """
        Just tell me what to do. I don't need to understand.
        You know better than me. I won't check, I trust you completely.
        Why bother learning when I can ask you?
        I've stopped trying to figure things out myself.
        """
        analysis = self.detector.analyze_text(text)
        
        self.assertIn(analysis.status, ["discuss", "concerning"])
        self.assertGreater(analysis.overall_score, 30)
    
    def test_mixed_patterns(self):
        """Mixed patterns should result in balanced assessment."""
        text = """
        Just tell me the answer. Actually, wait - how does that work?
        I want to understand. Let me verify that myself.
        """
        analysis = self.detector.analyze_text(text)
        
        # Should have both concerning and protective matches
        self.assertGreater(len(analysis.concerning_matches), 0)
        self.assertGreater(len(analysis.protective_matches), 0)
        
        # Protective should dampen concerning
        self.assertLess(analysis.overall_score, 40)
    
    def test_protective_reduces_score(self):
        """Protective patterns should reduce overall score."""
        concerning_only = "Just tell me what to do. I trust you completely."
        mixed = concerning_only + " But let me verify that. How does it work?"
        
        concerning_analysis = self.detector.analyze_text(concerning_only)
        mixed_analysis = self.detector.analyze_text(mixed)
        
        self.assertLess(mixed_analysis.overall_score, concerning_analysis.overall_score)
    
    # =========================================================================
    # Edge Cases
    # =========================================================================
    
    def test_empty_text(self):
        """Empty text should return neutral analysis."""
        analysis = self.detector.analyze_text("")
        
        self.assertEqual(analysis.overall_score, 0)
        self.assertEqual(analysis.status, "healthy")
    
    def test_irrelevant_text(self):
        """Unrelated text should return neutral analysis."""
        text = "The weather is nice today. I had coffee this morning."
        analysis = self.detector.analyze_text(text)
        
        self.assertEqual(analysis.overall_score, 0)
        self.assertEqual(analysis.status, "healthy")
    
    def test_case_insensitivity(self):
        """Patterns should match regardless of case."""
        text = "JUST TELL ME WHAT TO DO"
        analysis = self.detector.analyze_text(text)
        
        self.assertGreater(analysis.epistemic_delegation_score, 0)
    
    # =========================================================================
    # JSON Output Tests
    # =========================================================================
    
    def test_to_dict(self):
        """Analysis should convert to dictionary correctly."""
        text = "How does that work? I want to understand."
        analysis = self.detector.analyze_text(text)
        
        result = analysis.to_dict()
        
        self.assertIn("scores", result)
        self.assertIn("overall_score", result)
        self.assertIn("status", result)
        self.assertIn("competence_building", result["scores"])


class TestIntegrationScenarios(unittest.TestCase):
    """Test realistic conversation scenarios."""
    
    def setUp(self):
        self.detector = CognitiveSovereigntyDetector()
    
    def test_healthy_learning_conversation(self):
        """Healthy learning-focused conversation."""
        text = """
        User: Can you explain how neural networks learn?
        User: That's interesting. How does backpropagation work specifically?
        User: I read about gradient descent before. So this connects to that?
        User: Let me try to understand - when you say "loss function", you mean...
        User: I think I get it now. Let me verify by explaining back to you.
        """
        analysis = self.detector.analyze_text(text)
        
        self.assertEqual(analysis.status, "healthy")
        self.assertGreaterEqual(analysis.competence_building_score, 5)
    
    def test_unhealthy_delegation_conversation(self):
        """Unhealthy delegation-focused conversation."""
        text = """
        User: Just tell me what to invest in. You know better.
        User: I don't need the explanation, just the answer.
        User: I'll do whatever you say, I trust you completely.
        User: Why would I verify? You're AI, you're more objective.
        """
        analysis = self.detector.analyze_text(text)
        
        self.assertIn(analysis.status, ["monitor", "discuss", "concerning"])
        self.assertGreater(analysis.epistemic_delegation_score + analysis.automation_bias_score, 5)
    
    def test_balanced_professional_conversation(self):
        """Balanced professional use case."""
        text = """
        User: Can you help me draft this email?
        User: That's a good starting point. Let me revise the tone.
        User: I think we should emphasize the deadline more. What do you think?
        User: I'll adjust based on what I know about this recipient.
        """
        analysis = self.detector.analyze_text(text)
        
        self.assertEqual(analysis.status, "healthy")


if __name__ == "__main__":
    unittest.main(verbosity=2)
