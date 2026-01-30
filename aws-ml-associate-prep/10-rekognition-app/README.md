# 10 - Amazon Rekognition

> **Exam Weight**: Part of AI Services knowledge
> **Priority**: MEDIUM - Pre-built AI service

## What is Amazon Rekognition?

Amazon Rekognition is a pre-trained computer vision service that provides image and video analysis. No ML expertise required - just call the API.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     AMAZON REKOGNITION CAPABILITIES                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  IMAGE ANALYSIS                    VIDEO ANALYSIS                       │
│  ──────────────                    ──────────────                       │
│  • Object & Scene Detection        • Person Tracking                    │
│  • Facial Analysis                 • Face Search in Video               │
│  • Face Comparison                 • Path Tracking                      │
│  • Text Detection (OCR)            • Activity Detection                 │
│  • Celebrity Recognition           • Content Moderation                 │
│  • Content Moderation              • Segment Detection                  │
│  • Custom Labels                                                        │
│  • PPE Detection                                                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key APIs (KNOW FOR EXAM)

| API | Purpose | Use Case |
|-----|---------|----------|
| `DetectLabels` | Object/scene detection | Identify objects in images |
| `DetectFaces` | Face detection & analysis | Age, emotion, attributes |
| `CompareFaces` | Face comparison | Verify identity |
| `SearchFaces` | Face search in collection | Find person in database |
| `DetectText` | Text detection (OCR) | Read text in images |
| `RecognizeCelebrities` | Celebrity identification | Media applications |
| `DetectModerationLabels` | Content moderation | Filter inappropriate |
| `DetectProtectiveEquipment` | PPE detection | Safety compliance |

---

## Basic Usage

### Detect Labels (Object Detection)

```python
import boto3

rekognition = boto3.client('rekognition')

# From S3
response = rekognition.detect_labels(
    Image={
        'S3Object': {
            'Bucket': 'my-bucket',
            'Name': 'image.jpg'
        }
    },
    MaxLabels=10,
    MinConfidence=80
)

for label in response['Labels']:
    print(f"{label['Name']}: {label['Confidence']:.2f}%")
```

### Detect Faces

```python
response = rekognition.detect_faces(
    Image={'S3Object': {'Bucket': 'bucket', 'Name': 'photo.jpg'}},
    Attributes=['ALL']  # or 'DEFAULT'
)

for face in response['FaceDetails']:
    print(f"Age: {face['AgeRange']['Low']}-{face['AgeRange']['High']}")
    print(f"Emotion: {face['Emotions'][0]['Type']}")
    print(f"Smile: {face['Smile']['Value']}")
```

### Compare Faces

```python
response = rekognition.compare_faces(
    SourceImage={
        'S3Object': {'Bucket': 'bucket', 'Name': 'source.jpg'}
    },
    TargetImage={
        'S3Object': {'Bucket': 'bucket', 'Name': 'target.jpg'}
    },
    SimilarityThreshold=80
)

for match in response['FaceMatches']:
    print(f"Similarity: {match['Similarity']:.2f}%")
```

### Detect Text (OCR)

```python
response = rekognition.detect_text(
    Image={'S3Object': {'Bucket': 'bucket', 'Name': 'document.jpg'}}
)

for text in response['TextDetections']:
    if text['Type'] == 'LINE':
        print(f"Text: {text['DetectedText']}")
```

---

## Face Collections

Store faces for later search (face search database).

```python
# Create collection
rekognition.create_collection(CollectionId='my-faces')

# Index face (add to collection)
response = rekognition.index_faces(
    CollectionId='my-faces',
    Image={'S3Object': {'Bucket': 'bucket', 'Name': 'person.jpg'}},
    ExternalImageId='person-001',  # Your reference ID
    MaxFaces=1,
    DetectionAttributes=['ALL']
)

face_id = response['FaceRecords'][0]['Face']['FaceId']

# Search for face in collection
response = rekognition.search_faces_by_image(
    CollectionId='my-faces',
    Image={'S3Object': {'Bucket': 'bucket', 'Name': 'unknown.jpg'}},
    FaceMatchThreshold=80,
    MaxFaces=5
)

for match in response['FaceMatches']:
    print(f"Match: {match['Face']['ExternalImageId']}, Similarity: {match['Similarity']:.2f}%")
```

