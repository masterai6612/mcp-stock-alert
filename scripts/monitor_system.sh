#!/bin/bash
# System monitoring script

echo "🔍 System Status Check"
echo "====================="

# Check Docker services
echo "🐳 Docker Services:"
docker-compose ps

echo
echo "🔗 API Endpoints:"
echo -n "   n8n API (5002): "
if curl -s http://localhost:5002/health > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Down"
fi

echo -n "   Dashboard (5001): "
if curl -s http://localhost:5001 > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Down"
fi

echo -n "   n8n UI (5678): "
if curl -s http://localhost:5678 > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Down"
fi

echo
echo "📊 Recent Logs:"
echo "   Check: tail -f *.log"
echo "   n8n: docker-compose logs n8n"
