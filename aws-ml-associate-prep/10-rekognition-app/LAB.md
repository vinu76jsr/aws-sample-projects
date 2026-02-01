# Lab 10: Amazon Rekognition

## Overview
Use Amazon Rekognition[^rekognition] for image analysis including object detection, face analysis, and text detection.

**Duration**: 30-45 minutes
**Cost**: ~$1 (free tier available)
**Prerequisites**: AWS Account

---

## Architecture Overview

```mermaid
flowchart TB
    subgraph Input["fa:fa-image Image Input"]
        S3[(fa:fa-database S3 Bucket)]
        Bytes[fa:fa-file-image Image Bytes]
    end

    subgraph Rekognition["fa:fa-eye Amazon Rekognition APIs"]
        Labels[fa:fa-tags DetectLabels<br/>Objects & Scenes]
        Faces[fa:fa-smile DetectFaces<br/>Facial Analysis]
        Text[fa:fa-font DetectText<br/>OCR]
        Celeb[fa:fa-star RecognizeCelebrities]
        Mod[fa:fa-shield-alt DetectModerationLabels]
    end

    subgraph FaceCollection["fa:fa-users Face Collections"]
        Create[fa:fa-plus-circle CreateCollection]
        Index[fa:fa-user-plus IndexFaces]
        Search[fa:fa-search SearchFacesByImage]
    end

    subgraph Output["fa:fa-file-alt Results"]
        JSON[fa:fa-code JSON Response]
        Confidence[fa:fa-percentage Confidence Scores]
        BoundingBox[fa:fa-vector-square Bounding Boxes]
    end

    S3 --> Rekognition
    Bytes --> Rekognition
    Rekognition --> Output
    Rekognition --> FaceCollection

    style Input fill:#e3f2fd
    style Rekognition fill:#fff3e0
    style FaceCollection fill:#e8f5e9
    style Output fill:#fce4ec
```

### Face Collection Workflow

```mermaid
sequenceDiagram
    participant App as fa:fa-code Application
    participant Rek as fa:fa-eye Rekognition
    participant Col as fa:fa-users Face Collection

    App->>Rek: CreateCollection("employees")
    Rek->>Col: Create index

    loop For each employee
        App->>Rek: IndexFaces(image, collection)
        Rek->>Col: Store face vector
        Rek-->>App: FaceId returned
    end

    Note over App,Col: Later - Identity verification

    App->>Rek: SearchFacesByImage(new_image)
    Rek->>Col: Search similar vectors
    Col-->>Rek: Matching FaceIds
    Rek-->>App: Match results + confidence
```

### Video Analysis Pipeline

```mermaid
flowchart LR
    subgraph Async["fa:fa-video Async Video Analysis"]
        Video[fa:fa-film S3 Video]
        Start[fa:fa-play StartLabelDetection]
        SNS[fa:fa-bell SNS Notification]
        Get[fa:fa-download GetLabelDetection]
        Results[Timestamped Labels]
    end

    Video --> Start
    Start --> |JobId| SNS
    SNS --> Get
    Get --> Results

    style Async fill:#e3f2fd
```

---

## Lab Objectives

- [ ] Detect labels[^detect-labels] (objects) in images
- [ ] Analyze faces[^detect-faces] in photos
- [ ] Detect text[^detect-text] in images
- [ ] Create a face collection[^face-collection]

---

## Part 1: Setup and Detect Labels

### Step 1.1: Upload Sample Image

```bash
# Download sample image
curl -o sample-image.jpg "https://images.unsplash.com/photo-1517849845537-4d257902454a?w=640"

# Upload to S3
aws s3 cp sample-image.jpg s3://YOUR_BUCKET/rekognition-lab/
```

### Step 1.2: Detect Labels

```python
import boto3

rekognition = boto3.client('rekognition')

# Detect labels (objects, scenes)
response = rekognition.detect_labels(
    Image={
        'S3Object': {
            'Bucket': 'YOUR_BUCKET',
            'Name': 'rekognition-lab/sample-image.jpg'
        }
    },
    MaxLabels=10,
    MinConfidence=80
)

print("Detected Labels:")
for label in response['Labels']:
    print(f"  {label['Name']}: {label['Confidence']:.2f}%")
    for instance in label.get('Instances', []):
        box = instance['BoundingBox']
        print(f"    Bounding Box: {box}")
```

---

## Part 2: Face Detection

