"""
Poll and Choice models with DynamoDB operations.

DynamoDB Learning Notes - CRUD Operations:
------------------------------------------
1. put_item(): Create or replace an item
2. get_item(): Read a single item by primary key
3. update_item(): Update specific attributes of an item
4. delete_item(): Remove an item
5. query(): Find items with same partition key
6. scan(): Read all items (expensive, avoid in production)

Single-Table Design Pattern:
----------------------------
We store different entity types in the same table:

| PK            | SK              | Type    | Data                    |
|---------------|-----------------|---------|-------------------------|
| POLLS         | POLL#001        | index   | poll_id, question       |
| POLL#001      | METADATA        | poll    | question, pub_date      |
| POLL#001      | CHOICE#001      | choice  | choice_text, votes      |
| POLL#001      | CHOICE#002      | choice  | choice_text, votes      |

This allows efficient queries:
- Get all polls: Query PK="POLLS"
- Get poll with choices: Query PK="POLL#<id>"
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from db import get_table


class Poll:
    """
    Poll model - represents a question with multiple choices.

    Learning Note: This class wraps DynamoDB operations in a familiar ORM-like interface.
    """

    def __init__(
        self,
        poll_id: str = None,
        question_text: str = "",
        pub_date: str = None,
    ):
        self.poll_id = poll_id or str(uuid.uuid4())[:8]
        self.question_text = question_text
        self.pub_date = pub_date or datetime.utcnow().isoformat()

    def to_dict(self):
        """Convert to dictionary for DynamoDB."""
        return {
            "poll_id": self.poll_id,
            "question_text": self.question_text,
            "pub_date": self.pub_date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Poll":
        """Create Poll from dictionary."""
        return cls(
            poll_id=data.get("poll_id"),
            question_text=data.get("question_text", ""),
            pub_date=data.get("pub_date"),
        )

    def save(self):
        """
        Save poll to DynamoDB.

        Learning Note - put_item():
        - Creates a new item or replaces an existing item
        - Entire item is written (not partial update)
        - Use update_item() for partial updates
        """
        table = get_table()

        # Store poll metadata
        poll_item = {
            "PK": f"POLL#{self.poll_id}",
            "SK": "METADATA",
            "type": "poll",
            "GSI1PK": "POLLS",
            "GSI1SK": self.pub_date,
            **self.to_dict(),
        }
        table.put_item(Item=poll_item)

        # Store poll index entry (for listing all polls)
        index_item = {
            "PK": "POLLS",
            "SK": f"POLL#{self.poll_id}",
            "type": "poll_index",
            "poll_id": self.poll_id,
            "question_text": self.question_text,
            "pub_date": self.pub_date,
        }
        table.put_item(Item=index_item)

        return self

    @classmethod
    def get(cls, poll_id: str) -> Optional["Poll"]:
        """
        Get a poll by ID.

        Learning Note - get_item():
        - Requires the full primary key (PK + SK for composite keys)
        - Returns a single item or None
        - Very fast O(1) operation
        - ConsistentRead=True for strongly consistent reads (default is eventually consistent)
        """
        table = get_table()

        response = table.get_item(
            Key={
                "PK": f"POLL#{poll_id}",
                "SK": "METADATA"
            },
            ConsistentRead=True  # Ensure we get latest data
        )

        item = response.get("Item")
        if not item:
            return None

        return cls.from_dict(item)

    @classmethod
    def get_all(cls) -> list["Poll"]:
        """
        Get all polls.

        Learning Note - query():
        - Finds all items with the same partition key
        - Can filter by sort key using KeyConditionExpression
        - Much more efficient than scan()
        - Returns items in sort key order (ascending by default)
        """
        table = get_table()

        response = table.query(
            KeyConditionExpression=Key("PK").eq("POLLS"),
            ScanIndexForward=False,  # Sort descending (newest first)
        )

        polls = []
        for item in response.get("Items", []):
            poll = cls.from_dict(item)
            polls.append(poll)

        return polls

    @classmethod
    def get_recent(cls, limit: int = 5) -> list["Poll"]:
        """
        Get recent polls using GSI.

        Learning Note - Using GSI:
        - GSI allows querying on non-primary key attributes
        - Must specify IndexName parameter
        - Eventually consistent by default
        """
        table = get_table()

        response = table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq("POLLS"),
            ScanIndexForward=False,  # Newest first
            Limit=limit,
        )

        return [cls.from_dict(item) for item in response.get("Items", [])]

    def update(self, question_text: str = None):
        """
        Update poll question.

        Learning Note - update_item():
        - Updates specific attributes without replacing the entire item
        - Uses UpdateExpression with SET, REMOVE, ADD, DELETE actions
        - ExpressionAttributeNames: Placeholder for attribute names (handles reserved words)
        - ExpressionAttributeValues: Placeholder for values
        - ReturnValues: What to return (NONE, ALL_OLD, UPDATED_OLD, ALL_NEW, UPDATED_NEW)
        """
        table = get_table()

        if question_text:
            self.question_text = question_text

        # Update poll metadata
        table.update_item(
            Key={
                "PK": f"POLL#{self.poll_id}",
                "SK": "METADATA"
            },
            UpdateExpression="SET question_text = :q",
            ExpressionAttributeValues={":q": self.question_text},
        )

        # Update poll index
        table.update_item(
            Key={
                "PK": "POLLS",
                "SK": f"POLL#{self.poll_id}"
            },
            UpdateExpression="SET question_text = :q",
            ExpressionAttributeValues={":q": self.question_text},
        )

        return self

    def delete(self):
        """
        Delete poll and all its choices.

        Learning Note - delete_item():
        - Removes a single item by primary key
        - To delete related items, must delete each separately
        - DynamoDB doesn't have cascading deletes like SQL
        - Consider using batch_write_item() for multiple deletes
        """
        table = get_table()

        # First, get all choices and delete them
        choices = Choice.get_for_poll(self.poll_id)
        for choice in choices:
            choice.delete()

        # Delete poll metadata
        table.delete_item(
            Key={
                "PK": f"POLL#{self.poll_id}",
                "SK": "METADATA"
            }
        )

        # Delete poll index entry
        table.delete_item(
            Key={
                "PK": "POLLS",
                "SK": f"POLL#{self.poll_id}"
            }
        )

    def get_choices(self) -> list["Choice"]:
        """Get all choices for this poll."""
        return Choice.get_for_poll(self.poll_id)

    def get_total_votes(self) -> int:
        """Get total votes across all choices."""
        return sum(c.votes for c in self.get_choices())

    def __repr__(self):
        return f"<Poll {self.poll_id}: {self.question_text[:30]}...>"


class Choice:
    """
    Choice model - represents a choice option for a poll.
    """

    def __init__(
        self,
        choice_id: str = None,
        poll_id: str = "",
        choice_text: str = "",
        votes: int = 0,
    ):
        self.choice_id = choice_id or str(uuid.uuid4())[:8]
        self.poll_id = poll_id
        self.choice_text = choice_text
        self.votes = votes

    def to_dict(self):
        """Convert to dictionary for DynamoDB."""
        return {
            "choice_id": self.choice_id,
            "poll_id": self.poll_id,
            "choice_text": self.choice_text,
            "votes": self.votes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Choice":
        """Create Choice from dictionary."""
        return cls(
            choice_id=data.get("choice_id"),
            poll_id=data.get("poll_id", ""),
            choice_text=data.get("choice_text", ""),
            votes=int(data.get("votes", 0)),
        )

    def save(self):
        """Save choice to DynamoDB."""
        table = get_table()

        item = {
            "PK": f"POLL#{self.poll_id}",
            "SK": f"CHOICE#{self.choice_id}",
            "type": "choice",
            **self.to_dict(),
        }
        table.put_item(Item=item)
        return self

    @classmethod
    def get(cls, poll_id: str, choice_id: str) -> Optional["Choice"]:
        """Get a specific choice."""
        table = get_table()

        response = table.get_item(
            Key={
                "PK": f"POLL#{poll_id}",
                "SK": f"CHOICE#{choice_id}"
            }
        )

        item = response.get("Item")
        if not item:
            return None

        return cls.from_dict(item)

    @classmethod
    def get_for_poll(cls, poll_id: str) -> list["Choice"]:
        """
        Get all choices for a poll.

        Learning Note - begins_with():
        - Filter sort key by prefix
        - Very efficient for hierarchical data
        - Alternative: between() for range queries
        """
        table = get_table()

        response = table.query(
            KeyConditionExpression=(
                Key("PK").eq(f"POLL#{poll_id}") &
                Key("SK").begins_with("CHOICE#")
            )
        )

        return [cls.from_dict(item) for item in response.get("Items", [])]

    def vote(self):
        """
        Increment vote count atomically.

        Learning Note - Atomic Counters:
        - ADD action increments/decrements numeric values atomically
        - Safe for concurrent updates (no race conditions)
        - Alternative: Use conditional writes for complex logic
        """
        table = get_table()

        response = table.update_item(
            Key={
                "PK": f"POLL#{self.poll_id}",
                "SK": f"CHOICE#{self.choice_id}"
            },
            UpdateExpression="SET votes = votes + :inc",
            ExpressionAttributeValues={":inc": 1},
            ReturnValues="UPDATED_NEW"
        )

        self.votes = int(response["Attributes"]["votes"])
        return self

    def delete(self):
        """Delete this choice."""
        table = get_table()

        table.delete_item(
            Key={
                "PK": f"POLL#{self.poll_id}",
                "SK": f"CHOICE#{self.choice_id}"
            }
        )

    def __repr__(self):
        return f"<Choice {self.choice_id}: {self.choice_text} ({self.votes} votes)>"


# ============================================================================
# Batch Operations - Learning Examples
# ============================================================================

def batch_create_poll_with_choices(question: str, choices: list[str]) -> Poll:
    """
    Create a poll with multiple choices in a batch operation.

    Learning Note - batch_write_item():
    - Write up to 25 items in a single request
    - More efficient than multiple put_item() calls
    - Items can be across multiple tables
    - Unprocessed items returned if capacity exceeded
    """
    table = get_table()

    poll = Poll(question_text=question)

    # Prepare all items
    items = [
        # Poll metadata
        {
            "PutRequest": {
                "Item": {
                    "PK": f"POLL#{poll.poll_id}",
                    "SK": "METADATA",
                    "type": "poll",
                    "GSI1PK": "POLLS",
                    "GSI1SK": poll.pub_date,
                    **poll.to_dict(),
                }
            }
        },
        # Poll index
        {
            "PutRequest": {
                "Item": {
                    "PK": "POLLS",
                    "SK": f"POLL#{poll.poll_id}",
                    "type": "poll_index",
                    "poll_id": poll.poll_id,
                    "question_text": poll.question_text,
                    "pub_date": poll.pub_date,
                }
            }
        },
    ]

    # Add choices
    for choice_text in choices:
        choice = Choice(poll_id=poll.poll_id, choice_text=choice_text)
        items.append({
            "PutRequest": {
                "Item": {
                    "PK": f"POLL#{poll.poll_id}",
                    "SK": f"CHOICE#{choice.choice_id}",
                    "type": "choice",
                    **choice.to_dict(),
                }
            }
        })

    # Execute batch write
    from db import get_dynamodb_resource
    dynamodb = get_dynamodb_resource()

    response = dynamodb.batch_write_item(
        RequestItems={
            table.name: items
        }
    )

    # Handle unprocessed items (retry logic in production)
    unprocessed = response.get("UnprocessedItems", {})
    if unprocessed:
        print(f"Warning: {len(unprocessed)} items were not processed")

    return poll


def scan_all_items():
    """
    Scan entire table (for debugging/admin only).

    Learning Note - scan():
    - Reads every item in the table
    - Very expensive for large tables
    - Consumes read capacity for ALL items
    - Use query() instead whenever possible
    - Useful for: exports, migrations, admin tools
    """
    table = get_table()

    items = []
    last_key = None

    while True:
        if last_key:
            response = table.scan(ExclusiveStartKey=last_key)
        else:
            response = table.scan()

        items.extend(response.get("Items", []))

        # Pagination handling
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break

    return items