---

## Custom Labels

Train custom object detection models.

```
┌─────────────────────────────────────────────────────────────┐
│                    CUSTOM LABELS WORKFLOW                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Create Project                                          │
│  2. Create Dataset (S3 images + labels)                    │
│  3. Train Model                                             │
│  4. Evaluate Results                                        │
│  5. Start Model (deploy)                                    │
│  6. Detect Custom Labels                                    │
│  7. Stop Model (save costs)                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

```python
# Start custom model
response = rekognition.start_project_version(
    ProjectVersionArn='arn:aws:rekognition:...:project/my-project/version/1',
    MinInferenceUnits=1
)

# Detect with custom model
response = rekognition.detect_custom_labels(
    ProjectVersionArn='arn:aws:rekognition:...',
    Image={'S3Object': {'Bucket': 'bucket', 'Name': 'image.jpg'}},
    MinConfidence=80
)
```

### Exam Tip: Custom Labels
- Train on your specific objects (e.g., product defects)
- Requires labeled training data
- Billed per inference hour when running

---

## Video Analysis

For video, Rekognition uses async operations.

```python
# Start video analysis
response = rekognition.start_label_detection(
    Video={
        'S3Object': {
            'Bucket': 'bucket',
            'Name': 'video.mp4'
        }
    },
    NotificationChannel={
        'SNSTopicArn': 'arn:aws:sns:...',
        'RoleArn': 'arn:aws:iam:...'
    }
)

job_id = response['JobId']

# Get results (after SNS notification)
response = rekognition.get_label_detection(JobId=job_id)
```

### Video APIs

| Start API | Get API | Purpose |
|-----------|---------|---------|
| `start_label_detection` | `get_label_detection` | Detect labels in video |
| `start_face_detection` | `get_face_detection` | Detect faces |
| `start_person_tracking` | `get_person_tracking` | Track people |
| `start_content_moderation` | `get_content_moderation` | Moderate content |
| `start_segment_detection` | `get_segment_detection` | Detect scenes/shots |

---

## Exam Question Patterns

### Pattern 1: Object Detection
> "Identify objects in images..."

**Answer**: Rekognition DetectLabels

### Pattern 2: Face Verification
> "Verify if two photos are the same person..."

**Answer**: Rekognition CompareFaces

### Pattern 3: Face Search
> "Find a person across multiple images..."

**Answer**: Rekognition Face Collections + SearchFaces

### Pattern 4: Content Moderation
> "Filter inappropriate images..."

**Answer**: Rekognition DetectModerationLabels

### Pattern 5: Custom Objects
> "Detect company-specific products..."

**Answer**: Rekognition Custom Labels

### Pattern 6: Text in Images
> "Extract text from photos..."

**Answer**: Rekognition DetectText (or Textract for documents)

---

## Rekognition vs Textract

| Feature | Rekognition | Textract |
|---------|-------------|----------|
| **Focus** | Image/video analysis | Document text extraction |
| **Text** | Basic OCR | Forms, tables, queries |
| **Use Case** | Scene text, signs | Documents, invoices, forms |

---

## Checklist

- [ ] Know main Rekognition APIs and their purposes
- [ ] Understand face collections for face search
- [ ] Know Custom Labels for custom object detection
- [ ] Understand video analysis (async pattern)
- [ ] Know when to use Rekognition vs Textract

---

## Next Steps

After completing this module, proceed to:
- [11 - Comprehend NLP](../11-comprehend-nlp/) - Natural language processing
