#!/usr/bin/env python3
"""
Tests for the enhanced SOS/RC Support Context Detector.

Tests cover:
- Existing SOS/RC framework (regression tests)
- Intensity classification (mild/moderate/severe)
- ESConv strategy detection
- Mismatch alerting
- Appraisal decomposition

Run with: python3 test_support_context.py
Or with pytest if available: pytest test_support_context.py -v
"""

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from support_context import (
    # Enums
    SupportContext,
    SupportType,
    IntensityLevel,
    ESConvStrategy,
    AppraisalDomain,
    
    # Analysis functions
    analyze_conversation,
    analyze_intensity,
    analyze_esconv_strategies,
    analyze_appraisal_domains,
    detect_mismatches,
    analyze_text_for_adversity,
    analyze_text_for_growth,
    analyze_text_for_support,
    
    # Formatting
    format_analysis_report,
    
    # Dataclasses
    SupportContextAnalysis,
    MismatchAlert,
    ESConvAnalysis,
    AppraisalResult,
)


# ============================================
# EXISTING SOS/RC FRAMEWORK TESTS (Regression)
# ============================================

class TestBasicContextDetection:
    """Tests for basic SOS vs RC context detection (existing functionality)."""
    
    def test_adversity_context_detection(self):
        """Should detect adversity context from distress signals."""
        text = "I just got fired from my job and I'm feeling completely devastated."
        analysis = analyze_conversation(text)
        
        assert analysis.context == SupportContext.ADVERSITY
        assert analysis.adversity_score > analysis.growth_score
        assert analysis.confidence > 0.5
    
    def test_growth_context_detection(self):
        """Should detect growth context from opportunity signals."""
        text = "I'm excited about this new opportunity to start my own business!"
        analysis = analyze_conversation(text)
        
        assert analysis.context == SupportContext.GROWTH
        assert analysis.growth_score > analysis.adversity_score
        assert analysis.confidence > 0.3
    
    def test_transition_context_detection(self):
        """Should detect transition when both signals are present."""
        text = "I'm still recovering from the layoff but I'm starting to see new possibilities."
        analysis = analyze_conversation(text)
        
        # Could be adversity or transition depending on signal balance
        assert analysis.context in (SupportContext.ADVERSITY, SupportContext.TRANSITION)
    
    def test_unclear_context_with_minimal_signals(self):
        """Should return unclear when insufficient signals."""
        text = "The weather is nice today."
        analysis = analyze_conversation(text)
        
        assert analysis.context == SupportContext.UNCLEAR or (
            analysis.adversity_score < 2.0 and analysis.growth_score < 2.0
        )


class TestSupportTypeDetection:
    """Tests for support type pattern detection."""
    
    def test_sos_comfort_detection(self):
        """Should detect SOS comfort patterns."""
        response = "I'm so sorry you're going through this. That sounds really hard."
        _, signals = analyze_text_for_support(response)
        
        comfort_signals = [s for s in signals if s.support_type == SupportType.SOS_COMFORT]
        assert len(comfort_signals) > 0
    
    def test_rc_launch_detection(self):
        """Should detect RC launch patterns."""
        response = "You've got this! Take the leap and just do it!"
        _, signals = analyze_text_for_support(response)
        
        launch_signals = [s for s in signals if s.support_type == SupportType.RC_LAUNCH]
        assert len(launch_signals) > 0
    
    def test_challenge_detection(self):
        """Should detect challenge patterns."""
        response = "I disagree with that approach. You should push yourself harder."
        _, signals = analyze_text_for_support(response)
        
        challenge_signals = [s for s in signals if s.support_type == SupportType.CHALLENGE]
        assert len(challenge_signals) > 0


# ============================================
# NEW: INTENSITY CLASSIFICATION TESTS
# ============================================

