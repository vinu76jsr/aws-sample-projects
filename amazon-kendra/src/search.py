"""
Search Module - Querying Your Kendra Index
==========================================

WHAT THIS MODULE DOES:
This module provides functions to search (query) your Kendra index.
This is where the magic happens - users ask natural language questions
and Kendra returns intelligent answers!

HOW KENDRA SEARCH DIFFERS FROM TRADITIONAL SEARCH:
--------------------------------------------------
Traditional keyword search (like Google in 1998):
  Query: "vacation days policy"
  Result: Documents containing those exact words, ranked by frequency

Kendra's intelligent search:
  Query: "How many days off do I get per year?"
  Result: "Full-time employees receive 15 vacation days annually."
         (Direct answer extracted from HR handbook)

Kendra uses multiple ML models:
1. Query Understanding: Figures out what you're really asking
2. Semantic Search: Finds relevant content even without exact word matches
3. Answer Extraction: Pulls specific answers from documents
4. Ranking: Orders results by relevance and confidence

KENDRA RESULT TYPES:
--------------------
Kendra returns three types of results:

1. ANSWER (Highest Confidence):
   - Direct answer extracted from a document
   - Kendra is confident it found THE answer
   - Example: "The company was founded in 2010."
   - Appears at the top of results

2. QUESTION_ANSWER:
   - From FAQ-style documents
   - Matches a known question to its answer
   - Example: Q: "What's the password policy?" A: "12+ characters..."
   - Great for structured knowledge bases

3. DOCUMENT:
   - Relevant document excerpts
   - When Kendra can't find a specific answer
   - Provides context for the user to find info
   - Still uses semantic understanding

CONFIDENCE SCORES:
------------------
Each result has a confidence score indicating how sure Kendra is:
- VERY_HIGH: Kendra is highly confident
- HIGH: Good match
- MEDIUM: Moderate confidence
- LOW: Weak match (might not be relevant)

Use these scores to filter or highlight results appropriately.
"""

from .kendra_client import get_kendra_client
from .config import Config


