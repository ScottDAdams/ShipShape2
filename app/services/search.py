# app/services/search.py
from typing import List, Optional
from sqlalchemy import or_, text, func
from app.models import Item, BoatSection
from app.database import db


class SearchParser:
    def __init__(self, query_string: str):
        self.query_string = query_string

    def parse(self) -> dict:
        """Parse search query string into components"""
        terms = []
        exact_phrases = []
        current_term = []
        in_quotes = False

        # Parse the query string character by character
        i = 0
        while i < len(self.query_string):
            char = self.query_string[i]

            if char == '"':
                if in_quotes:
                    # End of exact phrase
                    exact_phrases.append(''.join(current_term).strip())
                    current_term = []
                in_quotes = not in_quotes
            elif char == '(':
                # Find matching closing parenthesis
                level = 1
                j = i + 1
                while j < len(self.query_string) and level > 0:
                    if self.query_string[j] == '(':
                        level += 1
                    elif self.query_string[j] == ')':
                        level -= 1
                    j += 1
                if level == 0:
                    sub_query = self.query_string[i + 1:j - 1]
                    terms.append(('group', sub_query))
                    i = j - 1
            elif char == ' ' and not in_quotes:
                if current_term:
                    term = ''.join(current_term).strip()
                    if term.upper() in ('AND', 'OR'):
                        terms.append(('operator', term.upper()))
                    else:
                        terms.append(('term', term))
                    current_term = []
            else:
                current_term.append(char)
            i += 1

        # Add any remaining term
        if current_term:
            term = ''.join(current_term).strip()
            if term.upper() in ('AND', 'OR'):
                terms.append(('operator', term.upper()))
            else:
                terms.append(('term', term))

        return {
            'terms': terms,
            'exact_phrases': exact_phrases
        }


class InventorySearchService:
    def __init__(self):
        self.parser = SearchParser

    def create_search_vector(self):
        """Create a combined search vector for full-text search"""
        return func.to_tsvector('english',
                                func.coalesce(Item.name, '') + ' ' +
                                func.coalesce(Item.part_number, '') + ' ' +
                                func.coalesce(Item.serial_number, '') + ' ' +
                                func.coalesce(Item.shelf, '') + ' ' +
                                func.coalesce(Item.box, '')
                                )

    def create_search_query(self, search_vector, term: str) -> text:
        """Create a search query for a single term"""
        return search_vector.match(func.plainto_tsquery('english', term))

    def search(self,
               query_string: Optional[str] = None,
               serial_number: Optional[str] = None,
               section_id: Optional[int] = None,
               sort_by: Optional[str] = None) -> List[Item]:
        """
        Perform a search across inventory items using PostgreSQL full-text search
        """
        # Start with base query
        query = Item.query

        # Add serial number filter if provided (exact or partial match)
        if serial_number:
            query = query.filter(Item.serial_number.ilike(f"%{serial_number}%"))

        # Add section filter if provided
        if section_id:
            query = query.filter(Item.boat_section_id == section_id)

        # If there's a main search query, parse and apply it
        if query_string:
            parser = self.parser(query_string)
            search_components = parser.parse()

            # Create search vector
            search_vector = self.create_search_vector()

            # Handle exact phrases
            for phrase in search_components['exact_phrases']:
                query = query.filter(self.create_search_query(search_vector, phrase))

            # Handle terms and operators
            terms = search_components['terms']
            if terms:
                filters = []
                current_filter = None
                current_operator = 'AND'

                for term_type, value in terms:
                    if term_type == 'operator':
                        current_operator = value
                    elif term_type == 'term':
                        term_filter = self.create_search_query(search_vector, value)
                        if current_filter is None:
                            current_filter = term_filter
                        else:
                            if current_operator == 'AND':
                                current_filter = current_filter & term_filter
                            else:  # OR
                                current_filter = current_filter | term_filter
                    elif term_type == 'group':
                        # Recursively handle grouped terms
                        sub_query = self.search(value)
                        if current_filter is None:
                            current_filter = sub_query
                        else:
                            if current_operator == 'AND':
                                current_filter = current_filter & sub_query
                            else:  # OR
                                current_filter = current_filter | sub_query

                if current_filter is not None:
                    query = query.filter(current_filter)

        # Apply sorting
        if sort_by == 'quantity':
            query = query.order_by(Item.quantity)
        elif sort_by == 'location':
            query = query.join(BoatSection).order_by(BoatSection.name, Item.shelf, Item.box)
        else:
            query = query.order_by(Item.name)

        return query.all()