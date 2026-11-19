/**
 * Inkloom AI - Node.js Server
 * Built with native Node.js (http, fs, path, url, crypto) - zero external dependencies required!
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');
const crypto = require('crypto');

const PORT = process.env.PORT || 8081;
const PYTHON_BACKEND = 'http://localhost:8080';

console.log(`[Inkloom AI] Node server module initialized. Target port: ${PORT}`);

// Export server starter
function createServer() {
  const server = http.createServer((req, res) => {
    // Enable CORS for all incoming requests
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    if (req.method === 'OPTIONS') {
      res.writeHead(204);
      res.end();
      return;
    }

    const parsedUrl = url.parse(req.url, true);

    if (parsedUrl.pathname === '/api/health') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'ok', service: 'Inkloom AI Node Bridge', port: PORT }));
      return;
    }

    // Default response
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ message: 'Inkloom AI Node Server Active' }));
  });

  return server;
}

if (require.main === module) {
  const server = createServer();
  server.listen(PORT, () => {
    console.log(`[Inkloom AI] Node server listening on http://localhost:${PORT}`);
  });
}

module.exports = { createServer };
