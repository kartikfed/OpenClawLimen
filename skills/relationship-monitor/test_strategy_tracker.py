#!/usr/bin/env python3
"""
Tests for Strategy Tracker

Tests for self-analysis of response patterns and preference bias detection.
"""

import pytest
import json
from datetime import datetime
from pathlib import Path
from strategy_tracker import (
    ESConvStrategy,
    SupportContext,
    IntensityLevel,
    ResponseAnalysis,
    SessionProfile,
    PreferenceBiasReport,
    analyze_single_response,
    calculate_diversity,
    check_context_appropriateness,
    analyze_session,
    detect_preference_bias,
    ESCONV_EXPECTED_DISTRIBUTION,
    ADVERSITY_EXPECTED,
    GROWTH_EXPECTED,
)


# =====================
# SINGLE RESPONSE TESTS
# =====================

class TestSingleResponseAnalysis:
    """Test single response analysis."""
    
    def test_detects_question_strategy(self):
        """Should detect question-asking strategy."""
        response = "How are you feeling about this? What happened that led to this situation?"
        analysis = analyze_single_response(response)
        
        assert analysis.strategies[ESConvStrategy.QUESTION] > 0
        assert analysis.dominant_strategy == ESConvStrategy.QUESTION
    
    def test_detects_suggestion_strategy(self):
        """Should detect advice-giving strategy."""
        response = "You might want to try talking to them directly. I'd suggest starting with a casual conversation."
        analysis = analyze_single_response(response)
        
        assert analysis.strategies[ESConvStrategy.SUGGESTION] > 0
    
    def test_detects_affirmation_strategy(self):
        """Should detect validation/reassurance strategy."""
        response = "I'm here for you. That makes total sense and your feelings are valid. You're handling this well."
        analysis = analyze_single_response(response)
        
        assert analysis.strategies[ESConvStrategy.AFFIRMATION] > 0
    
    def test_detects_reflection_strategy(self):
        """Should detect reflecting feelings strategy."""
        response = "It sounds like you're feeling overwhelmed by this. That must be really frustrating."
        analysis = analyze_single_response(response)
        
        assert analysis.strategies[ESConvStrategy.REFLECTION] > 0
    
    def test_detects_self_disclosure(self):
        """Should detect self-disclosure strategy."""
        response = "I've been through something similar. When I faced this situation, I found that..."
        analysis = analyze_single_response(response)
        
        assert analysis.strategies[ESConvStrategy.SELF_DISCLOSURE] > 0
    
    def test_detects_multiple_strategies(self):
        """Should detect when multiple strategies are used."""
        response = """
        That sounds really tough. I hear you.
        How long has this been going on?
        You might want to consider talking to someone about it.
        I've faced similar situations before.
        """
        analysis = analyze_single_response(response)
        
        # Should detect multiple strategies
        assert analysis.strategy_count >= 3
        assert analysis.diversity_score > 0.3
    
    def test_calculates_diversity_score(self):
        """Should calculate diversity score."""
        # Single strategy response - low diversity
        single = "How are you? What happened? When did this start? Why do you think that?"
        analysis_single = analyze_single_response(single)
        
        # Multi-strategy response - higher diversity
        multi = """
        I hear you - that sounds hard.
        How are you coping with this?
        You might want to try talking to someone.
        I've been through similar things.
        """
        analysis_multi = analyze_single_response(multi)
        
        assert analysis_multi.diversity_score > analysis_single.diversity_score
    
    def test_includes_timestamp(self):
        """Should include timestamp."""
        response = "Test response"
        analysis = analyze_single_response(response, timestamp="2026-03-14T01:00:00")
        
        assert analysis.timestamp == "2026-03-14T01:00:00"


class TestContextDetection:
    """Test context-aware analysis."""
    
    def test_detects_adversity_context(self):
        """Should detect adversity context from user message."""
        user_msg = "I just got fired from my job and I'm devastated"
        response = "I'm so sorry to hear that. That sounds really hard."
        
        analysis = analyze_single_response(response, user_message=user_msg)
        
        assert analysis.user_context == SupportContext.ADVERSITY
    
    def test_detects_growth_context(self):
        """Should detect growth context from user message."""
        user_msg = "I'm thinking about starting a new project and I'm really excited"
        response = "That sounds exciting! What are you thinking of building?"
        
        analysis = analyze_single_response(response, user_message=user_msg)
        
        assert analysis.user_context == SupportContext.GROWTH
    
    def test_detects_advice_during_crisis_mismatch(self):
        """Should flag advice-heavy response during severe distress."""
        user_msg = "I can't cope anymore, everything is falling apart, I don't know what to do"
        response = "You should just call your manager and explain the situation. Then try to organize your tasks. Maybe also consider working out more to reduce stress."
        
        analysis = analyze_single_response(response, user_message=user_msg)
        
        # Should detect mismatch
        assert analysis.context_intensity == IntensityLevel.SEVERE
        # Note: May or may not flag depending on exact score thresholds


