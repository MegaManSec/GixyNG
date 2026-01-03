import pytest

import gixy.core.sre_parse.sre_parse as sre_parse


def test_pcre_verb_removal():
    """Test that PCRE verbs like (*ANYCRLF) are properly stripped by the parser."""
    config = "(*ANYCRLF)/(?P<target>.+?)$"

    # (*ANYCRLF) should be stripped by the parser
    expected = [
        ('literal', 47), 
        ('subpattern', (1, [('min_repeat', (1, 4294967295, [('any', None)]))])), 
        ('at', 'at_end')
    ]

    actual = sre_parse.parse(config)
    assert repr(actual) == repr(expected)


def test_incomplete_pcre_verb():
    """Test that incomplete PCRE verbs raise an appropriate error."""
    config = "(*ANYCRLF"

    with pytest.raises(sre_parse.error) as exc_info:
        sre_parse.parse(config)
    
    assert "unterminated PCRE extension" in str(exc_info.value)


def test_multiple_pcre_verbs():
    """Test handling of multiple PCRE verbs."""
    config = "(*ANYCRLF)(*UCP)test"
    
    # Both PCRE verbs should be stripped
    result = sre_parse.parse(config)
    # Should just have the literal "test"
    assert len(result) == 4  # 't', 'e', 's', 't'
    assert all(token[0] == 'literal' for token in result)


def test_pcre_verb_with_regex():
    """Test PCRE verb followed by actual regex pattern."""
    config = r"(*ANYCRLF)^https?://example\.com"
    
    # Should parse the regex after stripping PCRE verb
    result = sre_parse.parse(config)
    assert result is not None
    # First token should be at_beginning (^)
    assert result[0][0] == 'at'
