#!/bin/bash

# Read parameters
ELASTIC_URL="$1"
USERNAME="$2"
PASSWORD="$3"

# Function to perform curl with or without authentication
perform_curl() {
  local url=$1
  local data=$2

  if [ -z "$USERNAME" ] || [ -z "$PASSWORD" ]; then
    curl -s -o /dev/null -w "%{http_code}" -X PUT "$url" -H "Content-Type: application/json" -d@"$data"
  else
    curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:$PASSWORD" -X PUT "$url" -H "Content-Type: application/json" -d@"$data"
  fi
}

# Upload each template
declare -a templates=("access_logs.json" "waf_logs.json" "ddos_logs.json" "bot_logs.json") 

for template in "${templates[@]}"; do
  response_code=$(perform_curl "$ELASTIC_URL/_template/$template" "$template")

  if [ "$response_code" -ne 200 ]; then
    echo "Failed to upload $template, HTTP status code: $response_code"
    exit 1
  fi
done

echo "Configuration complete."
