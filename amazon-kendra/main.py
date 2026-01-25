"""
Amazon Kendra Sample Project - Main Entry Point
================================================

WHAT IS THIS FILE?
------------------
This is the main entry point for the Amazon Kendra sample project.
It demonstrates how to use the various modules to:
1. List existing Kendra indexes
2. Add sample documents to an index
3. Search for information using natural language

HOW TO RUN THIS FILE:
---------------------
From the project root directory:
    $ python main.py

Or in Python interactive mode:
    >>> from main import main
    >>> main()

PREREQUISITES:
--------------
Before running this file, ensure you have:

1. AWS credentials configured (one of these methods):
   - Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
   - AWS credentials file: ~/.aws/credentials
   - IAM role (if running on AWS infrastructure)

2. A .env file with required settings (copy from .env.example):
   - KENDRA_INDEX_ID: Your Kendra index ID (required for most operations)
   - KENDRA_ROLE_ARN: IAM role ARN (required for creating indexes)
   - AWS_REGION: Optional, defaults to us-east-1

3. Python dependencies installed:
   $ pip install -r requirements.txt

UNDERSTANDING THE DEMO FUNCTIONS:
---------------------------------
This file contains three demo functions that showcase different Kendra capabilities:

1. demo_list_indexes(): Shows how to discover existing indexes
   - No index ID required
   - Good starting point to see what you have

2. demo_add_sample_documents(): Adds test content to search
   - Requires KENDRA_INDEX_ID
   - Documents are indexed asynchronously (wait before searching)

3. demo_search(): Demonstrates natural language search
   - Requires KENDRA_INDEX_ID with documents
   - Shows Kendra's ML-powered search in action

PROJECT ARCHITECTURE OVERVIEW:
------------------------------
This project follows a modular architecture:

    main.py                 <-- You are here (entry point & demos)
        |
        ├── src/config.py         <-- Configuration loading
        ├── src/kendra_client.py  <-- AWS client factory
        ├── src/index_manager.py  <-- Index CRUD operations
        ├── src/document_manager.py <-- Document ingestion
        └── src/search.py         <-- Search/query functions

Each module has a single responsibility (Single Responsibility Principle).
This makes the code easier to test, maintain, and understand.
"""

# =============================================================================
# IMPORTS
# =============================================================================
# We import specific functions from each module rather than importing entire modules.
# This makes it clear exactly what we're using and where it comes from.
#
# Pattern: from module import function1, function2
# vs: import module  # then use module.function1()
#
# Both are valid, but explicit imports make dependencies clearer.

from src.index_manager import list_indexes, describe_index, create_index
from src.document_manager import add_documents, delete_documents
from src.search import (
    search_and_print,
    query,
    format_results,
    submit_click_feedback,
    submit_relevance_feedback,
)
from src.config import Config


def demo_list_indexes():
    """
    Demonstrate how to list all Kendra indexes in your AWS account.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Queries AWS to find all Kendra indexes you have access to.
    This is useful for:
    - Discovering existing indexes
    - Finding the index ID you need
    - Checking index status

    WHY THIS IS USEFUL FOR LEARNING:
    --------------------------------
    This is the safest demo function - it only reads data, doesn't modify anything.
    Run this first to understand what indexes exist before doing other operations.

    EXPECTED OUTPUT:
    ----------------
    === Listing Kendra Indexes ===
    - My-Index (ID: abc123-..., Status: ACTIVE)
    - Test-Index (ID: def456-..., Status: CREATING)

    OR if no indexes:

    === Listing Kendra Indexes ===
    No indexes found in your account.
    """
    # Print a header to make output readable
    # The \n creates a blank line before the header for visual separation
    print("\n=== Listing Kendra Indexes ===")

    # Call our list_indexes function from the index_manager module
    # This returns a list of dictionaries, each representing an index
    indexes = list_indexes()

    # Check if the list is empty (no indexes found)
    # In Python, empty lists are "falsy", so "if not indexes:" is True for []
    if not indexes:
        print("No indexes found in your account.")
        # Early return - exit the function here, no need for else block
        return

    # Iterate through each index and print its details
    # Each idx is a dictionary with keys: Name, Id, Status, Edition, etc.
    for idx in indexes:
        # f-strings (formatted string literals) allow embedding expressions
        # Syntax: f"text {variable} more text {expression}"
        print(f"- {idx['Name']} (ID: {idx['Id']}, Status: {idx['Status']})")


