# Proposed Hierarchical BNS Structure

## Current Issues
1. Subsections (1), (2), (3) are mixed with main text
2. Clauses (a), (b), (c) are in punishment field
3. No clear hierarchy

## Proposed Structure

### Level 1: Section
```
Section 8: Amount of fine, liability in default of payment of fine, etc.
```

### Level 2: Subsections (1), (2), (3)...
```
  (1) Where no sum is expressed to which a fine may extend...
  (2) In every case of an offence-
  (3) The term for which the Court directs...
```

### Level 3: Clauses (a), (b), (c)... under subsections
```
  (2) In every case of an offence-
      (a) punishable with imprisonment as well as fine...
      (b) punishable with imprisonment or fine...
```

### Level 4: Sub-clauses (i), (ii), (iii)... under clauses
```
  (c) Imprisonment, which is of two descriptions, namely:-
      (1) Rigorous, that is, with hard labour;
      (2) Simple;
```

## JSON Structure Proposal

```json
{
  "section_number": "8",
  "title": "Amount of fine, liability in default of payment of fine, etc",

  "content": {
    "preamble": "General introduction if any",

    "subsections": [
      {
        "number": "(1)",
        "text": "Where no sum is expressed to which a fine may extend, the amount of fine to which the offender is liable is unlimited, but shall not be excessive."
      },
      {
        "number": "(2)",
        "text": "In every case of an offence-",
        "clauses": [
          {
            "label": "(a)",
            "text": "punishable with imprisonment as well as fine, in which the offender is sentenced to a fine, whether with or without imprisonment;"
          },
          {
            "label": "(b)",
            "text": "punishable with imprisonment or fine, or with fine only, in which the offender is sentenced to a fine, it shall be competent to the Court..."
          }
        ]
      },
      {
        "number": "(3)",
        "text": "The term for which the Court directs the offender to be imprisoned in default of payment of a fine shall not exceed one-fourth of the term of imprisonment which is the maximum fixed for the offence, if the offence be punishable with imprisonment as well as fine."
      }
    ]
  },

  "illustrations": [
    {
      "label": "(a)",
      "text": "A is sentenced to a fine of one thousand rupees..."
    }
  ],

  "explanations": [
    {
      "number": "1",
      "text": "It is not essential to counterfeiting..."
    }
  ],

  "metadata": {
    "category": "other",
    "severity": "very_serious",
    "keywords": ["fine", "imprisonment"]
  }
}
```

## Alternative Flatter Structure (Easier for LLM)

```json
{
  "section_number": "8",
  "title": "Amount of fine...",

  "full_text": "Complete unstructured text for embedding",

  "structured_content": {
    "8(1)": "Where no sum is expressed...",
    "8(2)": "In every case of an offence-",
    "8(2)(a)": "punishable with imprisonment as well as fine...",
    "8(2)(b)": "punishable with imprisonment or fine...",
    "8(3)": "The term for which the Court directs...",
    "8(4)": "The imprisonment which the Court imposes...",
    "8(5)": "If the offence is punishable with fine...",
    "8(5)(a)": "two months when the amount...",
    "8(5)(b)": "four months when the amount...",
    "8(5)(c)": "one year in any other case...",
    "8(6)": "The imprisonment which is imposed...",
    "8(6)(a)": "The imprisonment shall terminate...",
    "8(6)(b)": "If, before the expiration...",
    "8(7)": "The fine, or any part thereof..."
  },

  "illustrations": [...],
  "explanations": [...]
}
```

## Recommended: Hybrid Approach

Keep both for different use cases:

```json
{
  "section_number": "8",
  "title": "Amount of fine, liability in default of payment of fine, etc",

  "full_text": "Complete raw text for vector embeddings",

  "subsections": [
    {
      "id": "8(1)",
      "text": "Where no sum is expressed to which a fine may extend...",
      "level": 1
    },
    {
      "id": "8(2)",
      "text": "In every case of an offence-",
      "level": 1,
      "children": ["8(2)(a)", "8(2)(b)"]
    },
    {
      "id": "8(2)(a)",
      "text": "punishable with imprisonment as well as fine...",
      "level": 2,
      "parent": "8(2)"
    },
    {
      "id": "8(2)(b)",
      "text": "punishable with imprisonment or fine...",
      "level": 2,
      "parent": "8(2)"
    }
  ],

  "illustrations": [...],
  "explanations": [...],

  "metadata": {
    "category": "other",
    "severity": "very_serious",
    "keywords": ["fine", "imprisonment"]
  }
}
```

## Benefits

### For Vector Search:
- `full_text` field → single embedding for similarity search

### For LLM Reasoning:
- Structured `subsections` → LLM can identify exact applicable subsection
- Example: "Section 8(2)(a) applies because offense is punishable with imprisonment AND fine"

### For UI Display:
- Hierarchical structure → collapsible tree view
- Easy navigation

## Implementation

Create `reorganize_structure.py` that:
1. Parses description + punishment fields
2. Extracts subsections with regex
3. Builds hierarchy
4. Preserves full_text for embeddings
5. Outputs structured JSON

## Questions to Consider

1. **Should subsection IDs be dot notation or parentheses?**
   - Option A: "8.2.a" (easier to parse)
   - Option B: "8(2)(a)" (matches legal convention) ✅ Recommended

2. **How to handle edge cases?**
   - Sections without subsections → keep as simple text
   - Mixed numbering (some sections use 1,2,3 vs (1),(2),(3))

3. **Database storage?**
   - Store as JSONB in PostgreSQL ✅
   - Allows querying specific subsections
   - Flexible for future changes