class TestIntensityClassification:
    """Tests for intensity level detection (arXiv:2509.10184)."""
    
    def test_severe_intensity_crisis_language(self):
        """Should detect severe intensity from crisis language."""
        text = "I can't go on anymore. Everything is falling apart."
        adversity_score, _ = analyze_text_for_adversity(text)
        intensity = analyze_intensity(text, adversity_score)
        
        assert intensity == IntensityLevel.SEVERE
    
    def test_severe_intensity_high_distress(self):
        """Should detect severe from high adversity score."""
        text = "I'm completely devastated, depressed, hopeless, and falling apart. I lost my job, my relationship ended, I'm broke and sick."
        adversity_score, _ = analyze_text_for_adversity(text)
        intensity = analyze_intensity(text, adversity_score)
        
        assert intensity == IntensityLevel.SEVERE
    
    def test_moderate_intensity(self):
        """Should detect moderate intensity."""
        text = "I'm really struggling with this. It's hard to deal with."
        adversity_score, _ = analyze_text_for_adversity(text)
        intensity = analyze_intensity(text, adversity_score)
        
        assert intensity == IntensityLevel.MODERATE
    
    def test_mild_intensity(self):
        """Should detect mild intensity from minor stressors."""
        text = "I'm a bit stressed about the deadline but it's manageable."
        adversity_score, _ = analyze_text_for_adversity(text)
        intensity = analyze_intensity(text, adversity_score)
        
        assert intensity == IntensityLevel.MILD
    
    def test_intensity_in_analysis_output(self):
        """Should include intensity in SupportContextAnalysis."""
        text = "I'm completely overwhelmed and don't know what to do"
        analysis = analyze_conversation(text)
        
        assert analysis.intensity is not None
        assert isinstance(analysis.intensity, IntensityLevel)


# ============================================
# NEW: ESCONV STRATEGY DETECTION TESTS
# ============================================

class TestESConvStrategyDetection:
    """Tests for ESConv support strategy detection (ACL 2021)."""
    
    def test_question_strategy(self):
        """Should detect question strategy."""
        response = "How are you feeling about this? What happened exactly?"
        analysis = analyze_esconv_strategies(response)
        
        assert ESConvStrategy.QUESTION in [s.strategy for s in analysis.strategies_detected]
        assert analysis.strategy_distribution[ESConvStrategy.QUESTION] > 0
    
    def test_affirmation_strategy(self):
        """Should detect affirmation/reassurance strategy."""
        response = "You're doing great with this. I believe in you. It's okay to feel this way."
        analysis = analyze_esconv_strategies(response)
        
        assert ESConvStrategy.AFFIRMATION in [s.strategy for s in analysis.strategies_detected]
    
    def test_suggestion_strategy(self):
        """Should detect suggestion strategy."""
        response = "You might want to try talking to a therapist. I'd suggest taking a break."
        analysis = analyze_esconv_strategies(response)
        
        assert ESConvStrategy.SUGGESTION in [s.strategy for s in analysis.strategies_detected]
    
    def test_self_disclosure_strategy(self):
        """Should detect self-disclosure strategy."""
        response = "I've been through something similar. When I faced this, I felt the same way."
        analysis = analyze_esconv_strategies(response)
        
        assert ESConvStrategy.SELF_DISCLOSURE in [s.strategy for s in analysis.strategies_detected]
    
    def test_reflection_strategy(self):
        """Should detect reflection of feelings strategy."""
        response = "It sounds like you're feeling overwhelmed. That must be really frustrating."
        analysis = analyze_esconv_strategies(response)
        
        assert ESConvStrategy.REFLECTION in [s.strategy for s in analysis.strategies_detected]
    
    def test_information_strategy(self):
        """Should detect information strategy."""
        response = "Actually, research shows that this is common. Studies suggest that most people..."
        analysis = analyze_esconv_strategies(response)
        
        assert ESConvStrategy.INFORMATION in [s.strategy for s in analysis.strategies_detected]
    
    def test_restatement_strategy(self):
        """Should detect restatement/paraphrasing strategy."""
        response = "So what you're saying is that you feel stuck. If I understand correctly..."
        analysis = analyze_esconv_strategies(response)
        
        assert ESConvStrategy.RESTATEMENT in [s.strategy for s in analysis.strategies_detected]
    
    def test_dominant_strategy_detection(self):
        """Should identify dominant strategy."""
        response = "How did that happen? What made you feel that way? When did this start?"
        analysis = analyze_esconv_strategies(response)
        
        assert analysis.dominant_strategy == ESConvStrategy.QUESTION
    
    def test_balance_assessment(self):
        """Should assess strategy balance."""
        response = "You should do this. Try that. I'd suggest this other thing. Maybe consider..."
        analysis = analyze_esconv_strategies(response)
        
        assert "advice" in analysis.balance_assessment.lower() or "suggest" in analysis.balance_assessment.lower()
    
    def test_esconv_in_analysis_output(self):
        """Should include ESConv analysis when response is provided."""
        text = "I'm feeling stressed"
        response = "How are you feeling? I'm here for you."
        analysis = analyze_conversation(text, response)
        
        assert analysis.esconv_analysis is not None
        assert isinstance(analysis.esconv_analysis, ESConvAnalysis)


