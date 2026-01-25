#!/usr/bin/env python3
"""
Cleanup script to delete AWS resources created for this sample project.

This script will delete:
- Kendra index (specified in KENDRA_INDEX_ID)

Usage:
    python cleanup.py
"""

from src.config import Config
from src.kendra_client import get_kendra_client
from src.index_manager import describe_index, delete_index


def confirm_deletion(index_id: str) -> bool:
    """
    Prompt user to confirm deletion.

    Args:
        index_id: The Kendra index ID to be deleted

    Returns:
        True if user confirms, False otherwise
    """
    print(f"\nThis will permanently delete the Kendra index: {index_id}")
    print("This action cannot be undone!\n")

    response = input("Type 'DELETE' to confirm: ")
    return response.strip() == "DELETE"


def main():
    """Main cleanup function."""

    # Check if index ID is configured
    index_id = Config.KENDRA_INDEX_ID
    if not index_id or index_id == "your_index_id":
        print("Error: KENDRA_INDEX_ID not configured in .env file")
        return

    print("=" * 50)
    print("Amazon Kendra Sample Project - Cleanup")
    print("=" * 50)

    # Get current index status
    print(f"\nChecking index: {index_id}")
    try:
        index_info = describe_index(index_id)
        print(f"  Name: {index_info.get('Name', 'N/A')}")
        print(f"  Status: {index_info.get('Status', 'N/A')}")
        print(f"  Edition: {index_info.get('Edition', 'N/A')}")
    except Exception as e:
        print(f"Error: Could not find index. It may already be deleted.")
        print(f"Details: {e}")
        return

    # Confirm deletion
    if not confirm_deletion(index_id):
        print("\nCancelled. No resources were deleted.")
        return

    # Delete the index
    print(f"\nDeleting index {index_id}...")
    try:
        delete_index(index_id)
        print("Index deletion initiated successfully!")
        print("\nNote: Index deletion takes a few minutes to complete.")
        print("You can check the status in AWS Console > Amazon Kendra")
    except Exception as e:
        print(f"Error deleting index: {e}")
        return

    print("\n" + "=" * 50)
    print("Cleanup complete!")
    print("=" * 50)
    print("\nRemember to also delete the IAM role if no longer needed:")
    print("  AWS Console > IAM > Roles > Delete 'KendraIndexRole'")


if __name__ == "__main__":
    main()