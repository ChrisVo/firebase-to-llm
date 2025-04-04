import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import sys
import os
import argparse  # To handle command-line arguments
import datetime
from google.cloud.firestore_v1 import DocumentReference
from google.cloud.firestore_v1 import GeoPoint
from google.protobuf.timestamp_pb2 import Timestamp as FirestoreTimestamp

# --- Configuration ---
# You MUST provide the path to your service account key file.
# Generate it from Firebase Console: Project Settings > Service accounts > Generate new private key
# Example: SERVICE_ACCOUNT_KEY_PATH = "/path/to/your/serviceAccountKey.json"


# --- Helper function to handle non-serializable types for JSON ---
def json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (firestore.SERVER_TIMESTAMP.__class__, FirestoreTimestamp)):
        # Convert Firestore Timestamps to ISO 8601 strings (UTC)
        if hasattr(obj, "ToDatetime"):
            dt_utc = obj.ToDatetime().replace(tzinfo=datetime.timezone.utc)
        else:
            dt_utc = datetime.datetime.fromtimestamp(
                obj.seconds + obj.nanos / 1e9, tz=datetime.timezone.utc
            )
        return dt_utc.isoformat(timespec="milliseconds") + "Z"
    if isinstance(obj, DocumentReference):
        # Represent DocumentReferences by their path string
        return f"Reference(path='{obj.path}')"
    if isinstance(obj, GeoPoint):
        # Represent GeoPoints as a dictionary
        return {"latitude": obj.latitude, "longitude": obj.longitude}
    if obj == firestore.SERVER_TIMESTAMP:
        # Handle ServerTimestamp sentinel value
        return "firestore.SERVER_TIMESTAMP"
    if isinstance(obj, (datetime.date, datetime.datetime)):
        # Handle standard Python datetime objects just in case
        return obj.isoformat()

    # If none of the above custom types, let the default encoder try
    # If it still fails, fall back to string representation as a last resort.
    try:
        # Let default JSON encoder handle primitive types & serializable objects
        # Attempting a quick check if it's directly serializable
        json.dumps(obj)
        return obj
    except TypeError:
        # For anything else not handled above
        return str(obj)
    except Exception as e:
        # Catch other potential serialization errors
        print(
            f"Warning: Could not serialize object of type {type(obj)}: {e}",
            file=sys.stderr,
        )
        return f"Unserializable({type(obj).__name__})"


