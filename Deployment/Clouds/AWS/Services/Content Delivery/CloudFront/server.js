const express = require('express');
const app = express();

// Replace with your CloudFront domain
const CLOUDFRONT_DOMAIN = 'http://d1234567890abcdef.cloudfront.net';

app.get('/static-url/:filename', (req, res) => {
  const { filename } = req.params;
  // Optional: validate filename for security
  const url = `${CLOUDFRONT_DOMAIN}/${filename}`;
  res.json({ url });
});

// Example API endpoint for logo
app.get('/logo-url', (req, res) => {
  res.json({ url: `${CLOUDFRONT_DOMAIN}/logo.png` });
});

app.listen(3000, () => {
  console.log('Server running on port 3000.');
});