def query(
    query_text: str,
    index_id: str = None,
    page_size: int = 10,
    page_number: int = 1,
    attribute_filter: dict = None,
) -> dict:
    """
    Query the Kendra index with natural language.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Sends a search query to Kendra and returns the results.
    This is the core search function that powers your search experience.

    HOW KENDRA PROCESSES YOUR QUERY:
    --------------------------------
    1. Query Preprocessing:
       - Tokenization (breaking into words)
       - Spell correction
       - Synonym expansion

    2. Query Understanding:
       - Intent detection (is this a question? a command?)
       - Entity extraction (people, places, dates)
       - Query reformulation

    3. Document Retrieval:
       - Semantic matching (meaning, not just keywords)
       - Vector similarity search
       - Traditional inverted index search

    4. Ranking:
       - ML-based relevance scoring
       - Recency consideration (if configured)
       - Custom boosting (if configured)

    5. Answer Extraction:
       - Identifies answer spans in documents
       - Assigns confidence scores

    Args:
        query_text (str): The natural language query.
                         Examples:
                         - "What is the vacation policy?"
                         - "How do I reset my password?"
                         - "List all products released in 2023"
                         - "troubleshooting printer problems"

        index_id (str, optional): Which index to search.
                                 Defaults to KENDRA_INDEX_ID from config.

        page_size (int, optional): Number of results per page.
                                  Default: 10. Max: 100.
                                  Fewer results = faster response.

        page_number (int, optional): Which page of results to return.
                                    1-indexed (first page is 1, not 0).
                                    Use for pagination in UI.

        attribute_filter (dict, optional): Filter results by document attributes.
                         Powerful for restricting searches to specific categories.
                         See FILTERING EXAMPLES below.

    Returns:
        dict: Full Kendra query response containing:
            {
                'QueryId': 'unique-query-id',      # Useful for analytics
                'TotalNumberOfResults': 150,       # Total matches (for pagination)

                'ResultItems': [                   # The actual results
                    {
                        'Id': 'result-id',
                        'Type': 'ANSWER',          # ANSWER, QUESTION_ANSWER, or DOCUMENT
                        'DocumentId': 'doc-001',
                        'DocumentTitle': {'Text': 'Vacation Policy'},
                        'DocumentExcerpt': {'Text': '...relevant text...'},
                        'DocumentURI': 'https://...',
                        'ScoreAttributes': {
                            'ScoreConfidence': 'HIGH'  # Confidence level
                        },
                        'AdditionalAttributes': [...],  # Answer text for ANSWER type
                        ...
                    },
                    ...
                ],

                'FacetResults': [...],             # Facet counts (if configured)
                'ResponseMetadata': {...}          # AWS metadata
            }

    FILTERING EXAMPLES:
    -------------------
    Filter by single attribute:
    >>> filter = {
    ...     "EqualsTo": {
    ...         "Key": "_category",
    ...         "Value": {"StringValue": "HR"}
    ...     }
    ... }
    >>> query("vacation policy", attribute_filter=filter)

    Filter with multiple conditions (AND):
    >>> filter = {
    ...     "AndAllFilters": [
    ...         {"EqualsTo": {"Key": "_category", "Value": {"StringValue": "HR"}}},
    ...         {"GreaterThan": {"Key": "_created_at", "Value": {"DateValue": "2023-01-01"}}}
    ...     ]
    ... }

    Filter with OR conditions:
    >>> filter = {
    ...     "OrAllFilters": [
    ...         {"EqualsTo": {"Key": "_category", "Value": {"StringValue": "HR"}}},
    ...         {"EqualsTo": {"Key": "_category", "Value": {"StringValue": "IT"}}}
    ...     ]
    ... }

    QUERY TIPS:
    -----------
    - Use natural questions: "What is X?" works better than just "X"
    - Be specific: "Q3 2023 sales report" vs "sales report"
    - Include context: "Python error handling" vs just "error handling"
    """
    client = get_kendra_client()
    index_id = index_id or Config.KENDRA_INDEX_ID

    # ==========================================================================
    # BUILD QUERY PARAMETERS
    # ==========================================================================
    # We build a params dict and then unpack it into the API call.
    # This pattern makes it easy to add optional parameters conditionally.
    params = {
        "IndexId": index_id,      # Which index to search
        "QueryText": query_text,   # The user's search query
        "PageSize": page_size,     # How many results to return
        "PageNumber": page_number,  # Which page (for pagination)
    }

    # ==========================================================================
    # OPTIONAL: Add attribute filter
    # ==========================================================================
    # Filters restrict results to documents matching specific criteria.
    # This is useful for:
    # - Multi-tenant systems (filter by tenant_id)
    # - Category-based search (filter by department)
    # - Date-restricted search (only recent documents)
    if attribute_filter:
        params["AttributeFilter"] = attribute_filter

    # ==========================================================================
    # EXECUTE THE QUERY
    # ==========================================================================
    # **params unpacks the dictionary into keyword arguments
    # Equivalent to: client.query(IndexId=index_id, QueryText=query_text, ...)
    response = client.query(**params)

    return response