def demo_add_sample_documents():
    """
    Demonstrate how to add documents to a Kendra index.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Adds three sample documents about Amazon Kendra to your index.
    After adding, these documents become searchable (after indexing completes).

    IMPORTANT TIMING NOTE:
    ----------------------
    Document indexing is ASYNCHRONOUS. After this function returns:
    - Documents are submitted for processing
    - Kendra processes them in the background
    - They become searchable after 1-5 minutes

    If you search immediately after, you might not find them yet!

    SAMPLE DOCUMENTS CREATED:
    -------------------------
    1. "Getting Started with Amazon Kendra" - Overview of Kendra
    2. "Kendra Data Sources" - Information about data connectors
    3. "Kendra Query Types" - Explanation of result types

    WHY THESE DOCUMENTS?
    --------------------
    These documents are designed to:
    - Cover different topics (for varied search results)
    - Contain structured information (to demonstrate answer extraction)
    - Be self-referential (you can ask "What is Kendra?" and get answers)
    """
    print("\n=== Adding Sample Documents ===")

    # Define our sample documents as a list of dictionaries
    # Each document needs at minimum: Id, Content
    # Title is optional but highly recommended for display purposes
    sample_docs = [
        {
            # Id: Unique identifier for this document
            # Use descriptive IDs that help you identify documents later
            # Avoid using just numbers - "doc-001" is better than "1"
            "Id": "doc-001",

            # Title: Displayed in search results
            # Make titles descriptive and searchable
            "Title": "Getting Started with Amazon Kendra",

            # Content: The actual text that Kendra will index and search
            # Can be plain text, and Kendra will understand the meaning
            # Triple-quoted strings (''') allow multi-line content
            "Content": """
            Amazon Kendra is an intelligent search service powered by machine learning.
            It provides natural language search capabilities for your enterprise data.
            Kendra can index documents from various sources including S3, SharePoint,
            databases, and more. It understands context and returns precise answers
            rather than just a list of documents.
            """,
        },
        {
            "Id": "doc-002",
            "Title": "Kendra Data Sources",
            "Content": """
            Amazon Kendra supports multiple data source connectors:
            - Amazon S3: Index documents stored in S3 buckets
            - SharePoint: Connect to SharePoint Online or Server
            - Salesforce: Index Salesforce knowledge articles
            - ServiceNow: Connect to ServiceNow catalogs
            - Database: Connect to RDS and other databases
            - Custom: Use the BatchPutDocument API for custom sources
            Each data source can be synced on a schedule to keep content up to date.
            """,
        },
        {
            "Id": "doc-003",
            "Title": "Kendra Query Types",
            "Content": """
            Amazon Kendra supports several types of search results:
            - ANSWER: Direct answers extracted from documents
            - QUESTION_ANSWER: FAQ-style question and answer pairs
            - DOCUMENT: Relevant document excerpts
            Kendra uses machine learning to understand query intent and provide
            the most relevant type of result. You can also use filters to narrow
            results based on document attributes like date, category, or custom fields.
            """,
        },
    ]

    # ==========================================================================
    # CONFIGURATION CHECK
    # ==========================================================================
    # Before trying to add documents, verify that we have an index ID
    # This prevents confusing errors from the API
    if not Config.KENDRA_INDEX_ID:
        print("Error: KENDRA_INDEX_ID not configured. Set it in .env file.")
        # Return early - can't proceed without an index
        return

    # Add the documents to Kendra
    # This function handles formatting and API calls
    response = add_documents(sample_docs)

    # Return the response in case the caller wants to inspect it
    # This is optional but makes the function more flexible
    return response


def demo_search():
    """
    Demonstrate Kendra's natural language search capabilities.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Executes several sample queries against your Kendra index to
    demonstrate how Kendra understands and responds to natural language.

    QUERY EXAMPLES:
    ---------------
    1. "What is Amazon Kendra?"
       - Tests basic question answering
       - Should return an ANSWER type result with direct answer

    2. "What data sources does Kendra support?"
       - Tests information retrieval
       - Should list the data source connectors

    3. "How does Kendra search work?"
       - Tests conceptual understanding
       - Should explain Kendra's search mechanism

    LEARNING POINTS:
    ----------------
    Watch for:
    - Different result types (ANSWER vs DOCUMENT)
    - Confidence scores (VERY_HIGH, HIGH, etc.)
    - How Kendra extracts specific answers
    - Relevance of returned excerpts

    TRY YOUR OWN QUERIES:
    ---------------------
    After running this demo, try searching interactively:

    >>> from src.search import search_and_print
    >>> search_and_print("your question here")
    """
    print("\n=== Search Demo ===")

    # Check configuration before attempting to search
    if not Config.KENDRA_INDEX_ID:
        print("Error: KENDRA_INDEX_ID not configured. Set it in .env file.")
        return

    # Define a list of sample queries to demonstrate
    # These are designed to match the sample documents we added
    queries = [
        "What is Amazon Kendra?",           # Basic question
        "What data sources does Kendra support?",  # List-type question
        "How does Kendra search work?",     # Conceptual question
    ]

    # Execute each query and display results
    for q in queries:
        # search_and_print() handles the query, formatting, and output
        # It's a convenience function that combines multiple steps
        search_and_print(q)

        # Print an empty line between results for readability
        print()


