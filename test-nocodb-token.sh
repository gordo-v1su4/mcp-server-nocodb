#!/bin/bash

# Test NocoDB API Token
# Usage: ./test-nocodb-token.sh <your_token_here>

if [ -z "$1" ]; then
    echo "❌ Usage: $0 <nocodb_api_token>"
    echo "Example: $0 eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    exit 1
fi

TOKEN="$1"
echo "🔍 Testing token: ${TOKEN:0:20}..."

# Test the token
RESPONSE=$(curl -s -H "xc-token: $TOKEN" https://nocodb.v1su4.com/api/v1/db/meta/projects)

if [[ $RESPONSE == *"error"* ]] || [[ $RESPONSE == *"Invalid"* ]]; then
    echo "❌ Token is INVALID"
    echo "Response: $RESPONSE"
    echo ""
    echo "🔧 How to fix:"
    echo "1. Go to nocodb.v1su4.com"
    echo "2. Login to your account"
    echo "3. Go to Account Settings → Tokens"
    echo "4. Generate a new token"
    echo "5. Copy the EXACT token value"
    echo "6. Update in Coolify: NOCODB_API_TOKEN=your_new_token"
    exit 1
else
    echo "✅ Token is VALID!"
    echo "Projects: $RESPONSE"
    echo ""
    echo "🎉 Your token is working correctly!"
fi