def format_results(response: dict) -> list:
    """
    Format raw Kendra query response into a cleaner structure.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Takes the complex Kendra API response and extracts the most
    useful information into a simpler format. This makes it easier
    to display results in a UI or process them programmatically.

    WHY IS THIS NEEDED?
    -------------------
    Kendra's raw response is verbose and deeply nested. For example,
    getting a document title requires: item['DocumentTitle']['Text']

    This function simplifies that to just: result['title']

    It also handles:
    - Missing fields gracefully (using .get() with defaults)
    - Different result types (ANSWER vs DOCUMENT)
    - Extracting the answer text from ANSWER type results

    Args:
        response (dict): Raw response from the query() function.

    Returns:
        list: List of simplified result dictionaries:
            [
                {
                    'id': 'doc-001',           # Document ID
                    'title': 'Vacation Policy', # Document title
                    'type': 'ANSWER',          # Result type
                    'score': 'HIGH',           # Confidence score
                    'excerpt': '...',          # Text excerpt
                    'answer': '...'            # Only for ANSWER type
                },
                ...
            ]

    EXAMPLE USAGE:
    --------------
    >>> response = query("What is the vacation policy?")
    >>> results = format_results(response)
    >>> for r in results:
    ...     print(f"{r['title']}: {r.get('answer', r['excerpt'])}")
    """
    results = []

    # ==========================================================================
    # ITERATE THROUGH RESULT ITEMS
    # ==========================================================================
    # ResultItems contains all the matched documents/answers.
    # .get() with default [] handles case where no results found.
    for item in response.get("ResultItems", []):

        # Build our simplified result structure
        result = {
            # Document ID - useful for fetching full document later
            "id": item.get("DocumentId"),

            # Document title - for display in search results
            # Nested structure: {'DocumentTitle': {'Text': 'actual title'}}
            "title": item.get("DocumentTitle", {}).get("Text", "No title"),

            # Result type: ANSWER, QUESTION_ANSWER, or DOCUMENT
            # Important for knowing how to display the result
            "type": item.get("Type"),

            # Confidence score: VERY_HIGH, HIGH, MEDIUM, LOW, or NOT_AVAILABLE
            # Use this to style results (e.g., highlight high-confidence answers)
            "score": item.get("ScoreAttributes", {}).get("ScoreConfidence"),
        }

        # ======================================================================
        # EXTRACT DOCUMENT EXCERPT
        # ======================================================================
        # The excerpt is a snippet of the document showing relevant content.
        # Useful when the result is type DOCUMENT (no direct answer).
        if item.get("DocumentExcerpt"):
            result["excerpt"] = item["DocumentExcerpt"].get("Text", "")

        # ======================================================================
        # EXTRACT ANSWER TEXT (for ANSWER type results)
        # ======================================================================
        # When Kendra finds a direct answer, it's stored in AdditionalAttributes.
        # This is the "magic" of Kendra - extracting specific answers.
        #
        # Structure:
        # AdditionalAttributes: [
        #     {
        #         'Key': 'AnswerText',
        #         'Value': {
        #             'TextWithHighlightsValue': {
        #                 'Text': 'The answer is...',
        #                 'Highlights': [...]  # Word positions to highlight
        #             }
        #         }
        #     }
        # ]
        if item.get("AdditionalAttributes"):
            for attr in item["AdditionalAttributes"]:
                if attr["Key"] == "AnswerText":
                    # Navigate the nested structure to get the actual text
                    result["answer"] = (
                        attr["Value"]
                        .get("TextWithHighlightsValue", {})
                        .get("Text", "")
                    )

        results.append(result)

    return results


def search_and_print(query_text: str, index_id: str = None) -> list:
    """
    Convenience function to search and print formatted results.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Combines query() and format_results() into a single call that
    also prints nicely formatted output. Great for testing and demos.

    This is a "convenience function" or "helper function" - it doesn't
    add new functionality, just makes common operations easier.

    Args:
        query_text (str): The search query to execute.
        index_id (str, optional): Which index to search.

    Returns:
        list: Formatted results (same as format_results()).

    OUTPUT FORMAT:
    --------------
    The function prints results like:

    Search results for: 'What is Kendra?'
    Total results: 3
    --------------------------------------------------

    1. Amazon Kendra Overview
       Type: ANSWER | Confidence: VERY_HIGH
       Answer: Amazon Kendra is an intelligent search service...

    2. Getting Started Guide
       Type: DOCUMENT | Confidence: HIGH
       Excerpt: Learn how to set up Amazon Kendra for your...

    EXAMPLE USAGE:
    --------------
    >>> # Quick way to test your index
    >>> search_and_print("How do I reset my password?")

    >>> # Or use in a loop for multiple queries
    >>> test_queries = [
    ...     "What is Kendra?",
    ...     "How to add documents?",
    ...     "What file types are supported?"
    ... ]
    >>> for q in test_queries:
    ...     search_and_print(q)
    ...     print()  # Blank line between results
    """
    # Execute the query
    response = query(query_text, index_id)

    # Format the results into our simpler structure
    results = format_results(response)

    # ==========================================================================
    # PRINT FORMATTED OUTPUT
    # ==========================================================================
    print(f"\nSearch results for: '{query_text}'")
    print(f"Total results: {response.get('TotalNumberOfResults', 0)}")
    print("-" * 50)

    # Enumerate gives us both the index (i) and the item (result)
    # start=1 makes the counter start at 1 instead of 0
    for i, result in enumerate(results, 1):
        # Print result number and title
        print(f"\n{i}. {result['title']}")

        # Print type and confidence score
        # .get() with 'N/A' handles missing scores
        print(f"   Type: {result['type']} | Confidence: {result.get('score', 'N/A')}")

        # Print the answer (if ANSWER type) or excerpt (if DOCUMENT type)
        # [:200] truncates to first 200 characters to keep output readable
        if result.get("answer"):
            print(f"   Answer: {result['answer'][:200]}...")
        elif result.get("excerpt"):
            print(f"   Excerpt: {result['excerpt'][:200]}...")

    return results