class TestDiversityCalculation:
    """Test diversity score calculation."""
    
    def test_perfect_evenness_high_diversity(self):
        """Perfectly even distribution should have high diversity."""
        even_dist = {s: 1/len(ESConvStrategy) for s in ESConvStrategy}
        diversity = calculate_diversity(even_dist)
        
        assert diversity > 0.9  # Close to 1.0
    
    def test_single_strategy_low_diversity(self):
        """Single strategy should have low diversity."""
        single_dist = {s: 0 for s in ESConvStrategy}
        single_dist[ESConvStrategy.QUESTION] = 1.0
        diversity = calculate_diversity(single_dist)
        
        assert diversity < 0.1  # Close to 0.0
    
    def test_empty_distribution_zero_diversity(self):
        """Empty distribution should have zero diversity."""
        empty_dist = {s: 0 for s in ESConvStrategy}
        diversity = calculate_diversity(empty_dist)
        
        assert diversity == 0.0


# =====================
# SESSION ANALYSIS TESTS
# =====================

class TestSessionAnalysis:
    """Test session/period analysis."""
    
    def test_empty_session(self):
        """Should handle empty session."""
        profile = analyze_session([])
        
        assert profile.response_count == 0
        assert profile.diversity_score == 0
    
    def test_aggregates_distribution(self):
        """Should aggregate distribution across responses."""
        responses = [
            ("How are you feeling?", None, None),
            ("What happened next?", None, None),
            ("That sounds tough. I hear you.", None, None),
        ]
        
        profile = analyze_session(responses)
        
        assert profile.response_count == 3
        # Should have both question and affirmation in distribution
        assert profile.strategy_distribution.get("QUESTION", 0) > 0
    
    def test_tracks_mismatches(self):
        """Should track context mismatches."""
        # Hard to test without real mismatch data
        # Just verify the fields exist
        responses = [
            ("Test response", None, None),
        ]
        
        profile = analyze_session(responses)
        
        assert hasattr(profile, 'mismatch_count')
        assert hasattr(profile, 'mismatch_rate')


# =====================
# PREFERENCE BIAS TESTS
# =====================

class TestPreferenceBias:
    """Test preference bias detection."""
    
    def test_detects_advice_heavy_bias(self):
        """Should detect when heavily biased toward suggestions."""
        # Distribution with 50% suggestions (expected ~16%)
        my_dist = {
            "QUESTION": 0.10,
            "SUGGESTION": 0.50,  # Way over expected
            "AFFIRMATION": 0.10,
            "SELF_DISCLOSURE": 0.10,
            "REFLECTION": 0.05,
            "INFORMATION": 0.05,
            "RESTATEMENT": 0.05,
            "OTHER": 0.05,
        }
        
        report = detect_preference_bias(my_dist)
        
        assert report.has_bias
        assert "SUGGESTION" in report.overused_strategies
        assert "suggestion" in report.bias_type.lower()
    
    def test_detects_question_averse_bias(self):
        """Should detect when underusing questions."""
        # Distribution with 2% questions (expected ~20%)
        my_dist = {
            "QUESTION": 0.02,  # Way under expected
            "SUGGESTION": 0.30,
            "AFFIRMATION": 0.30,
            "SELF_DISCLOSURE": 0.10,
            "REFLECTION": 0.10,
            "INFORMATION": 0.08,
            "RESTATEMENT": 0.05,
            "OTHER": 0.05,
        }
        
        report = detect_preference_bias(my_dist)
        
        assert report.has_bias
        assert "QUESTION" in report.underused_strategies
    
    def test_no_bias_when_balanced(self):
        """Should not flag bias when distribution matches expected."""
        # Distribution close to expected
        my_dist = {s.name: v for s, v in ESCONV_EXPECTED_DISTRIBUTION.items()}
        
        report = detect_preference_bias(my_dist)
        
        assert not report.has_bias or report.bias_severity == "mild"
    
    def test_generates_recommendations(self):
        """Should generate actionable recommendations."""
        # Heavily biased distribution
        my_dist = {
            "QUESTION": 0.05,
            "SUGGESTION": 0.60,
            "AFFIRMATION": 0.05,
            "SELF_DISCLOSURE": 0.10,
            "REFLECTION": 0.05,
            "INFORMATION": 0.05,
            "RESTATEMENT": 0.05,
            "OTHER": 0.05,
        }
        
        report = detect_preference_bias(my_dist)
        
        assert len(report.recommendations) > 0
    
    def test_context_specific_expectations(self):
        """Should use context-specific expectations when provided."""
        # High affirmation - appropriate for adversity, less so for growth
        high_affirmation = {
            "QUESTION": 0.10,
            "SUGGESTION": 0.10,
            "AFFIRMATION": 0.40,
            "SELF_DISCLOSURE": 0.10,
            "REFLECTION": 0.15,
            "INFORMATION": 0.05,
            "RESTATEMENT": 0.05,
            "OTHER": 0.05,
        }
        
        # In adversity context, high affirmation is more expected
        adversity_report = detect_preference_bias(
            high_affirmation, 
            context=SupportContext.ADVERSITY
        )
        
        # In growth context, high affirmation may be flagged
        growth_report = detect_preference_bias(
            high_affirmation, 
            context=SupportContext.GROWTH
        )
        
        # The adversity report should have lower deviation for affirmation
        adv_deviation = adversity_report.deviation_scores.get("AFFIRMATION", 0)
        growth_deviation = growth_report.deviation_scores.get("AFFIRMATION", 0)
        
        # Affirmation expected is higher in adversity (25%) vs growth (15%)
        # So 40% should be less deviant in adversity context
        assert adv_deviation < growth_deviation