def demo_feedback():
    """
    Demonstrate how to submit user feedback to Kendra.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Shows how to capture and submit user interaction feedback to Kendra.
    This feedback helps Kendra improve search relevance over time.

    TWO TYPES OF FEEDBACK:
    ----------------------
    1. Click Feedback: When a user clicks on a search result
       - Implicit signal (user naturally clicks)
       - Tells Kendra which results are engaging

    2. Relevance Feedback: Explicit thumbs up/down
       - Explicit signal (user actively rates)
       - Tells Kendra if results were actually helpful

    WHY FEEDBACK MATTERS:
    ---------------------
    - Improves ML ranking models over time
    - Helps identify content gaps
    - Provides analytics data
    - Makes search better for all users

    REAL-WORLD INTEGRATION:
    -----------------------
    In a production search UI:
    1. Store query_id when displaying results
    2. Track clicks on result links
    3. Add thumbs up/down buttons
    4. Submit feedback to Kendra
    """
    print("\n=== Feedback Submission Demo ===")

    # Check configuration
    if not Config.KENDRA_INDEX_ID:
        print("Error: KENDRA_INDEX_ID not configured. Set it in .env file.")
        return

    # First, perform a search to get a query_id
    search_query = "What is Amazon Kendra?"
    print(f"\n1. Performing search: '{search_query}'")

    response = query(search_query)
    query_id = response["QueryId"]

    print(f"   Query ID: {query_id[:30]}...")
    print(f"   Results found: {len(response.get('ResultItems', []))}")

    # Check if we have results to provide feedback on
    if not response.get("ResultItems"):
        print("\n   No results found. Add documents first with demo_add_sample_documents()")
        return

    # Get the first result for demonstration
    first_result = response["ResultItems"][0]
    result_id = first_result["Id"]
    result_title = first_result.get("DocumentTitle", {}).get("Text", "Unknown")

    print(f"\n2. Simulating user click on: '{result_title}'")

    # Submit click feedback
    try:
        submit_click_feedback(query_id, result_id)
        print("   ✓ Click feedback submitted successfully")
    except Exception as e:
        print(f"   ✗ Error submitting click feedback: {e}")

    # Submit relevance feedback (thumbs up)
    print(f"\n3. Simulating user marking result as relevant (thumbs up)")
    try:
        submit_relevance_feedback(query_id, result_id, is_relevant=True)
        print("   ✓ Relevance feedback submitted successfully")
    except Exception as e:
        print(f"   ✗ Error submitting relevance feedback: {e}")

    # Show how to submit negative feedback
    if len(response["ResultItems"]) > 1:
        second_result = response["ResultItems"][1]
        second_id = second_result["Id"]
        second_title = second_result.get("DocumentTitle", {}).get("Text", "Unknown")

        print(f"\n4. Simulating user marking '{second_title}' as not relevant (thumbs down)")
        try:
            submit_relevance_feedback(query_id, second_id, is_relevant=False)
            print("   ✓ Negative feedback submitted successfully")
        except Exception as e:
            print(f"   ✗ Error submitting feedback: {e}")

    print("\n" + "=" * 50)
    print("Feedback demo complete!")
    print("\nIn production, you would:")
    print("- Store query_id in session state when displaying results")
    print("- Call submit_click_feedback() when user clicks a result link")
    print("- Call submit_relevance_feedback() when user clicks thumbs up/down")
    print("- View feedback analytics in AWS Console > Kendra > Analytics")