def get_suggestions(query_text: str, index_id: str = None, max_suggestions: int = 5) -> list:
    """
    Get query suggestions based on partial input (autocomplete).

    WHAT THIS FUNCTION DOES:
    ------------------------
    As the user types in a search box, this function provides
    suggestions for what they might be searching for. This is
    the "autocomplete" or "type-ahead" feature.

    HOW IT WORKS:
    -------------
    Kendra learns from:
    1. Documents in the index (common phrases, titles)
    2. Previous queries (what people actually search for)
    3. Query patterns (common question structures)

    Example:
    User types: "how do I res"
    Suggestions:
    - "how do I reset my password"
    - "how do I request time off"
    - "how do I resolve conflicts"

    REQUIREMENTS:
    -------------
    Query suggestions need to be ENABLED on your index:
    1. In AWS Console: Index Settings > Query Suggestions > Enable
    2. Or via API: update_query_suggestions_config()

    Suggestions improve over time as:
    - More queries are logged
    - More documents are indexed
    - Kendra learns usage patterns

    Args:
        query_text (str): The partial text the user has typed.
                         Example: "how do", "password", "vacation pol"

        index_id (str, optional): Which index to get suggestions from.

        max_suggestions (int, optional): Maximum suggestions to return.
                                        Default: 5. Max: 10.

    Returns:
        list: List of suggested query strings.
              Example: ["how do I reset password", "how do I request PTO", ...]

    EXAMPLE USAGE:
    --------------
    >>> # Simulate autocomplete as user types
    >>> suggestions = get_suggestions("how do I")
    >>> print(suggestions)
    ['how do I reset my password', 'how do I request time off', ...]

    >>> # In a web app, you might call this on each keystroke
    >>> # (with debouncing to avoid too many API calls)

    UI INTEGRATION TIP:
    -------------------
    In a real search UI:
    1. Add a debounce (e.g., wait 300ms after user stops typing)
    2. Show suggestions in a dropdown
    3. Allow keyboard navigation (arrow keys)
    4. Execute search when user selects a suggestion

    SUGGESTIONS vs SEARCH:
    ----------------------
    get_suggestions(): Returns query strings (what to search for)
    query(): Executes search and returns document results

    Suggestions are for helping users formulate their query.
    Search is for actually finding answers.
    """
    client = get_kendra_client()
    index_id = index_id or Config.KENDRA_INDEX_ID

    # Call the get_query_suggestions API
    response = client.get_query_suggestions(
        IndexId=index_id,
        QueryText=query_text,
        MaxSuggestionsCount=max_suggestions,
    )

    # ==========================================================================
    # EXTRACT SUGGESTION STRINGS
    # ==========================================================================
    # The API response is deeply nested:
    # {
    #     'Suggestions': [
    #         {
    #             'Id': 'suggestion-id',
    #             'Value': {
    #                 'Text': {
    #                     'Text': 'actual suggestion text',
    #                     'Highlights': [...]
    #                 }
    #             }
    #         }
    #     ]
    # }
    #
    # We use a list comprehension to extract just the text strings.
    suggestions = [
        s.get("Value", {}).get("Text", {}).get("Text", "")
        for s in response.get("Suggestions", [])
    ]

    return suggestions


