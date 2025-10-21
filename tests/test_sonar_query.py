"""Tests for SonarQueryHandler implementation."""

import pytest
from robora.sonar_query import SonarQueryHandler
from pydantic import BaseModel, Field


class MockResponseModel(BaseModel):
    """Mock response model for testing."""
    answer: str = Field(description="The answer to the question")
    confidence: str = Field(description="Confidence level")


class TestSonarQueryHandler:
    """Test the SonarQueryHandler implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = SonarQueryHandler(response_model=MockResponseModel)
    
    def test_format_pretty_citations_empty(self):
        """Test formatting empty citations."""
        result = self.handler._format_pretty_citations([])
        assert result == "No citations available."
    
    def test_format_pretty_citations_basic(self):
        """Test formatting basic citations with URL only."""
        citations = [
            {
                'url': 'https://example.com',
                'title': None,
                'snippet': None,
                'date': None,
                'last_updated': None,
                'matched': False
            }
        ]
        result = self.handler._format_pretty_citations(citations)
        assert '[1]' in result
        assert 'https://example.com' in result
    
    def test_format_pretty_citations_with_title(self):
        """Test formatting citations with title."""
        citations = [
            {
                'url': 'https://example.com',
                'title': 'Example Title',
                'snippet': None,
                'date': None,
                'last_updated': None,
                'matched': True
            }
        ]
        result = self.handler._format_pretty_citations(citations)
        assert '[1]' in result
        assert 'Example Title' in result
        assert 'https://example.com' in result
    
    def test_format_pretty_citations_with_date(self):
        """Test formatting citations with date."""
        citations = [
            {
                'url': 'https://example.com',
                'title': 'Example Title',
                'snippet': None,
                'date': '2024-01-15',
                'last_updated': None,
                'matched': True
            }
        ]
        result = self.handler._format_pretty_citations(citations)
        assert 'Published: 2024-01-15' in result
    
    def test_format_pretty_citations_with_last_updated(self):
        """Test formatting citations with last_updated when no date."""
        citations = [
            {
                'url': 'https://example.com',
                'title': 'Example Title',
                'snippet': None,
                'date': None,
                'last_updated': '2024-01-20',
                'matched': True
            }
        ]
        result = self.handler._format_pretty_citations(citations)
        assert 'Updated: 2024-01-20' in result
    
    def test_format_pretty_citations_with_snippet(self):
        """Test formatting citations with snippet."""
        citations = [
            {
                'url': 'https://example.com',
                'title': 'Example Title',
                'snippet': 'This is a test snippet with some content.',
                'date': '2024-01-15',
                'last_updated': None,
                'matched': True
            }
        ]
        result = self.handler._format_pretty_citations(citations)
        assert 'This is a test snippet with some content.' in result
    
    def test_format_pretty_citations_truncates_long_snippet(self):
        """Test that long snippets are truncated."""
        long_snippet = "A" * 200  # 200 character snippet
        citations = [
            {
                'url': 'https://example.com',
                'title': 'Example Title',
                'snippet': long_snippet,
                'date': None,
                'last_updated': None,
                'matched': True
            }
        ]
        result = self.handler._format_pretty_citations(citations)
        # Should be truncated to 147 chars + "..."
        assert '...' in result
        assert len(result.split('\n')[0]) < 200  # First line should be shorter
    
    def test_format_pretty_citations_multiple(self):
        """Test formatting multiple citations."""
        citations = [
            {
                'url': 'https://example1.com',
                'title': 'First Citation',
                'snippet': 'First snippet',
                'date': '2024-01-15',
                'last_updated': None,
                'matched': True
            },
            {
                'url': 'https://example2.com',
                'title': 'Second Citation',
                'snippet': 'Second snippet',
                'date': None,
                'last_updated': '2024-01-20',
                'matched': True
            }
        ]
        result = self.handler._format_pretty_citations(citations)
        assert '[1]' in result
        assert '[2]' in result
        assert 'First Citation' in result
        assert 'Second Citation' in result
        assert 'https://example1.com' in result
        assert 'https://example2.com' in result
    
    def test_extract_fields_includes_pretty_citations(self):
        """Test that extract_fields includes pretty_citations."""
        # Create a mock full response
        full_response = {
            'choices': [
                {
                    'message': {
                        'content': '{"answer": "Test answer", "confidence": "high"}'
                    }
                }
            ],
            'citations': [
                'https://example.com'
            ],
            'search_results': [
                {
                    'url': 'https://example.com',
                    'title': 'Example Title',
                    'snippet': 'Example snippet',
                    'date': '2024-01-15',
                    'last_updated': None
                }
            ]
        }
        
        result = self.handler.extract_fields(full_response)
        
        # Check that both fields are present
        assert 'enriched_citations' in result
        assert 'pretty_citations' in result
        
        # Check enriched_citations structure
        assert len(result['enriched_citations']) == 1
        assert result['enriched_citations'][0]['url'] == 'https://example.com'
        assert result['enriched_citations'][0]['title'] == 'Example Title'
        
        # Check pretty_citations format
        assert '[1]' in result['pretty_citations']
        assert 'Example Title' in result['pretty_citations']
        assert 'https://example.com' in result['pretty_citations']
        assert 'Example snippet' in result['pretty_citations']
    
    def test_extract_fields_empty_citations(self):
        """Test extract_fields with no citations."""
        full_response = {
            'choices': [
                {
                    'message': {
                        'content': '{"answer": "Test answer", "confidence": "high"}'
                    }
                }
            ],
            'citations': [],
            'search_results': []
        }
        
        result = self.handler.extract_fields(full_response)
        
        assert 'enriched_citations' in result
        assert 'pretty_citations' in result
        assert result['enriched_citations'] == []
        assert result['pretty_citations'] == "No citations available."