def main():
    """
    Main function that orchestrates the demo.

    WHAT THIS FUNCTION DOES:
    ------------------------
    This is the entry point when you run: python main.py

    It:
    1. Prints a welcome banner
    2. Checks configuration status
    3. Runs the demo functions

    FUNCTION CALL ORDER:
    --------------------
    We only call demo_list_indexes() by default because:
    - It's safe (read-only operation)
    - It works without a configured index ID
    - It helps you discover your indexes

    The other demos are commented out because:
    - demo_add_sample_documents() adds data (might not want to pollute index)
    - demo_search() requires documents to be indexed first

    HOW TO RUN ALL DEMOS:
    ---------------------
    1. Uncomment the lines at the bottom of this function
    2. Run: python main.py

    Or run demos individually in Python:
    >>> from main import demo_list_indexes, demo_search
    >>> demo_list_indexes()
    >>> demo_search()
    """
    # ==========================================================================
    # WELCOME BANNER
    # ==========================================================================
    # Print a nice header to identify the program
    # "=" * 50 creates a string of 50 equal signs (string multiplication)
    print("Amazon Kendra Sample Project")
    print("=" * 50)

    # ==========================================================================
    # CONFIGURATION STATUS CHECK
    # ==========================================================================
    # Check if the required configuration is present
    # This helps users understand what they need to set up
    if not Config.KENDRA_INDEX_ID:
        # Inform the user about missing configuration
        # Multi-line print statements make the output readable
        print("\nNote: KENDRA_INDEX_ID not set in .env file.")
        print("Some operations will not work without an index.")
        print("\nTo create an index, you also need KENDRA_ROLE_ARN set.")
        # Note: We continue execution because list_indexes() works without index ID

    # ==========================================================================
    # RUN DEMONSTRATIONS
    # ==========================================================================

    # Always run the list demo - it's safe and informative
    demo_list_indexes()

    # ==========================================================================
    # ADDITIONAL DEMOS (Uncomment to run)
    # ==========================================================================
    # These are commented out by default to prevent accidental data modification.
    # Uncomment them when you're ready to test adding documents and searching.

    # Uncomment this to add sample documents to your index:
    # demo_add_sample_documents()

    # Uncomment this to test search (run after adding documents and waiting):
    # demo_search()

    # Uncomment this to test feedback submission (requires documents and search results):
    # demo_feedback()


# =============================================================================
# PYTHON ENTRY POINT PATTERN
# =============================================================================
# This is the standard Python idiom for making a script both:
# 1. Runnable directly: python main.py
# 2. Importable as a module: from main import demo_search
#
# When you run "python main.py":
# - Python sets __name__ to "__main__"
# - The if condition is True
# - main() is called
#
# When you import this file:
# - Python sets __name__ to "main" (the module name)
# - The if condition is False
# - main() is NOT called automatically
#
# This gives you flexibility to use the code either way.
# =============================================================================
if __name__ == "__main__":
    main()


# =============================================================================
# LEARNING EXERCISES:
# =============================================================================
#
# EXERCISE 1: Run the basic demo
# ------------------------------
# $ python main.py
# Observe the output and understand what indexes exist.
#
#
# EXERCISE 2: Add documents and search
# ------------------------------------
# 1. Ensure KENDRA_INDEX_ID is set in your .env file
# 2. Uncomment demo_add_sample_documents() in main()
# 3. Run: python main.py
# 4. Wait 2-3 minutes for indexing
# 5. Uncomment demo_search() in main()
# 6. Run: python main.py again
#
#
# EXERCISE 3: Interactive exploration
# -----------------------------------
# $ python
# >>> from src.search import search_and_print
# >>> search_and_print("What is Kendra?")
# >>> search_and_print("How do I add documents?")
# >>>
# >>> # Try your own questions!
# >>> search_and_print("your question here")
#
#
# EXERCISE 4: Explore the raw API response
# ----------------------------------------
# >>> from src.search import query
# >>> response = query("What is Kendra?")
# >>> print(response.keys())  # See what's in the response
# >>> print(response['TotalNumberOfResults'])
# >>> print(response['ResultItems'][0])  # First result in detail
#
#
# NEXT STEPS FOR LEARNING:
# ------------------------
# 1. Read through each module in src/ to understand the code
# 2. Experiment with different types of documents
# 3. Try filtering results by attributes
# 4. Explore the AWS Console for Kendra to see visual interface
# 5. Check out AWS documentation for advanced features
#
# =============================================================================


# =============================================================================
# TROUBLESHOOTING GUIDE:
# =============================================================================
#
# ERROR: "No credentials could be found"
# SOLUTION: Set up AWS credentials via:
#   - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
#   - AWS CLI: aws configure
#   - IAM role (if on AWS infrastructure)
#
# ERROR: "ResourceNotFoundException" when listing indexes
# SOLUTION: Verify:
#   - AWS_REGION in .env matches where your indexes are
#   - Your credentials have kendra:ListIndices permission
#
# ERROR: "KENDRA_INDEX_ID not configured"
# SOLUTION:
#   1. Create a .env file in project root
#   2. Add: KENDRA_INDEX_ID=your-index-id-here
#   3. Get index ID from AWS Console or list_indexes() output
#
# ERROR: "ValidationException" when adding documents
# SOLUTION: Check that:
#   - Document IDs are unique
#   - Content is valid UTF-8 text
#   - Content size is under 5MB per document
#
# ERROR: Search returns no results
# SOLUTION:
#   - Wait 2-5 minutes after adding documents (indexing is async)
#   - Verify documents were added: check describe_index() statistics
#   - Try broader search terms
#
# =============================================================================