# =============================================================================
# LEARNING EXERCISES:
# =============================================================================
#
# EXERCISE 1: Basic search
# ------------------------
# >>> from src.search import search_and_print
# >>>
# >>> # Try different query styles
# >>> search_and_print("What is Amazon Kendra?")  # Question format
# >>> search_and_print("Amazon Kendra features")   # Keyword format
# >>> search_and_print("intelligent search")       # Conceptual search
#
#
# EXERCISE 2: Understand result types
# -----------------------------------
# >>> from src.search import query, format_results
# >>>
# >>> response = query("What is the password policy?")
# >>> results = format_results(response)
# >>>
# >>> # Group results by type
# >>> for result in results:
# ...     print(f"Type: {result['type']}, Score: {result['score']}")
# ...     if result['type'] == 'ANSWER':
# ...         print(f"  ANSWER: {result.get('answer')}")
# ...     else:
# ...         print(f"  Excerpt: {result.get('excerpt')[:100]}...")
#
#
# EXERCISE 3: Filtering results
# -----------------------------
# >>> # Search only HR documents
# >>> hr_filter = {
# ...     "EqualsTo": {
# ...         "Key": "_category",
# ...         "Value": {"StringValue": "HR"}
# ...     }
# ... }
# >>>
# >>> response = query("vacation policy", attribute_filter=hr_filter)
# >>> # Now results only include HR documents!
#
#
# EXERCISE 4: Pagination
# ----------------------
# >>> # Get page 1 with 5 results
# >>> page1 = query("Kendra", page_size=5, page_number=1)
# >>> print(f"Total: {page1['TotalNumberOfResults']}, Showing page 1")
# >>>
# >>> # Get page 2
# >>> page2 = query("Kendra", page_size=5, page_number=2)
# >>> print("Page 2 results:")
# >>> for item in page2['ResultItems']:
# ...     print(f"  - {item['DocumentTitle']['Text']}")
#
#
# ADVANCED TOPIC: Query Analytics
# -------------------------------
# Kendra provides query analytics via CloudWatch:
# - Query latency
# - Result click-through rates
# - Zero-result queries
# - Popular queries
#
# Use these to:
# - Identify content gaps (queries with no good results)
# - Improve document quality
# - Add FAQs for common questions
# - Tune relevance settings
#
# Access via: AWS Console > Kendra > Your Index > Analytics
#
# =============================================================================


# =============================================================================
# FEEDBACK SUBMISSION FUNCTIONS
# =============================================================================
# These functions allow you to submit user interaction data back to Kendra,
# which helps improve search relevance over time.


def submit_click_feedback(
    query_id: str,
    result_id: str,
    click_time: "datetime" = None,
    index_id: str = None,
) -> dict:
    """
    Submit click feedback when a user clicks on a search result.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Tells Kendra that a user clicked on a specific search result.
    Kendra uses this information to improve ranking over time -
    results that get clicked more often are considered more relevant.

    WHY CLICK FEEDBACK MATTERS:
    ---------------------------
    - Improves ML ranking models through implicit feedback
    - Helps Kendra learn which results are actually useful
    - No user action required beyond natural clicking behavior
    - Provides data for analytics dashboards

    HOW TO CAPTURE CLICKS:
    ----------------------
    In a typical search UI:
    1. User submits a query → you get QueryId from response
    2. User sees results → each has a ResultId (Id field)
    3. User clicks a result → call this function
    4. Kendra records the feedback

    Args:
        query_id (str): The QueryId from the original search response.
                       Found in: response['QueryId']
                       This links the click to the specific query.

        result_id (str): The Id of the clicked result item.
                        Found in: response['ResultItems'][n]['Id']
                        NOT the DocumentId - use the result's Id.

        click_time (datetime, optional): When the click occurred.
                                        Defaults to current time.
                                        Useful for batch processing clicks.

        index_id (str, optional): Which index this feedback is for.

    Returns:
        dict: Empty response with just ResponseMetadata on success.

    EXAMPLE USAGE:
    --------------
    >>> from src.search import query, submit_click_feedback
    >>>
    >>> # User searches
    >>> response = query("How do I reset my password?")
    >>> query_id = response['QueryId']
    >>>
    >>> # Display results to user...
    >>> # User clicks on the first result
    >>> clicked_result = response['ResultItems'][0]
    >>> result_id = clicked_result['Id']
    >>>
    >>> # Submit click feedback
    >>> submit_click_feedback(query_id, result_id)
    Click feedback submitted for result: abc123...

    INTEGRATION EXAMPLE (Web App):
    ------------------------------
    In a web application, you might:

    1. Store query_id in session/state when displaying results
    2. Add click handlers to result links
    3. When clicked, send feedback before navigating:

    ```javascript
    // Frontend pseudocode
    function handleResultClick(resultId) {
        fetch('/api/feedback/click', {
            method: 'POST',
            body: JSON.stringify({
                queryId: sessionStorage.getItem('lastQueryId'),
                resultId: resultId
            })
        });
        // Then navigate to the document
    }
    ```
    """
    from datetime import datetime, timezone

    client = get_kendra_client()
    index_id = index_id or Config.KENDRA_INDEX_ID

    # Use provided time or current UTC time
    if click_time is None:
        click_time = datetime.now(timezone.utc)

    # Submit the click feedback
    response = client.submit_feedback(
        IndexId=index_id,
        QueryId=query_id,
        ClickFeedbackItems=[
            {
                "ResultId": result_id,
                "ClickTime": click_time,
            }
        ],
    )

    print(f"Click feedback submitted for result: {result_id[:20]}...")
    return response