```python
# Download face image
# Use any image with a face

# Detect faces
response = rekognition.detect_faces(
    Image={
        'S3Object': {
            'Bucket': 'YOUR_BUCKET',
            'Name': 'rekognition-lab/face-image.jpg'
        }
    },
    Attributes=['ALL']
)

print("Face Analysis:")
for face in response['FaceDetails']:
    print(f"  Age Range: {face['AgeRange']['Low']}-{face['AgeRange']['High']}")
    print(f"  Gender: {face['Gender']['Value']} ({face['Gender']['Confidence']:.1f}%)")
    print(f"  Emotions:")
    for emotion in face['Emotions'][:3]:
        print(f"    - {emotion['Type']}: {emotion['Confidence']:.1f}%")
    print(f"  Smile: {face['Smile']['Value']}")
    print(f"  Eyeglasses: {face['Eyeglasses']['Value']}")
```

---

## Part 3: Text Detection (OCR)

```python
# Detect text in image
response = rekognition.detect_text(
    Image={
        'S3Object': {
            'Bucket': 'YOUR_BUCKET',
            'Name': 'rekognition-lab/text-image.jpg'
        }
    }
)

print("Detected Text:")
for text in response['TextDetections']:
    if text['Type'] == 'LINE':
        print(f"  {text['DetectedText']} (Confidence: {text['Confidence']:.1f}%)")
```

---

## Part 4: Face Collection

```python
# Create face collection
collection_id = 'lab-faces'

rekognition.create_collection(CollectionId=collection_id)
print(f"Collection '{collection_id}' created")

# Index a face
response = rekognition.index_faces(
    CollectionId=collection_id,
    Image={
        'S3Object': {
            'Bucket': 'YOUR_BUCKET',
            'Name': 'rekognition-lab/person1.jpg'
        }
    },
    ExternalImageId='person-001',
    MaxFaces=1,
    DetectionAttributes=['ALL']
)

face_id = response['FaceRecords'][0]['Face']['FaceId']
print(f"Indexed face: {face_id}")

# Search for face
response = rekognition.search_faces_by_image(
    CollectionId=collection_id,
    Image={
        'S3Object': {
            'Bucket': 'YOUR_BUCKET',
            'Name': 'rekognition-lab/search-image.jpg'
        }
    },
    FaceMatchThreshold=80,
    MaxFaces=5
)

for match in response['FaceMatches']:
    print(f"Match: {match['Face']['ExternalImageId']} ({match['Similarity']:.1f}%)")
```

---

## Part 5: Clean Up

```python
# Delete collection
rekognition.delete_collection(CollectionId=collection_id)

# Delete S3 objects
!aws s3 rm s3://YOUR_BUCKET/rekognition-lab/ --recursive
```

---

## Lab Summary

| Concept | What You Did |
|---------|--------------|
| **Label Detection** | Identified objects in images |
| **Face Analysis** | Detected age, emotion, attributes |
| **Text Detection** | Extracted text (OCR) |
| **Face Collection** | Built searchable face database |

---

## Exam Relevance

- ✅ Rekognition API capabilities
- ✅ Face collections for search
- ✅ When to use Rekognition vs Textract
- ✅ Confidence scores[^confidence-score] and bounding boxes[^bounding-box]
- ✅ Content moderation[^moderation] features

---

## Glossary

[^rekognition]: **Amazon Rekognition** - A fully managed computer vision service that provides pre-trained and customizable models for image and video analysis tasks.

[^detect-labels]: **DetectLabels** - A Rekognition API that identifies objects, scenes, activities, and concepts in images, returning labels with confidence scores.

[^detect-faces]: **DetectFaces** - A Rekognition API that detects faces in images and returns facial attributes such as age range, emotions, gender, and facial landmarks.

[^detect-text]: **DetectText** - A Rekognition API that performs OCR to detect and extract text from images, returning detected words and lines with their locations.

[^face-collection]: **Face Collection** - A searchable repository of face vectors in Rekognition used for face matching and identity verification workflows.

[^bounding-box]: **Bounding Box** - A rectangular region defined by coordinates that indicates where a detected object, face, or text appears within an image.

[^confidence-score]: **Confidence Score** - A percentage value (0-100) indicating how certain Rekognition is about a detection or classification result.

[^moderation]: **Content Moderation** - Rekognition's DetectModerationLabels API that identifies potentially unsafe or inappropriate content in images and videos.

---

## Next Lab

Continue to [Lab 11: Comprehend NLP](../11-comprehend-nlp/LAB.md) →