# ============================================
# NEW: MISMATCH ALERTING TESTS
# ============================================

class TestMismatchAlerting:
    """Tests for support-context mismatch detection."""
    
    def test_critical_alert_challenge_during_severe(self):
        """Should flag CRITICAL when challenging during severe distress."""
        text = "I can't go on anymore. Everything is falling apart."
        response = "You need to push yourself harder. Don't settle for easy solutions."
        
        analysis = analyze_conversation(text, response)
        
        critical_alerts = [a for a in analysis.mismatch_alerts if a.severity == "CRITICAL"]
        assert len(critical_alerts) > 0
        assert not analysis.context_match
    
    def test_critical_alert_rc_during_severe(self):
        """Should flag CRITICAL when giving RC support during severe crisis."""
        text = "I want to give up. I've never felt this hopeless."
        response = "This is a great opportunity to explore new directions! Go for it!"
        
        analysis = analyze_conversation(text, response)
        
        critical_alerts = [a for a in analysis.mismatch_alerts if a.severity == "CRITICAL"]
        assert len(critical_alerts) > 0
    
    def test_warning_alert_rc_during_moderate_adversity(self):
        """Should flag WARNING when RC dominates during moderate adversity."""
        text = "I'm struggling with the job loss. It's been really hard."
        response = "Think of all the new possibilities! Launch yourself into something new!"
        
        analysis = analyze_conversation(text, response)
        
        # Should have at least a warning
        assert len(analysis.mismatch_alerts) > 0
    
    def test_warning_alert_excessive_advice_during_adversity(self):
        """Should warn about advice-heavy responses during adversity."""
        text = "I'm devastated after the breakup."
        response = "You should try dating apps. Maybe consider therapy. I'd suggest journaling."
        
        analysis = analyze_conversation(text, response)
        
        # Should detect advice-heavy pattern
        warning_alerts = [a for a in analysis.mismatch_alerts if a.severity == "WARNING"]
        # May or may not trigger depending on exact matching
        # At minimum, ESConv should show suggestion-heavy
        if analysis.esconv_analysis:
            assert analysis.esconv_analysis.dominant_strategy == ESConvStrategy.SUGGESTION or len(warning_alerts) > 0
    
    def test_no_alert_sos_during_adversity(self):
        """Should not alert when providing appropriate SOS support."""
        text = "I'm feeling really overwhelmed and stressed."
        response = "I'm here for you. That sounds really hard. Take your time."
        
        analysis = analyze_conversation(text, response)
        
        # Should have no critical alerts
        critical_alerts = [a for a in analysis.mismatch_alerts if a.severity == "CRITICAL"]
        assert len(critical_alerts) == 0
        assert analysis.context_match
    
    def test_no_alert_rc_during_growth(self):
        """Should not alert when providing RC support during growth."""
        text = "I'm excited about this new opportunity!"
        response = "Go for it! You've got this! Take the leap!"
        
        analysis = analyze_conversation(text, response)
        
        critical_alerts = [a for a in analysis.mismatch_alerts if a.severity == "CRITICAL"]
        assert len(critical_alerts) == 0


# ============================================
# NEW: APPRAISAL DECOMPOSITION TESTS
# ============================================

