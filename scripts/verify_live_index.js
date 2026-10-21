const https = require('https');

https.get('https://nexus-gaming-arena-28be9.web.app/', (res) => {
  let body = '';
  res.on('data', chunk => body += chunk);
  res.on('end', () => {
    console.log('HTTP Status:', res.statusCode);
    console.log('Contains +100 COINS:', body.includes('+100 COINS'));
    console.log('Contains +500 COINS:', body.includes('+500 COINS'));
    console.log('Contains value="Wolfy":', body.includes('value="Wolfy"'));
    console.log('Contains reg-team-name:', body.includes('id="reg-team-name"'));
    console.log('Contains google_auth_popup.html:', body.includes('google_auth_popup.html'));
  });
});
