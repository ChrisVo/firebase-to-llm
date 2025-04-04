# Firebase to LLM Data Sampler

A Python tool that helps you sample real data from your Firestore collections to use as test data when developing and testing LLM applications. With modern LLMs supporting large context windows, using real production data samples can significantly improve your testing and development process.

## Why Use Real Data for LLM Testing?

- **Better Testing**: Real-world data patterns help catch edge cases
- **Improved Prompting**: Develop more accurate prompt templates using actual data structures
- **Schema Understanding**: Help LLMs better understand your data models
- **Context Window Utilization**: Modern LLMs can handle large amounts of context - why not use it?

## Prerequisites

- Python 3.x
- Firebase Admin SDK credentials (service account key)
- `firebase-admin` Python package

## Installation

1. Clone this repository or download the script
2. Install the required package:

```bash
pip install firebase-admin
```

## Getting Your Firebase Credentials

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to Project Settings (gear icon) > Service accounts
4. Click "Generate New Private Key"
5. Save the JSON file securely - DO NOT commit this file to version control
6. Add `*.json` to your `.gitignore` file

## Usage

Basic usage to sample your data:

```bash
python firebase-to-llm.py path/to/your/serviceAccountKey.json
```

With optional parameters:

```bash
python firebase-to-llm.py path/to/your/serviceAccountKey.json --project-id your-project-id --max-depth 5 --sample-size 10
```

### Command Line Arguments

- `key_file`: (Required) Path to your Firebase Admin SDK service account key file (JSON)
- `--project-id`: (Optional) Firebase Project ID (usually inferred from key file)
- `--max-depth`: (Optional) Maximum recursion depth for subcollections (default: 10)
- `--sample-size`: (Optional) Number of documents to sample per collection (default: all)

## Output Format

The script outputs sampled data in a hierarchical format that's easy to include in LLM prompts:

- Top-level collections are listed first
- For each collection:
  - A sample of documents with their IDs
  - Document data in JSON format
  - Nested subcollections (if any) are recursively sampled
  - Timestamps are converted to ISO 8601 format

Example output:

```
--- Collection: users (Sample) ---
  --- Document: user123 ---
  {
    "name": "John Doe",
    "email": "john@example.com",
    "createdAt": "2024-01-01T00:00:00Z"
  }
```

## Using the Output with LLMs

### Example Prompt Template

```
Given this sample of my Firestore data structure:

{paste_output_here}

[Your task-specific prompt...]
```

### Common Use Cases

1. **Schema Analysis**: Ask LLMs to analyze your data structure
2. **Query Generation**: Test query generation against real data patterns
3. **Data Validation**: Develop validation rules based on actual data
4. **Documentation**: Generate documentation from real examples
5. **Edge Case Discovery**: Find unusual patterns in your data

## Security Considerations

1. Never commit your service account key to version control
2. Store the key file securely
3. Use appropriate Firebase Security Rules
4. Be aware of read quotas and billing implications
5. Consider sampling or anonymizing sensitive data

## Limitations

- Maximum recursion depth is configurable (default: 10)
- Some Firestore-specific types may be converted to strings
- Large datasets may take time to process
- Output is written to stdout (redirect to file if needed)

## Troubleshooting

### Common Issues

1. "No module named 'firebase_admin'":

   ```bash
   pip install firebase-admin
   ```

2. "Illegal Firebase credential provided":

   - Ensure your service account key file is valid
   - Check file permissions
   - Verify the JSON format is correct

3. "Permission denied":
   - Check IAM roles in Firebase Console
   - Verify the service account has appropriate permissions

### Getting Help

If you encounter issues:

1. Check the error message details
2. Verify your credentials
3. Ensure you have the correct permissions in Firebase
4. Check your network connection

## License

MIT License - Feel free to modify and distribute as needed.
