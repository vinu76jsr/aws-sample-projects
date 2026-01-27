# AWS Step Functions - Learn by Example

A hands-on guide to understand Step Functions through progressive examples.

## What is Step Functions?

Step Functions is a **serverless workflow orchestrator**. It coordinates multiple AWS services into serverless workflows defined using JSON (Amazon States Language).

**Think of it as**: A flowchart that actually runs. You define states (boxes) and transitions (arrows), and AWS executes them.

## Core Concepts

### State Machine
The entire workflow definition. Contains:
- `StartAt`: Which state to begin with
- `States`: All the states in your workflow

### States
Individual steps in your workflow. Each state has:
- A **Type** (what it does)
- Either `Next` (which state follows) or `End: true` (workflow ends)

### The 8 State Types

| Type | Purpose | Real-world use |
|------|---------|----------------|
| **Task** | Do work (Lambda, API, etc.) | Process data, call APIs |
| **Pass** | Pass data through (or inject data) | Transform data, testing |
| **Choice** | Branch based on conditions | If/else logic |
| **Wait** | Pause execution | Rate limiting, delays |
| **Parallel** | Run branches simultaneously | Fan-out operations |
| **Map** | Loop over array items | Batch processing |
| **Succeed** | End successfully | Mark completion |
| **Fail** | End with error | Mark failure |

## Examples (Progressive Learning Path)

### 1. Hello World (`01-hello-world.json`)
**Concept**: Minimal state machine with one Pass state

```
[Start] → [HelloWorld (Pass)] → [End]
```

Try it:
1. Go to Step Functions console
2. Create state machine → Write workflow in code
3. Paste the JSON
4. Execute with empty input `{}`

---

### 2. Data Flow (`02-pass-chain.json`)
**Concept**: How data flows between states using `ResultPath`

```
[Start] → [AddName] → [AddAge] → [AddStatus] → [End]
```

**Key learning**: `ResultPath` controls WHERE the result goes in the JSON:
- `"ResultPath": "$.name"` → puts result at `{"name": <result>}`
- `"ResultPath": "$"` → replaces entire input with result
- `"ResultPath": null` → discards result, keeps input unchanged

Input: `{}`
Output: `{"name": "John", "age": 30, "status": "active"}`

---

### 3. Choice - Branching (`03-choice.json`)
**Concept**: Conditional logic (if/else)

```
                    ┌─→ [Minor] → [End]
[Start] → [CheckAge]├─→ [Adult] → [End]
                    └─→ [Senior] → [End]
```

**Choice operators**:
- `StringEquals`, `StringGreaterThan`
- `NumericEquals`, `NumericLessThan`, `NumericGreaterThanEquals`
- `BooleanEquals`
- `IsPresent`, `IsNull`, `IsString`, `IsNumeric`
- `And`, `Or`, `Not` (combine conditions)

Test inputs (in `test-inputs/03-choice-inputs.json`):
```json
{"age": 15}   → Minor path
{"age": 35}   → Adult path
{"age": 70}   → Senior path
```

---

### 4. Wait - Delays (`04-wait.json`)
**Concept**: Pause execution

```
[OrderReceived] → [Wait 5s] → [PaymentConfirmed] → [Wait 3s] → [Shipped]
```

**Wait options**:
```json
{"Seconds": 10}                           // Fixed seconds
{"Timestamp": "2024-12-31T23:59:59Z"}    // Until specific time
{"SecondsPath": "$.waitTime"}            // Dynamic from input
{"TimestampPath": "$.deadline"}          // Dynamic timestamp
```

---

### 5. Parallel - Fan Out (`05-parallel.json`)
**Concept**: Run multiple branches at the same time

```
              ┌─→ [CheckInventory] ───┐
[ProcessOrder]├─→ [ValidatePayment] ──┼→ [Consolidate] → [End]
              └─→ [CalculateShipping]─┘
```

**Key points**:
- All branches run simultaneously
- Output is an **array** of each branch's result
- If ANY branch fails, the entire Parallel fails

Output structure:
```json
[
  {"task": "inventory", ...},
  {"task": "payment", ...},
  {"task": "shipping", ...}
]
```

---

### 6. Map - Iteration (`06-map.json`)
**Concept**: Process each item in an array

```
                      ┌─────────────────────┐
[ProcessItems] ──────→│ For each item:      │──→ [Complete]
                      │ [CalculateItemTotal]│
                      └─────────────────────┘
```

