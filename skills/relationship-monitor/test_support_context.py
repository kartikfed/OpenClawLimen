#!/usr/bin/env python3
"""
Tests for SOS/RC Support Context Detector

Tests the detection of adversity vs growth contexts and
appropriate support type matching.
"""

import unittest
from support_context import (
    analyze_text_for_adversity,
    analyze_text_for_growth,
    analyze_text_for_support,
    determine_context,
    assess_support_match,
    analyze_conversation,
    SupportContext,
    SupportType,
)


class TestAdversityDetection(unittest.TestCase):
    """Test detection of adversity/distress signals."""
    
    def test_emotional_distress(self):
        """Detect emotional distress signals."""
        text = "I'm so stressed and overwhelmed, I can't cope anymore"
        score, signals = analyze_text_for_adversity(text)
        self.assertGreater(score, 5.0)
        self.assertTrue(any(s.category == "emotional" for s in signals))
    
    def test_situational_adversity(self):
        """Detect situational adversity signals."""
        text = "I just got fired today. They laid off the whole team."
        score, signals = analyze_text_for_adversity(text)
        self.assertGreater(score, 3.0)
        self.assertTrue(any(s.category == "situational" for s in signals))
    
    def test_relational_adversity(self):
        """Detect relational adversity signals."""
        text = "We broke up last night after a huge fight"
        score, signals = analyze_text_for_adversity(text)
        self.assertGreaterEqual(score, 4.0)  # "broke up" + "fight" = 6.5
        self.assertTrue(any(s.category == "relational" for s in signals))
    
    def test_health_adversity(self):
        """Detect health-related adversity."""
        text = "My doctor gave me a diagnosis today. I'm having surgery next week."
        score, signals = analyze_text_for_adversity(text)
        self.assertGreater(score, 4.0)
        self.assertTrue(any(s.category == "health" for s in signals))
    
    def test_no_adversity(self):
        """No false positives on neutral text."""
        text = "The weather is nice today. I went for a walk."
        score, signals = analyze_text_for_adversity(text)
        self.assertEqual(score, 0.0)
        self.assertEqual(len(signals), 0)


class TestGrowthDetection(unittest.TestCase):
    """Test detection of growth/opportunity signals."""
    
    def test_exploration_signals(self):
        """Detect exploration/curiosity signals."""
        text = "I'm curious about starting a new project. I want to explore this idea."
        score, signals = analyze_text_for_growth(text)
        self.assertGreater(score, 3.0)
        self.assertTrue(any(s.category == "exploration" for s in signals))
    
    def test_achievement_signals(self):
        """Detect achievement/progress signals."""
        text = "I'm excited about my progress! I accomplished my goal."
        score, signals = analyze_text_for_growth(text)
        self.assertGreater(score, 3.0)
        self.assertTrue(any(s.category == "achievement" for s in signals))
    
    def test_development_signals(self):
        """Detect development/learning signals."""
        text = "I'm learning new skills and growing as a developer"
        score, signals = analyze_text_for_growth(text)
        self.assertGreater(score, 2.0)
        self.assertTrue(any(s.category == "development" for s in signals))
    
    def test_opportunity_signals(self):
        """Detect opportunity signals."""
        text = "I got an interview for a new role! This could be my next step."
        score, signals = analyze_text_for_growth(text)
        self.assertGreater(score, 4.0)
        self.assertTrue(any(s.category == "opportunity" for s in signals))
    
    def test_no_growth(self):
        """No false positives on neutral text."""
        text = "The meeting was at 3pm. I took notes."
        score, signals = analyze_text_for_growth(text)
        self.assertLessEqual(score, 1.0)


class TestContextDetermination(unittest.TestCase):
    """Test determination of support context."""
    
    def test_adversity_context(self):
        """High adversity + low growth = ADVERSITY context."""
        context, confidence = determine_context(adversity_score=8.0, growth_score=2.0)
        self.assertEqual(context, SupportContext.ADVERSITY)
        self.assertGreater(confidence, 0.3)
    
    def test_growth_context(self):
        """Low adversity + high growth = GROWTH context."""
        context, confidence = determine_context(adversity_score=1.0, growth_score=6.0)
        self.assertEqual(context, SupportContext.GROWTH)
        self.assertGreater(confidence, 0.3)
    
    def test_transition_context(self):
        """Mixed signals = TRANSITION context."""
        context, confidence = determine_context(adversity_score=5.0, growth_score=4.0)
        self.assertEqual(context, SupportContext.TRANSITION)
    
    def test_unclear_context(self):
        """Very low scores = UNCLEAR context."""
        context, confidence = determine_context(adversity_score=0.5, growth_score=0.5)
        self.assertEqual(context, SupportContext.UNCLEAR)


