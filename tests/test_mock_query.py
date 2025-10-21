"""Tests for MockQueryHandler implementation."""

import pytest
from robora.mock_query import MockQueryHandler, MockResponseModel


class TestMockQueryHandler:
    """Test the MockQueryHandler implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = MockQueryHandler(response_model=MockResponseModel)
    
    def test_format_pretty_citations_empty(self):
        """Test formatting empty citations."""
        result = self.handler._format_pretty_citations([])
        assert result == "No citations available."
    
    def test_format_pretty_citations_with_title_and_snippet(self):
        """Test formatting citations with all fields."""
        citations = [
            {
                'url': 'https://example.com',
                'title': 'Example Title',
                'snippet': 'Example snippet content',
                'date': '2024-01-15',
                'last_updated': None,
                'matched': True
            }
        ]
        result = self.handler._format_pretty_citations(citations)
        assert '[1]' in result
        assert 'Example Title' in result
        assert 'https://example.com' in result
        assert 'Example snippet content' in result
        assert 'Published: 2024-01-15' in result
    
    @pytest.mark.asyncio
    async def test_query_includes_citations(self):
        """Test that query returns a response with citations."""
        response = await self.handler.query("test question")
        
        assert response.full_response is not None
        assert 'citations' in response.full_response
        assert 'search_results' in response.full_response
        assert len(response.full_response['citations']) > 0
    
    def test_extract_fields_includes_pretty_citations(self):
        """Test that extract_fields includes pretty_citations."""
        # Use the mock response structure from the query method
        full_response = {
            'choices': [
                {
                    'message': {
                        'content': '{"relevance": 7, "explanation": "Test explanation"}'
                    }
                }
            ],
            'citations': [
                'https://mock-security-source1.com',
                'https://mock-security-source2.com'
            ],
            'search_results': [
                {
                    'url': 'https://mock-security-source1.com',
                    'title': 'Mock Cybersecurity Guidelines',
                    'snippet': 'Essential cybersecurity practices and recommendations...',
                    'date': '2024-01-15',
                    'last_updated': '2024-01-15'
                },
                {
                    'url': 'https://mock-security-source2.com', 
                    'title': 'Security Assessment Framework',
                    'snippet': 'Framework for evaluating cybersecurity posture...',
                    'date': '2024-01-10',
                    'last_updated': '2024-01-12'
                }
            ]
        }
        
        result = self.handler.extract_fields(full_response)
        
        # Check that both fields are present
        assert 'enriched_citations' in result
        assert 'pretty_citations' in result
        
        # Check enriched_citations structure
        assert len(result['enriched_citations']) == 2
        
        # Check pretty_citations format
        pretty = result['pretty_citations']
        assert '[1]' in pretty
        assert '[2]' in pretty
        assert 'Mock Cybersecurity Guidelines' in pretty
        assert 'Security Assessment Framework' in pretty
        assert 'https://mock-security-source1.com' in pretty
        assert 'https://mock-security-source2.com' in pretty