# --- Recursive Function to Dump Collections and Documents ---
def dump_collection(col_ref, current_depth=0, max_depth=10, no_limit=False):
    """Recursively dumps documents and subcollections."""
    if current_depth > max_depth:
        print(
            f"{'  ' * current_depth}!!! Max recursion depth ({max_depth}) reached for collection: {col_ref.id}. Stopping recursion here. !!!"
        )
        return

    print(f"\n{'  ' * current_depth}-----------------------------------------")
    print(f"{'  ' * current_depth}--- Processing Collection: {col_ref.id} ---")
    print(f"{'  ' * current_depth}-----------------------------------------")
    doc_count = 0
    try:
        # Define the default limit
        limit_count = 5

        # Conditionally create the query based on no_limit parameter
        if no_limit:
            print(
                f"{'  ' * current_depth}Fetching ALL documents from collection: {col_ref.id}"
            )
            query = col_ref  # No limit applied
        else:
            print(
                f"{'  ' * current_depth}Fetching up to {limit_count} documents from collection: {col_ref.id}"
            )
            query = col_ref.limit(limit_count)  # Apply the limit

        # Use stream() on the potentially limited query
        docs_stream = query.stream()
        for doc_snapshot in docs_stream:
            doc_count += 1
            doc_ref = doc_snapshot.reference
            doc_data = doc_snapshot.to_dict()

            print(f"\n{'  ' * (current_depth + 1)}--- Document: {doc_ref.id} ---")
            # Pretty print the document data as JSON
            print(
                json.dumps(
                    doc_data, indent=2, default=json_serializer, ensure_ascii=False
                )
            )

            # --- Recurse into Subcollections ---
            subcollections = doc_ref.collections()
            sub_col_list = list(subcollections)  # Consume iterator
            if sub_col_list:
                print(
                    f"{'  ' * (current_depth + 1)}--- Checking subcollections for document {doc_ref.id} ---"
                )
                for sub_col_ref in sub_col_list:
                    dump_collection(
                        sub_col_ref, current_depth + 1, max_depth, no_limit=no_limit
                    )  # Recursive call
            # --- End Subcollection Recursion ---

        if doc_count == 0:
            print(
                f"{'  ' * (current_depth + 1)}(Collection '{col_ref.id}' appears empty or has no documents directly within it)"
            )

    except Exception as e:
        print(
            f"\n!!! Warning: Error processing collection '{col_ref.id}'. Skipping collection. !!!"
        )
        print(f"{'  ' * current_depth}Error details: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Dump Firestore data recursively to standard output.",
        epilog="Make sure you have generated a service account key JSON file from your Firebase project settings.",
    )
    parser.add_argument(
        "key_file",
        help="Path to your Firebase Admin SDK service account key file (JSON).",
    )
    parser.add_argument(
        "--project-id",
        help="Firebase Project ID (optional, usually inferred from key file).",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=10,
        help="Maximum recursion depth for subcollections (default: 10).",
    )
    parser.add_argument(
        "--no-limit",
        action="store_true",
        default=False,
        help="Fetch all documents in each collection, overriding the default limit of 5.",
    )

    args = parser.parse_args()

    service_account_key_path = args.key_file
    project_id_override = args.project_id
    max_recursion_depth = args.max_depth

    if not os.path.exists(service_account_key_path):
        print(
            f"Error: Service account key file not found at '{service_account_key_path}'"
        )
        sys.exit(1)

    print("--- Starting Firestore Data Dump (Python Admin SDK) ---")

    try:
        print(
            f"\nAttempting to load service account key from: {service_account_key_path}"
        )
        with open(service_account_key_path, "r") as f:
            print("Successfully opened key file")
            key_data = json.load(f)
            print("Successfully parsed key file JSON")

        # Initialize Firebase Admin SDK
        print("Initializing credentials...")
        cred = credentials.Certificate(
            key_data
        )  # Changed this line to use the parsed JSON directly
        print("Credentials initialized successfully")

        init_options = {"credential": cred}
        if project_id_override:
            init_options["projectId"] = project_id_override
            print(f"Using override project ID: {project_id_override}")

        # Check if already initialized
        if not firebase_admin._apps:
            print("Initializing new Firebase Admin app...")
            firebase_admin.initialize_app(
                cred
            )  # Simplified this to just use the credentials
            print("Firebase Admin app initialized successfully")
        else:
            print("Firebase Admin already initialized")

        db = firestore.client()
        actual_project_id = firebase_admin.get_app().project_id
        print(
            f"--- Successfully initialized Firebase Admin SDK for project: {actual_project_id} ---"
        )

    except Exception as e:
        print(f"\nDetailed error initializing Firebase Admin SDK:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Ensure the key file is valid and has the necessary permissions in IAM.")
        sys.exit(1)

    # --- Get and Dump Top-Level Collections ---
    try:
        print("\nFetching top-level collections...")
        top_level_collections = list(
            db.collections()
        )  # Get iterator and convert to list

        if not top_level_collections:
            print("No top-level collections found in this database.")
            print("--- Firestore Data Dump Complete (No Data) ---")
            sys.exit(0)

        print(f"Found {len(top_level_collections)} top-level collections.")
        print(
            "\nFetching data recursively (this may take time and incur read costs)..."
        )

        for collection_ref in top_level_collections:
            dump_collection(
                collection_ref, max_depth=max_recursion_depth, no_limit=args.no_limit
            )  # Start the recursive dump

        print("\n-----------------------------------------")
        print(f"--- End of Firestore Data Dump ({actual_project_id}) ---")

    except Exception as e:
        print(f"\nAn unexpected error occurred during data fetching: {e}")
        sys.exit(1)