**Test input** (`test-inputs/06-map-input.json`):
```json
{
  "orderId": "ORD-12345",
  "items": [
    {"name": "Widget", "price": 29.99, "quantity": 2},
    {"name": "Gadget", "price": 49.99, "quantity": 1}
  ]
}
```

**Map modes**:
- `INLINE`: Process items within the same execution (simple)
- `DISTRIBUTED`: Process items as child executions (massive scale)

---

### 7. Error Handling (`07-error-handling.json`)
**Concept**: Fail and Succeed states

```
[TryProcess] → [SimulateTask] ─→ [Success] ✓
                      │
                      └─→ [FailState] ✗
```

Test with:
- `{"shouldFail": false}` → Success
- `{"shouldFail": true}` → Failure

---

### 8. Task with Lambda (`08-task-lambda.json`)
**Concept**: Real-world Task state calling Lambda with Retry and Catch

```
                 ┌─→ [ProcessUser] → [NotifySuccess] → [End]
[ValidateInput] ─┤         │
                 │         └─(error)→ [HandleError] → [End]
                 └─→ [InvalidInput] ✗
```

**Retry configuration**:
```json
"Retry": [{
  "ErrorEquals": ["Lambda.ServiceException"],
  "IntervalSeconds": 2,    // Wait before retry
  "MaxAttempts": 3,        // How many retries
  "BackoffRate": 2         // Multiply interval each retry
}]
```

**Catch configuration**:
```json
"Catch": [{
  "ErrorEquals": ["States.ALL"],   // Catch everything
  "ResultPath": "$.error",         // Put error here
  "Next": "HandleError"            // Go to this state
}]
```

## JSONPath in Step Functions

Step Functions uses JSONPath to reference data:

| Expression | Meaning |
|------------|---------|
| `$` | The entire input |
| `$.name` | The `name` field |
| `$.items[0]` | First item in array |
| `$.items[*].price` | All prices in items array |

**Common parameters**:
- `InputPath`: Filter input BEFORE state runs
- `Parameters`: Construct new input (use `.$` suffix for JSONPath)
- `ResultPath`: WHERE to put the result
- `OutputPath`: Filter output AFTER state runs

Example flow:
```
Input → [InputPath filter] → [Parameters build] → STATE → [ResultPath place] → [OutputPath filter] → Output
```

## Quick Start: Run Your First State Machine

1. **Open Step Functions Console**
   ```
   AWS Console → Step Functions → Create state machine
   ```

2. **Choose "Write workflow in code"**

3. **Paste `01-hello-world.json`**

4. **Click "Create"** (use default settings)

5. **Start execution** with input: `{}`

6. **Watch the visual graph** update in real-time!

## Testing in Console Tips

- Use **Workflow Studio** (visual editor) to understand structure
- Click any state to see its input/output
- Use **Express** type for quick tests (cheaper, no history)
- Use **Standard** type for production (full history, exactly-once)

## Common Patterns

### Sequential Processing
```
A → B → C → D
```

### Fan-out/Fan-in
```
    ┌→ B ─┐
A → ├→ C ─┼→ E
    └→ D ─┘
```

### Error Recovery
```
A → B ─(retry 3x)─→ B
      └─(catch)──→ Fallback
```

### Conditional Loop
```
A → B → [Check] ─(done)─→ End
           └─(more)─→ B
```

## Pricing

- **Standard**: $0.025 per 1,000 state transitions
- **Express**: $1.00 per 1M requests + duration

For learning, Express is much cheaper!

## Files in This Project

```
step-functions-intro/
├── README.md
├── state-machines/
│   ├── 01-hello-world.json      # Simplest example
│   ├── 02-pass-chain.json       # Data flow
│   ├── 03-choice.json           # Branching
│   ├── 04-wait.json             # Delays
│   ├── 05-parallel.json         # Concurrent execution
│   ├── 06-map.json              # Array iteration
│   ├── 07-error-handling.json   # Fail/Succeed
│   └── 08-task-lambda.json      # Lambda integration
├── sample-lambda/
│   └── index.py                 # Lambda for Task state
└── test-inputs/
    ├── 03-choice-inputs.json    # Test data for Choice
    └── 06-map-input.json        # Test data for Map
```

## Next Steps

After mastering these basics:
1. Try **Workflow Studio** (visual drag-and-drop)
2. Integrate with **SNS**, **SQS**, **DynamoDB** directly (no Lambda needed)
3. Use **Express workflows** for high-volume, short-duration tasks
4. Explore **Distributed Map** for massive parallel processing
5. Build a real workflow: Order processing, ETL pipeline, or approval system