def submit_relevance_feedback(
    query_id: str,
    result_id: str,
    is_relevant: bool,
    index_id: str = None,
) -> dict:
    """
    Submit explicit relevance feedback for a search result.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Tells Kendra whether a specific result was relevant or not.
    This is EXPLICIT feedback - the user actively indicates quality,
    unlike click feedback which is implicit.

    RELEVANCE FEEDBACK USE CASES:
    -----------------------------
    - Thumbs up/down buttons on search results
    - "Was this helpful?" prompts after viewing a document
    - Admin curation of search quality
    - Quality assurance workflows

    RELEVANT vs NOT_RELEVANT:
    -------------------------
    RELEVANT: The result answered the user's question or was useful
    NOT_RELEVANT: The result was off-topic or unhelpful

    This feedback is more valuable than click feedback because:
    - It's explicit (user made a conscious choice)
    - It captures negative signals (clicks don't capture "bad" results)
    - It can correct ranking mistakes directly

    Args:
        query_id (str): The QueryId from the original search response.

        result_id (str): The Id of the result being rated.
                        Found in: response['ResultItems'][n]['Id']

        is_relevant (bool): True if the result was relevant/helpful,
                           False if it was not relevant/unhelpful.

        index_id (str, optional): Which index this feedback is for.

    Returns:
        dict: Empty response with just ResponseMetadata on success.

    EXAMPLE USAGE:
    --------------
    >>> from src.search import query, submit_relevance_feedback
    >>>
    >>> # User searches and views a result
    >>> response = query("vacation policy")
    >>> query_id = response['QueryId']
    >>> result_id = response['ResultItems'][0]['Id']
    >>>
    >>> # User clicks thumbs up - result was helpful
    >>> submit_relevance_feedback(query_id, result_id, is_relevant=True)
    Relevance feedback submitted: RELEVANT for result abc123...
    >>>
    >>> # Or thumbs down - result was not helpful
    >>> submit_relevance_feedback(query_id, result_id, is_relevant=False)
    Relevance feedback submitted: NOT_RELEVANT for result abc123...

    UI IMPLEMENTATION TIP:
    ----------------------
    Common patterns for collecting relevance feedback:

    1. Thumbs up/down icons next to each result
    2. Star ratings (map 4-5 stars → RELEVANT, 1-2 → NOT_RELEVANT)
    3. "Was this helpful? Yes/No" after document view
    4. Report button (map to NOT_RELEVANT)

    Remember to store query_id when displaying results so you can
    submit feedback even after the user navigates away.
    """
    client = get_kendra_client()
    index_id = index_id or Config.KENDRA_INDEX_ID

    # Convert boolean to Kendra's relevance value enum
    relevance_value = "RELEVANT" if is_relevant else "NOT_RELEVANT"

    # Submit the relevance feedback
    response = client.submit_feedback(
        IndexId=index_id,
        QueryId=query_id,
        RelevanceFeedbackItems=[
            {
                "ResultId": result_id,
                "RelevanceValue": relevance_value,
            }
        ],
    )

    print(f"Relevance feedback submitted: {relevance_value} for result {result_id[:20]}...")
    return response