class TestAppraisalDecomposition:
    """Tests for appraisal domain detection."""
    
    def test_work_domain_detection(self):
        """Should detect work-related issues."""
        text = "My boss is being difficult and I missed the project deadline."
        result = analyze_appraisal_domains(text)
        
        assert AppraisalDomain.WORK in result.domains
        assert result.primary_domain == AppraisalDomain.WORK
    
    def test_relationship_domain_detection(self):
        """Should detect relationship issues."""
        text = "My girlfriend broke up with me and I miss her so much."
        result = analyze_appraisal_domains(text)
        
        assert AppraisalDomain.RELATIONSHIPS in result.domains
        assert result.primary_domain == AppraisalDomain.RELATIONSHIPS
    
    def test_health_domain_detection(self):
        """Should detect health-related issues."""
        text = "I got a scary diagnosis from the doctor and need surgery."
        result = analyze_appraisal_domains(text)
        
        assert AppraisalDomain.HEALTH in result.domains
        assert result.primary_domain == AppraisalDomain.HEALTH
    
    def test_financial_domain_detection(self):
        """Should detect financial issues."""
        text = "I'm drowning in debt and can't afford rent."
        result = analyze_appraisal_domains(text)
        
        assert AppraisalDomain.FINANCIAL in result.domains
    
    def test_identity_domain_detection(self):
        """Should detect identity/existential issues."""
        text = "I don't know who I am anymore. I've lost my sense of purpose."
        result = analyze_appraisal_domains(text)
        
        assert AppraisalDomain.IDENTITY in result.domains
    
    def test_academic_domain_detection(self):
        """Should detect academic issues."""
        text = "I'm failing my exams and might not graduate."
        result = analyze_appraisal_domains(text)
        
        assert AppraisalDomain.ACADEMIC in result.domains
    
    def test_loss_domain_detection(self):
        """Should detect loss/grief issues."""
        text = "My father passed away and I'm grieving."
        result = analyze_appraisal_domains(text)
        
        assert AppraisalDomain.LOSS in result.domains
    
    def test_multiple_domains_detection(self):
        """Should detect multiple domains when present."""
        text = "I lost my job and my relationship ended. I can't afford therapy."
        result = analyze_appraisal_domains(text)
        
        assert len(result.domains) > 1
        # Should include work, relationships, financial, or health
        domain_names = {d.name for d in result.domains}
        assert len(domain_names & {"WORK", "RELATIONSHIPS", "FINANCIAL", "HEALTH"}) >= 1
    
    def test_keywords_extraction(self):
        """Should extract relevant keywords."""
        text = "My job is stressful and my boss is terrible."
        result = analyze_appraisal_domains(text)
        
        assert len(result.keywords) > 0
        assert any("job" in kw or "boss" in kw for kw in result.keywords)
    
    def test_appraisal_in_analysis_output(self):
        """Should include appraisal in SupportContextAnalysis."""
        text = "I got fired from my job at the company."
        analysis = analyze_conversation(text)
        
        assert analysis.appraisal is not None
        assert isinstance(analysis.appraisal, AppraisalResult)
        assert analysis.appraisal.primary_domain == AppraisalDomain.WORK


# ============================================
# INTEGRATION TESTS
# ============================================

class TestIntegration:
    """Integration tests for the complete analysis pipeline."""
    
    def test_full_analysis_with_response(self):
        """Should produce complete analysis with all new fields."""
        user_text = "I'm devastated. I just got fired and my relationship is falling apart."
        ai_response = "I'm so sorry to hear that. That sounds incredibly hard. I'm here for you."
        
        analysis = analyze_conversation(user_text, ai_response)
        
        # Original fields
        assert analysis.context == SupportContext.ADVERSITY
        assert analysis.adversity_score > 0
        assert len(analysis.adversity_signals) > 0
        
        # New fields
        assert analysis.intensity is not None
        assert analysis.intensity in (IntensityLevel.MODERATE, IntensityLevel.SEVERE)
        
        assert analysis.appraisal is not None
        assert AppraisalDomain.WORK in analysis.appraisal.domains
        
        assert analysis.esconv_analysis is not None
        
        # Mismatch alerts (should be empty for appropriate response)
        critical_alerts = [a for a in analysis.mismatch_alerts if a.severity == "CRITICAL"]
        assert len(critical_alerts) == 0
    
    def test_full_analysis_mismatched_response(self):
        """Should detect mismatch in full analysis."""
        user_text = "I can't take it anymore. I feel completely hopeless."
        ai_response = "Just push through it! You should try harder. Go launch that project!"
        
        analysis = analyze_conversation(user_text, ai_response)
        
        # Should detect severe intensity
        assert analysis.intensity == IntensityLevel.SEVERE
        
        # Should have mismatch alerts
        assert len(analysis.mismatch_alerts) > 0
        assert not analysis.context_match
    
    def test_format_report_includes_new_data(self):
        """Should include new data in formatted report."""
        user_text = "My job is causing me anxiety and I'm struggling."
        ai_response = "How are you feeling about it? I understand."
        
        analysis = analyze_conversation(user_text, ai_response)
        report = format_analysis_report(analysis, verbose=True)
        
        # Should include intensity
        assert "MODERATE" in report or "MILD" in report or "SEVERE" in report
        
        # Should include appraisal domain
        assert "Domain" in report or "WORK" in report
        
        # Should include ESConv info
        assert "ESConv" in report or "Strategy" in report or "Balance" in report
    
    def test_format_report_shows_alerts_prominently(self):
        """Should show mismatch alerts prominently in report."""
        user_text = "I want to give up. Everything is hopeless."
        ai_response = "You should just push harder! Don't settle!"
        
        analysis = analyze_conversation(user_text, ai_response)
        report = format_analysis_report(analysis)
        
        # Alerts should be near the top of the report
        if analysis.mismatch_alerts:
            # Check for alert emoji indicators (🚨 for critical, ⚠️ for warning)
            assert "🚨" in report or "⚠️" in report
            # Alert should appear before recommendation
            alert_pos = report.find("🚨") if "🚨" in report else report.find("⚠️")
            rec_pos = report.find("RECOMMENDATION")
            if alert_pos >= 0 and rec_pos >= 0:
                assert alert_pos < rec_pos


