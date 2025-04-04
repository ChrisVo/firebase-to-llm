# Firebase to LLM Data Dump Tool

A Python script to dump Firestore database contents recursively, making it easy to export data for analysis or LLM training purposes.

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

Basic usage:

```bash
python firebase-to-llm.py path/to/your/serviceAccountKey.json
```

With optional parameters:

```bash
python firebase-to-llm.py path/to/your/serviceAccountKey.json --project-id your-project-id --max-depth 5
```

### Command Line Arguments

- `key_file`: (Required) Path to your Firebase Admin SDK service account key file (JSON)
- `--project-id`: (Optional) Firebase Project ID (usually inferred from key file)
- `--max-depth`: (Optional) Maximum recursion depth for subcollections (default: 10)

## Output Format

The script outputs data in a hierarchical format:

- Top-level collections are listed first
- For each collection:
  - Documents are displayed with their IDs
  - Document data is shown in JSON format
  - Subcollections (if any) are recursively displayed
  - Timestamps are converted to ISO 8601 format

Example output:

```
--- Processing Collection: users ---
  --- Document: user123 ---
  {
    "name": "John Doe",
    "email": "john@example.com",
    "createdAt": "2024-01-01T00:00:00Z"
  }
```

## Error Handling

The script handles several common scenarios:

- Circular references in documents (warns and continues)
- Invalid credentials
- Missing permissions
- Network issues
- Empty collections

## Security Considerations

1. Never commit your service account key to version control
2. Store the key file securely
3. Use appropriate Firebase Security Rules
4. Be aware of read quotas and billing implications

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