def submit_feedback(
    query_id: str,
    click_items: list = None,
    relevance_items: list = None,
    index_id: str = None,
) -> dict:
    """
    Submit multiple feedback items in a single API call.

    WHAT THIS FUNCTION DOES:
    ------------------------
    A flexible function that can submit multiple click and/or relevance
    feedback items at once. Useful for batch processing or when you have
    both types of feedback to submit.

    WHEN TO USE THIS vs INDIVIDUAL FUNCTIONS:
    -----------------------------------------
    Use submit_click_feedback(): Single click event in real-time
    Use submit_relevance_feedback(): Single thumbs up/down in real-time
    Use submit_feedback(): Batch processing, multiple items, mixed types

    Args:
        query_id (str): The QueryId from the original search response.

        click_items (list, optional): List of click feedback items.
            Each item is a dict with:
            - "ResultId" (str): The result that was clicked
            - "ClickTime" (datetime, optional): When clicked

        relevance_items (list, optional): List of relevance feedback items.
            Each item is a dict with:
            - "ResultId" (str): The result being rated
            - "RelevanceValue" (str): "RELEVANT" or "NOT_RELEVANT"

        index_id (str, optional): Which index this feedback is for.

    Returns:
        dict: Empty response with ResponseMetadata on success.

    EXAMPLE USAGE:
    --------------
    >>> from datetime import datetime, timezone
    >>> from src.search import query, submit_feedback
    >>>
    >>> response = query("password reset")
    >>> query_id = response['QueryId']
    >>>
    >>> # Submit mixed feedback in one call
    >>> submit_feedback(
    ...     query_id=query_id,
    ...     click_items=[
    ...         {"ResultId": response['ResultItems'][0]['Id']},
    ...         {"ResultId": response['ResultItems'][2]['Id']},
    ...     ],
    ...     relevance_items=[
    ...         {"ResultId": response['ResultItems'][0]['Id'], "RelevanceValue": "RELEVANT"},
    ...         {"ResultId": response['ResultItems'][1]['Id'], "RelevanceValue": "NOT_RELEVANT"},
    ...     ]
    ... )

    BATCH PROCESSING EXAMPLE:
    -------------------------
    If you're processing feedback from logs or analytics:

    >>> # Collected feedback from user sessions
    >>> session_feedback = [
    ...     {"query_id": "q1", "result_id": "r1", "clicked": True, "rated": "RELEVANT"},
    ...     {"query_id": "q1", "result_id": "r2", "clicked": False, "rated": "NOT_RELEVANT"},
    ... ]
    >>>
    >>> # Group by query_id and submit
    >>> for query_id, items in group_by_query(session_feedback):
    ...     clicks = [{"ResultId": i["result_id"]} for i in items if i["clicked"]]
    ...     ratings = [{"ResultId": i["result_id"], "RelevanceValue": i["rated"]}
    ...                for i in items if i.get("rated")]
    ...     submit_feedback(query_id, click_items=clicks, relevance_items=ratings)
    """
    from datetime import datetime, timezone

    client = get_kendra_client()
    index_id = index_id or Config.KENDRA_INDEX_ID

    # Build the API call parameters
    params = {
        "IndexId": index_id,
        "QueryId": query_id,
    }

    # Add click feedback items if provided
    if click_items:
        # Ensure each item has a ClickTime
        for item in click_items:
            if "ClickTime" not in item:
                item["ClickTime"] = datetime.now(timezone.utc)
        params["ClickFeedbackItems"] = click_items

    # Add relevance feedback items if provided
    if relevance_items:
        params["RelevanceFeedbackItems"] = relevance_items

    # Submit all feedback
    response = client.submit_feedback(**params)

    # Report what was submitted
    click_count = len(click_items) if click_items else 0
    relevance_count = len(relevance_items) if relevance_items else 0
    print(f"Feedback submitted: {click_count} clicks, {relevance_count} relevance ratings")

    return response


