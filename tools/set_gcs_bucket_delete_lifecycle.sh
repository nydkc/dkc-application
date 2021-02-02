#!/bin/sh

if [ "$#" -lt 1 ]; then
    echo "Configures lifecycle on a GCS bucket, that will delete any object older than 1 day."
    echo "The purpose of this is to reduce costs with storing temporary data in GCS. Notably,"
    echo "we set this for the Cloud Build artifacts bucket:"
    echo "\tgs://<multi_region>.artifacts.<project_id>.appspot.com"
    echo
    echo "Usage: $0 gs://<bucket_name>"
    exit
fi

GCS_BUCKET="$1"

LIFECYCLE_CONFIG_FILE="/tmp/gcs_bucket_delete_lifecycle_config.json"

cat > "$LIFECYCLE_CONFIG_FILE" <<EOF
{
    "rule": [
        {
            "action": {"type": "Delete"},
            "condition": {"age": 1}
        }
    ]
}
EOF

gsutil lifecycle set "$LIFECYCLE_CONFIG_FILE" "$GCS_BUCKET"