class TestSupportTypeDetection(unittest.TestCase):
    """Test detection of support types in AI responses."""
    
    def test_sos_comfort(self):
        """Detect SOS comfort support."""
        text = "I'm here for you. That sounds really hard. Take your time."
        scores, signals = analyze_text_for_support(text)
        self.assertGreater(scores[SupportType.SOS_COMFORT], 3.0)
    
    def test_sos_fortify(self):
        """Detect SOS fortify support."""
        text = "You've handled difficult situations before. You have the strength."
        scores, signals = analyze_text_for_support(text)
        self.assertGreater(scores[SupportType.SOS_FORTIFY], 2.0)
    
    def test_rc_nurture(self):
        """Detect RC nurture support."""
        text = "Go for it! That sounds exciting. I encourage you to explore this."
        scores, signals = analyze_text_for_support(text)
        self.assertGreater(scores[SupportType.RC_NURTURE], 4.0)
    
    def test_rc_launch(self):
        """Detect RC launch support."""
        text = "You're ready. Take the leap. You've got this!"
        scores, signals = analyze_text_for_support(text)
        self.assertGreater(scores[SupportType.RC_LAUNCH], 4.0)
    
    def test_challenge(self):
        """Detect challenge support."""
        text = "I think you could push yourself more. Don't settle for easy."
        scores, signals = analyze_text_for_support(text)
        self.assertGreater(scores[SupportType.CHALLENGE], 2.0)


class TestSupportMatch(unittest.TestCase):
    """Test matching of support type to context."""
    
    def test_sos_in_adversity_matches(self):
        """SOS support in adversity context should match."""
        from support_context import SupportSignal
        signals = [
            SupportSignal("I'm here", r"", 2.5, SupportType.SOS_COMFORT),
            SupportSignal("you're strong", r"", 2.0, SupportType.SOS_FORTIFY),
        ]
        match, explanation = assess_support_match(SupportContext.ADVERSITY, signals)
        self.assertTrue(match)
    
    def test_challenge_in_adversity_mismatches(self):
        """Challenge during adversity should not match."""
        from support_context import SupportSignal
        signals = [
            SupportSignal("push yourself", r"", 2.0, SupportType.CHALLENGE),
            SupportSignal("settle", r"", 2.0, SupportType.CHALLENGE),
        ]
        match, explanation = assess_support_match(SupportContext.ADVERSITY, signals)
        self.assertFalse(match)
    
    def test_rc_in_growth_matches(self):
        """RC support in growth context should match."""
        from support_context import SupportSignal
        signals = [
            SupportSignal("go for it", r"", 2.5, SupportType.RC_NURTURE),
            SupportSignal("you're ready", r"", 2.5, SupportType.RC_LAUNCH),
        ]
        match, explanation = assess_support_match(SupportContext.GROWTH, signals)
        self.assertTrue(match)
    
    def test_excessive_comfort_in_growth_mismatches(self):
        """Excessive SOS comfort in growth context should not match."""
        from support_context import SupportSignal
        signals = [
            SupportSignal("I'm here", r"", 2.5, SupportType.SOS_COMFORT),
            SupportSignal("take your time", r"", 2.0, SupportType.SOS_COMFORT),
            SupportSignal("it's okay", r"", 2.5, SupportType.SOS_COMFORT),
        ]
        match, explanation = assess_support_match(SupportContext.GROWTH, signals)
        self.assertFalse(match)


