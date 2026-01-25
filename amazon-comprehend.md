# Amazon Comprehend - Natural Language Processing

Amazon Comprehend is a managed NLP service for extracting insights from text.

## Using AWS Console

1. Go to [AWS Comprehend Console](https://console.aws.amazon.com/comprehend)
2. Click **Real-time analysis** in the left sidebar
3. Enter or paste your text in the input box
4. Click **Analyze**
5. View results across multiple tabs

## Analysis Types

### Entities
Identifies named entities: people, places, organizations, dates, quantities, etc.

```
Input: "Jeff Bezos founded Amazon in Seattle in 1994."

Output:
- Jeff Bezos → PERSON
- Amazon → ORGANIZATION
- Seattle → LOCATION
- 1994 → DATE
```

### Key Phrases
Extracts important phrases from the text.

### Sentiment
Detects overall sentiment: Positive, Negative, Neutral, or Mixed.

```
Input: "The product quality is excellent but shipping was slow."

Output: Mixed (Positive: 0.45, Negative: 0.30, Neutral: 0.20, Mixed: 0.05)
```

### Language Detection
Identifies the dominant language in the text.

### PII Detection
Identifies personally identifiable information (names, addresses, SSN, etc.)

### Syntax
Provides part-of-speech tagging for each word.

## Batch Processing

For large volumes:
1. Upload text files to S3
2. Go to **Analysis jobs** → **Create job**
3. Select analysis type and S3 input/output locations
4. Monitor job progress in the console

## Custom Models

Train custom classifiers or entity recognizers:
1. Go to **Custom classification** or **Custom entity recognition**
2. Prepare labeled training data in CSV format
3. Create and train the model
4. Deploy as an endpoint for real-time inference

## Pricing

- **Entities, Sentiment, Key Phrases, Language, Syntax**: $0.0001 per unit (100 characters)
- **PII Detection**: $0.0001 per unit
- **Custom Models**: Training + inference costs
- **Free tier**: 50K units/month for 12 months
