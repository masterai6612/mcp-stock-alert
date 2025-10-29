#!/bin/bash

echo "📥 IMPORTING N8N WORKFLOWS"
echo "=========================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if n8n is running
print_info "Checking if n8n is running..."
if ! curl -s http://localhost:5678 > /dev/null 2>&1; then
    print_error "n8n is not running. Please start the system first:"
    echo "   ./start_complete_system.sh"
    exit 1
fi

print_status "n8n is running"

# Wait a bit more for n8n to be fully ready
print_info "Waiting for n8n to be fully ready..."
sleep 5

# Import workflows
WORKFLOW_DIR="workflows/n8n-workflows"
IMPORTED_COUNT=0
FAILED_COUNT=0

print_info "Importing workflows from $WORKFLOW_DIR..."
echo

for workflow_file in "$WORKFLOW_DIR"/*.json; do
    if [ -f "$workflow_file" ]; then
        workflow_name=$(basename "$workflow_file" .json)
        print_info "Importing: $workflow_name"
        
        # Try to import the workflow
        response=$(curl -s -X POST \
            -H "Content-Type: application/json" \
            -d @"$workflow_file" \
            http://localhost:5678/rest/workflows/import 2>/dev/null)
        
        if [ $? -eq 0 ] && echo "$response" | grep -q '"id"'; then
            print_status "Successfully imported: $workflow_name"
            IMPORTED_COUNT=$((IMPORTED_COUNT + 1))
        else
            print_warning "Failed to import: $workflow_name"
            FAILED_COUNT=$((FAILED_COUNT + 1))
            
            # Try alternative import method
            print_info "Trying alternative import method for: $workflow_name"
            response2=$(curl -s -X POST \
                -H "Content-Type: application/json" \
                -d @"$workflow_file" \
                http://localhost:5678/rest/workflows 2>/dev/null)
            
            if [ $? -eq 0 ] && echo "$response2" | grep -q '"id"'; then
                print_status "Successfully imported with alternative method: $workflow_name"
                IMPORTED_COUNT=$((IMPORTED_COUNT + 1))
                FAILED_COUNT=$((FAILED_COUNT - 1))
            fi
        fi
        
        sleep 1
    fi
done

echo
echo "=========================="
print_info "📊 IMPORT SUMMARY"
echo "=========================="
print_status "Successfully imported: $IMPORTED_COUNT workflows"
if [ $FAILED_COUNT -gt 0 ]; then
    print_warning "Failed to import: $FAILED_COUNT workflows"
fi

echo
print_info "🌐 Access your workflows at:"
echo "   http://localhost:5678/workflows"
echo
print_info "🔑 Login credentials:"
echo "   Username: admin"
echo "   Password: stockagent123"
echo

if [ $IMPORTED_COUNT -gt 0 ]; then
    print_status "🎉 Workflows are now available in n8n!"
    print_info "💡 Recommended workflows to activate:"
    echo "   • comprehensive-stock-agent - Full 269+ stock analysis"
    echo "   • minimal-comprehensive-agent - Lightweight version"
    echo "   • manual-comprehensive-test - Manual testing"
else
    print_error "No workflows were imported successfully"
    print_info "💡 You can manually import workflows by:"
    echo "   1. Go to http://localhost:5678/workflows"
    echo "   2. Click 'Import from File'"
    echo "   3. Select files from workflows/n8n-workflows/"
fi

echo