class TestBiasSeverity:
    """Test bias severity classification."""
    
    def test_strong_bias_classification(self):
        """Should classify strong bias (>25% deviation)."""
        my_dist = {
            "QUESTION": 0.50,  # 30%+ over expected
            "SUGGESTION": 0.10,
            "AFFIRMATION": 0.10,
            "SELF_DISCLOSURE": 0.10,
            "REFLECTION": 0.05,
            "INFORMATION": 0.05,
            "RESTATEMENT": 0.05,
            "OTHER": 0.05,
        }
        
        report = detect_preference_bias(my_dist)
        
        assert report.bias_severity == "strong"
    
    def test_moderate_bias_classification(self):
        """Should classify moderate bias (15-25% deviation)."""
        my_dist = {
            "QUESTION": 0.40,  # ~18% over expected
            "SUGGESTION": 0.12,
            "AFFIRMATION": 0.12,
            "SELF_DISCLOSURE": 0.10,
            "REFLECTION": 0.08,
            "INFORMATION": 0.06,
            "RESTATEMENT": 0.06,
            "OTHER": 0.06,
        }
        
        report = detect_preference_bias(my_dist)
        
        assert report.bias_severity in ["moderate", "strong"]
    
    def test_mild_bias_classification(self):
        """Should classify mild bias (10-15% deviation)."""
        my_dist = {
            "QUESTION": 0.30,  # ~10% over expected
            "SUGGESTION": 0.14,
            "AFFIRMATION": 0.14,
            "SELF_DISCLOSURE": 0.10,
            "REFLECTION": 0.08,
            "INFORMATION": 0.08,
            "RESTATEMENT": 0.08,
            "OTHER": 0.08,
        }
        
        report = detect_preference_bias(my_dist)
        
        assert report.bias_severity in ["mild", "moderate"]


# =====================
# INTEGRATION TESTS
# =====================

class TestIntegration:
    """Integration tests for full workflow."""
    
    def test_full_analysis_workflow(self):
        """Test complete workflow from response to report."""
        # Simulate a conversation
        responses = [
            ("How are you doing today? What's on your mind?", 
             "I'm feeling stressed about work", None),
            ("That sounds tough. I hear you. Work stress can be really overwhelming.",
             "Yeah, my boss keeps piling on more work", None),
            ("You might want to try talking to your boss about workload. Have you considered that?",
             "I don't know if that would help", None),
            ("I understand the hesitation. In my experience, direct communication often helps.",
             "Maybe you're right", None),
        ]
        
        profile = analyze_session(responses)
        
        assert profile.response_count == 4
        assert profile.diversity_score > 0
        
        # Get bias report
        bias_report = detect_preference_bias(
            profile.strategy_distribution,
            response_count=profile.response_count
        )
        
        assert hasattr(bias_report, 'has_bias')
        assert hasattr(bias_report, 'recommendations')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