# =============================================================================
# ADVANCED TOPIC: Relevance Tuning
# =============================================================================
# You can customize how Kendra ranks results:
#
# 1. Document Attribute Boosting:
#    - Prioritize recent documents
#    - Boost documents from certain categories
#
#    >>> client.update_index(
#    ...     Id=index_id,
#    ...     DocumentMetadataConfigurationUpdates=[
#    ...         {
#    ...             'Name': '_created_at',
#    ...             'Relevance': {
#    ...                 'Freshness': True,  # Newer = higher rank
#    ...             }
#    ...         }
#    ...     ]
#    ... )
#
# 2. Featured Results:
#    - Pin specific documents for certain queries
#    - Useful for ensuring key content surfaces
#
# 3. Custom Ranking Expressions:
#    - Complex ranking formulas
#    - Combine multiple signals
#
# Learn more: AWS Kendra Developer Guide > Tuning Search Relevance
# =============================================================================


# =============================================================================
# FEEDBACK LEARNING EXERCISES:
# =============================================================================
#
# EXERCISE 5: Submit click feedback
# ---------------------------------
# >>> from src.search import query, submit_click_feedback
# >>>
# >>> # Perform a search
# >>> response = query("What is Amazon Kendra?")
# >>> query_id = response['QueryId']
# >>>
# >>> # Simulate user clicking on first result
# >>> if response['ResultItems']:
# ...     result_id = response['ResultItems'][0]['Id']
# ...     submit_click_feedback(query_id, result_id)
#
#
# EXERCISE 6: Submit relevance feedback
# -------------------------------------
# >>> from src.search import query, submit_relevance_feedback
# >>>
# >>> response = query("password policy")
# >>> query_id = response['QueryId']
# >>>
# >>> # User found first result helpful
# >>> if response['ResultItems']:
# ...     result_id = response['ResultItems'][0]['Id']
# ...     submit_relevance_feedback(query_id, result_id, is_relevant=True)
# >>>
# >>> # User found second result not helpful
# >>> if len(response['ResultItems']) > 1:
# ...     result_id = response['ResultItems'][1]['Id']
# ...     submit_relevance_feedback(query_id, result_id, is_relevant=False)
#
#
# EXERCISE 7: Build a feedback-enabled search function
# ----------------------------------------------------
# This exercise combines search with automatic feedback collection:
#
# >>> def interactive_search(query_text):
# ...     """Search and collect feedback interactively."""
# ...     from src.search import query, format_results, submit_click_feedback
# ...
# ...     response = query(query_text)
# ...     query_id = response['QueryId']
# ...     results = format_results(response)
# ...
# ...     # Display results
# ...     for i, r in enumerate(results, 1):
# ...         print(f"{i}. {r['title']}")
# ...
# ...     # Get user's choice
# ...     choice = input("Enter result number to view (or 'q' to quit): ")
# ...     if choice.isdigit():
# ...         idx = int(choice) - 1
# ...         if 0 <= idx < len(response['ResultItems']):
# ...             result_id = response['ResultItems'][idx]['Id']
# ...             submit_click_feedback(query_id, result_id)
# ...             print(f"\nViewing: {results[idx]['title']}")
# ...             print(results[idx].get('answer') or results[idx].get('excerpt'))
# ...
# >>> # Try it:
# >>> interactive_search("How do I request time off?")
#
#
# BEST PRACTICES FOR FEEDBACK COLLECTION:
# ---------------------------------------
# 1. Always store query_id with search results in your session/state
# 2. Submit click feedback immediately (don't wait for page unload)
# 3. Use debouncing for relevance feedback UI to avoid accidental clicks
# 4. Consider privacy: anonymize feedback if needed
# 5. Monitor feedback volume in CloudWatch to ensure collection is working
#
# =============================================================================