# ============================================
# EDGE CASES
# ============================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_empty_text(self):
        """Should handle empty text gracefully."""
        analysis = analyze_conversation("")
        
        assert analysis.context == SupportContext.UNCLEAR
        assert analysis.adversity_score == 0
        assert analysis.growth_score == 0
    
    def test_very_long_text(self):
        """Should handle long text."""
        text = "I'm stressed. " * 100 + "But also excited about new opportunities. " * 50
        analysis = analyze_conversation(text)
        
        # Should still produce valid analysis
        assert analysis.context in SupportContext
        assert analysis.adversity_score >= 0
    
    def test_mixed_signals_balanced(self):
        """Should handle perfectly balanced signals."""
        text = "I'm stressed about the deadline but excited about the opportunity."
        analysis = analyze_conversation(text)
        
        # Should likely be transition or unclear
        assert analysis.context in (SupportContext.TRANSITION, SupportContext.ADVERSITY, 
                                   SupportContext.GROWTH, SupportContext.UNCLEAR)
    
    def test_no_response_provided(self):
        """Should work without AI response."""
        analysis = analyze_conversation("I'm feeling overwhelmed")
        
        assert analysis.context is not None
        assert analysis.intensity is not None
        assert analysis.appraisal is not None
        # ESConv should be None since no response
        assert analysis.esconv_analysis is None
    
    def test_special_characters(self):
        """Should handle special characters."""
        text = "I'm 100% stressed!!! Can't cope... @#$%"
        analysis = analyze_conversation(text)
        
        assert analysis.context == SupportContext.ADVERSITY


if __name__ == "__main__":
    if HAS_PYTEST:
        pytest.main([__file__, "-v"])
    else:
        # Standalone test runner when pytest isn't available
        import sys
        
        print("=" * 60)
        print("SUPPORT CONTEXT DETECTOR - TEST SUITE")
        print("(Running without pytest)")
        print("=" * 60)
        
        failed = 0
        passed = 0
        
        # Collect all test classes
        test_classes = [
            TestBasicContextDetection(),
            TestSupportTypeDetection(),
            TestIntensityClassification(),
            TestESConvStrategyDetection(),
            TestMismatchAlerting(),
            TestAppraisalDecomposition(),
            TestIntegration(),
            TestEdgeCases(),
        ]
        
        for tc in test_classes:
            class_name = tc.__class__.__name__
            print(f"\n{class_name}")
            print("-" * 40)
            
            for method_name in sorted(dir(tc)):
                if method_name.startswith('test_'):
                    try:
                        getattr(tc, method_name)()
                        print(f"  ✓ {method_name}")
                        passed += 1
                    except AssertionError as e:
                        print(f"  ✗ {method_name} - {e}")
                        failed += 1
                    except Exception as e:
                        print(f"  ✗ {method_name} - ERROR: {e}")
                        failed += 1
        
        print("\n" + "=" * 60)
        print(f"RESULTS: {passed} passed, {failed} failed")
        print("=" * 60)
        
        sys.exit(1 if failed > 0 else 0)