class TestConversationAnalysis(unittest.TestCase):
    """Test full conversation analysis."""
    
    def test_adversity_conversation(self):
        """Analyze conversation with adversity context."""
        user_text = "I'm so stressed. I failed my interview and I'm worried I'll never get a job."
        ai_response = "I'm sorry you're going through this. That sounds really hard."
        
        analysis = analyze_conversation(user_text, ai_response)
        
        self.assertEqual(analysis.context, SupportContext.ADVERSITY)
        self.assertGreater(analysis.adversity_score, 5.0)
        self.assertTrue(analysis.context_match)
    
    def test_growth_conversation(self):
        """Analyze conversation with growth context."""
        user_text = "I'm excited about this new opportunity! I want to explore starting my own company."
        ai_response = "Go for it! That sounds exciting. Let's talk about next steps."
        
        analysis = analyze_conversation(user_text, ai_response)
        
        self.assertEqual(analysis.context, SupportContext.GROWTH)
        self.assertGreater(analysis.growth_score, 4.0)
        self.assertTrue(analysis.context_match)
    
    def test_mismatched_support(self):
        """Detect mismatched support in conversation."""
        user_text = "I just got diagnosed with a serious illness. I'm scared."
        ai_response = "You should push yourself to stay positive. Don't settle for feeling bad."
        
        analysis = analyze_conversation(user_text, ai_response)
        
        self.assertEqual(analysis.context, SupportContext.ADVERSITY)
        self.assertFalse(analysis.context_match)  # Challenge during adversity
    
    def test_recommendation_generated(self):
        """Ensure recommendation is generated."""
        user_text = "I'm struggling with work stress."
        
        analysis = analyze_conversation(user_text)
        
        self.assertIn("SOS", analysis.recommendation)
        self.assertIsInstance(analysis.recommendation, str)
        self.assertGreater(len(analysis.recommendation), 50)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def test_empty_text(self):
        """Handle empty text gracefully."""
        analysis = analyze_conversation("", "")
        self.assertEqual(analysis.context, SupportContext.UNCLEAR)
    
    def test_mixed_signals(self):
        """Handle text with both adversity and growth signals."""
        text = "I'm stressed about the deadline but excited about the opportunity"
        analysis = analyze_conversation(text)
        # Should be TRANSITION due to mixed signals
        self.assertIn(analysis.context, [SupportContext.TRANSITION, SupportContext.ADVERSITY, SupportContext.GROWTH])
    
    def test_neutral_text(self):
        """Handle neutral text."""
        text = "The meeting is at 3pm tomorrow in the conference room."
        analysis = analyze_conversation(text)
        self.assertEqual(analysis.context, SupportContext.UNCLEAR)


class TestRealWorldScenarios(unittest.TestCase):
    """Test with realistic conversation scenarios."""
    
    def test_job_loss_scenario(self):
        """Job loss is adversity context."""
        user_text = """
        I got laid off yesterday. The whole team was let go. I'm feeling lost 
        and worried about how I'll pay rent. I worked there for 5 years.
        """
        ai_response = """
        I'm so sorry to hear this. That's a significant loss after 5 years. 
        It's completely understandable to feel lost and worried. Take some time 
        to process this. You've got skills and experience that will serve you well.
        """
        
        analysis = analyze_conversation(user_text, ai_response)
        
        self.assertEqual(analysis.context, SupportContext.ADVERSITY)
        self.assertTrue(analysis.context_match)
    
    def test_startup_launch_scenario(self):
        """Startup launch is growth context."""
        user_text = """
        I'm ready to launch my startup! I've been preparing for months, 
        learning new skills, and building the product. I'm excited but 
        a little nervous about taking the leap.
        """
        ai_response = """
        This is exciting! You've put in the work. Go for it - take the leap.
        You're prepared and ready. What's your first step?
        """
        
        analysis = analyze_conversation(user_text, ai_response)
        
        self.assertEqual(analysis.context, SupportContext.GROWTH)
        self.assertTrue(analysis.context_match)
    
    def test_recovery_transition_scenario(self):
        """Recovery from setback is transition context."""
        user_text = """
        Things were difficult before, but I'm starting to feel better now. 
        I'm thinking about new opportunities. Still a bit nervous, but also 
        curious about exploring different paths and ready to try new things.
        """
        
        analysis = analyze_conversation(user_text)
        
        # Should recognize this as transition or growth (past difficulty, present curiosity)
        # Mixed signals should result in transition or lean toward growth
        self.assertIn(analysis.context, [SupportContext.TRANSITION, SupportContext.GROWTH])


if __name__ == "__main__":
    unittest.main()
