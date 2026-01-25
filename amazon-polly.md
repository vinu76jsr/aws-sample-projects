# Amazon Polly - Text to Speech

Amazon Polly is a cloud service that converts text into lifelike speech.

## Using AWS Console

1. Go to [AWS Polly Console](https://console.aws.amazon.com/polly)
2. Select a **voice** (e.g., "Joanna" for US English, "Matthew" for US English Male)
3. Choose **Engine** - Standard or Neural (Neural sounds more natural)
4. Enter your text in the input box
5. Click **Listen** to preview the audio
6. Click **Download** to save as MP3/OGG/PCM

## Available Voices

| Language | Voice Examples |
|----------|---------------|
| English (US) | Joanna, Matthew, Ivy, Kendra |
| English (UK) | Amy, Brian, Emma |
| Spanish | Lucia, Enrique, Lupe |
| French | Celine, Mathieu, Lea |
| German | Marlene, Hans, Vicki |

Full list: [Polly Voice List](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html)

## SSML Support

Polly supports SSML for advanced control:

```xml
<speak>
  Hello <break time="1s"/> world!
  <prosody rate="slow">This is slower.</prosody>
  <emphasis level="strong">This is emphasized.</emphasis>
</speak>
```

## Pricing

- Standard voices: $4.00 per 1 million characters
- Neural voices: $16.00 per 1 million characters
- Free tier: 5 million characters/month for 12 months
