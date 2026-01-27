# Polls DynamoDB - Learn DynamoDB with Python

A polls application (inspired by Django's tutorial) built with Python and Amazon DynamoDB. This project is designed to help you learn DynamoDB concepts through hands-on practice.

## Features

- Flask web application with voting functionality
- CLI for interacting with DynamoDB directly
- Single-table design pattern (DynamoDB best practice)
- Comprehensive code comments explaining DynamoDB concepts
- Local development with DynamoDB Local

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Single Table Design                       │
├─────────────────┬─────────────────┬────────┬────────────────────┤
│ PK              │ SK              │ Type   │ Attributes         │
├─────────────────┼─────────────────┼────────┼────────────────────┤
│ POLLS           │ POLL#abc123     │ index  │ question, pub_date │
│ POLL#abc123     │ METADATA        │ poll   │ question, pub_date │
│ POLL#abc123     │ CHOICE#def456   │ choice │ text, votes        │
│ POLL#abc123     │ CHOICE#ghi789   │ choice │ text, votes        │
└─────────────────┴─────────────────┴────────┴────────────────────┘
```

## Quick Start

### 1. Start DynamoDB Local

```bash
docker-compose up -d
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work for local development)
```

### 4. Initialize Database

```bash
# Create table
python cli.py init

# Seed with sample data
python cli.py seed
```

### 5. Run the Application

**Web Application:**
```bash
python app.py
# Open http://localhost:5000
```

**CLI:**
```bash
python cli.py --help
python cli.py list
python cli.py show <poll_id>
python cli.py vote <poll_id>
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `python cli.py init` | Create DynamoDB table |
| `python cli.py seed` | Add sample polls |
| `python cli.py list` | List all polls |
| `python cli.py show <id>` | Show poll with results |
| `python cli.py vote <id>` | Vote on a poll |
| `python cli.py create` | Create a new poll |
| `python cli.py delete <id>` | Delete a poll |
| `python cli.py scan` | Scan entire table (learning demo) |
| `python cli.py reset` | Delete and recreate table |
| `python cli.py info` | Show DynamoDB learning guide |

## DynamoDB Concepts Covered

### 1. Table Design
- **Partition Key (PK)**: Determines data distribution
- **Sort Key (SK)**: Enables range queries within a partition
- **Single-Table Design**: Store multiple entity types in one table

### 2. Operations
- **put_item**: Create or replace an item
- **get_item**: Read by primary key (O(1) operation)
- **update_item**: Partial updates with expressions
- **delete_item**: Remove an item
- **query**: Efficient reads within a partition
- **scan**: Full table read (expensive!)
- **batch_write_item**: Multiple writes in one request

### 3. Advanced Features
- **Global Secondary Index (GSI)**: Query on non-key attributes
- **Atomic Counters**: Thread-safe increments (for votes)
- **Conditional Writes**: Prevent race conditions
- **Pagination**: Handle large result sets

### 4. Best Practices
- Design for access patterns first
- Prefer query() over scan()
- Use batch operations for efficiency
- Choose appropriate billing mode

## Project Structure

```
polls-dynamodb/
├── app.py              # Flask web application
├── cli.py              # Command-line interface
├── config.py           # Configuration management
├── db.py               # DynamoDB connection and table setup
├── models.py           # Poll and Choice models with DynamoDB ops
├── templates/          # Flask HTML templates
│   ├── base.html
│   ├── index.html
│   ├── detail.html
│   ├── results.html
│   ├── create.html
│   └── ...
├── requirements.txt    # Python dependencies
├── docker-compose.yml  # DynamoDB Local setup
├── .env.example        # Environment template
└── README.md
```

## Using with Real AWS

To use with actual AWS DynamoDB instead of DynamoDB Local:

1. Remove or comment out `DYNAMODB_ENDPOINT` in `.env`
2. Configure AWS credentials:
   ```bash
   aws configure
   # Or set environment variables:
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export AWS_REGION=us-east-1
   ```
3. Run the application (table will be created in AWS)

## Learning Resources

### Code Comments
Each file contains detailed comments explaining DynamoDB concepts. Start with:
1. `db.py` - Table creation and connection
2. `models.py` - CRUD operations and access patterns

### Key Files to Study

**db.py** - Learn about:
- Creating tables with KeySchema
- Defining attributes and indexes
- Billing modes (on-demand vs provisioned)

**models.py** - Learn about:
- put_item, get_item, update_item, delete_item
- query with KeyConditionExpression
- Atomic counters for votes
- Batch operations

### Recommended Learning Path

1. Run `python cli.py info` for a quick overview
2. Create and explore polls via CLI
3. Use `python cli.py scan` to see raw table structure
4. Read the code comments in `models.py`
5. Experiment with the web application
6. Modify the code to add new features

## Exercises

Try these exercises to deepen your understanding:

1. **Add a "last voted" timestamp** to choices
2. **Create a "popular polls" query** using a GSI
3. **Add poll categories** and query by category
4. **Implement poll expiration** with TTL
5. **Add user tracking** to prevent duplicate votes

## Cost Considerations

| Mode | Description | Best For |
|------|-------------|----------|
| On-Demand | Pay per request | Variable/unpredictable traffic |
| Provisioned | Set capacity units | Steady, predictable traffic |

This project uses on-demand billing (`PAY_PER_REQUEST`) for simplicity.

## Troubleshooting

### "Table does not exist"
```bash
python cli.py init
```

### Connection refused (DynamoDB Local)
```bash
docker-compose up -d
docker-compose logs dynamodb-local
```

### AWS credentials error
```bash
# For local development, ensure .env has:
DYNAMODB_ENDPOINT=http://localhost:8000
AWS_ACCESS_KEY_ID=local
AWS_SECRET_ACCESS_KEY=local
```

## License

MIT - Use this project to learn and build!
