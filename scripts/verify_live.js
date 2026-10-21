fetch('https://nexus-gaming-arena-28be9.web.app')
  .then(r => r.text())
  .then(html => {
    console.log('Live contains v=7.0.4:', html.includes('v=7.0.4'));
    const modalStart = html.indexOf('id="modal-google-account-picker"');
    const modalEnd = html.indexOf('id="modal-install-app"');
    const modalHtml = html.substring(modalStart, modalEnd);
    console.log('Wolfy in Google modal:', modalHtml.includes('Wolfy'));
    console.log('wolfy@nexusarena.gg in Google modal:', modalHtml.includes('wolfy@nexusarena.gg'));
    console.log('Alex Vance in Google modal:', modalHtml.includes('Alex Vance'));
    console.log('Pro Gamer One in Google modal:', modalHtml.includes('Pro Gamer One'));
  })
  .catch(e => console.error(e));
