fetch('https://nexus-gaming-arena-28be9.web.app/google_auth_popup.html')
  .then(r => r.text())
  .then(html => {
    console.log('google_auth_popup.html status 200 check:');
    console.log('Wolfy in popup:', html.includes('Wolfy'));
    console.log('wolfy@nexusarena.gg in popup:', html.includes('wolfy@nexusarena.gg'));
    console.log('Alex Vance in popup:', html.includes('Alex Vance'));
    console.log('Pro Gamer One in popup:', html.includes('Pro Gamer One'));
    console.log('Contains Keep me logged in:', html.includes('Keep me logged in'));
    console.log('Contains google-email-input:', html.includes('google-email-input'));
    console.log('Contains google-password-input:', html.includes('google-password-input'));
  })
  .catch(e => console.error(e));
