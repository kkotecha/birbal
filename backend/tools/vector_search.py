"""Vector search tool for BNS sections using Supabase pgvector"""

from typing import List, Dict, Optional
from langchain_openai import OpenAIEmbeddings
from tools.supabase_client import get_supabase_client
from config import EMBEDDING_MODEL


class BNSVectorSearch:
    """Search BNS chunks using semantic similarity"""

    def __init__(self):
        self.supabase = get_supabase_client()
        self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    def search(
        self,
        query: str,
        top_k: int = 10,
        similarity_threshold: float = 0.5,
        chunk_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Search BNS chunks by semantic similarity.

        Args:
            query: Crime description or search text
            top_k: Number of results to return
            similarity_threshold: Minimum cosine similarity (0-1)
            chunk_type: Filter by chunk type ('main', 'subsection', 'illustration')

        Returns:
            List of matching chunks with metadata
        """
        # Generate embedding for query
        query_embedding = self.embeddings.embed_query(query)

        # Build SQL query for vector search
        # Using cosine distance: <=> operator
        # Note: Supabase RPC function needed for proper vector search

        # For now, use direct query approach
        # We'll create an RPC function in Supabase later for better performance

        try:
            # Use Supabase RPC function for vector similarity search
            params = {
                'query_embedding': query_embedding,
                'match_threshold': similarity_threshold,
                'match_count': top_k
            }

            if chunk_type:
                params['filter_chunk_type'] = chunk_type

            result = self.supabase.rpc('match_bns_chunks', params).execute()

            return result.data

        except Exception as e:
            print(f"Error in vector search: {e}")
            return []

    def search_by_section(self, section_number: str) -> Dict:
        """Get all chunks for a specific section"""

        result = self.supabase.table('bns_chunks')\
            .select('*')\
            .eq('section_number', section_number)\
            .execute()

        return result.data

    def get_section_details(self, section_number: str) -> Dict:
        """Get complete section details from bns_sections table"""

        result = self.supabase.table('bns_sections')\
            .select('*')\
            .eq('section_number', section_number)\
            .execute()

        if result.data:
            return result.data[0]
        return None


# Convenience function
def search_bns_sections(query: str, top_k: int = 10) -> List[Dict]:
    """Quick search function"""
    searcher = BNSVectorSearch()
    return searcher.search(query, top_k=top_k)
