const fs = require('fs');
const html = fs.readFileSync('nexus_gaming_arena.html', 'utf8');
const app = fs.readFileSync('static/js/app.js', 'utf8');
const popup = fs.readFileSync('google_auth_popup.html', 'utf8');

const requiredHtmlIds = [
  'modal-login',
  'auth-view-login',
  'auth-view-register',
  'landing-auth-view-login',
  'modal-google-account-picker',
  'google-modal-step-1',
  'google-modal-step-2',
  'google-modal-step-3',
  'google-modal-step-4',
  'google-modal-email-input',
  'google-modal-password-input',
  'modal-keep-login-toggle',
  'modal-keep-login-status',
  'reg-otp-code',
  'btn-send-reg-otp',
  'btn-verify-reg-otp',
  'reg-otp-status',
  'modal-concurrent-session-prohibited'
];

let allFound = true;
requiredHtmlIds.forEach(id => {
  const found = html.includes('id="' + id + '"');
  console.log(id + ':', found ? '✓ Found in HTML' : '✗ Missing in HTML');
  if (!found) allFound = false;
});

const requiredPopupIds = [
  'step-1-account',
  'step-2-password',
  'step-3-verifying',
  'step-4-success',
  'google-email-input',
  'google-password-input',
  'keep-login-checkbox'
];

requiredPopupIds.forEach(id => {
  const found = popup.includes('id="' + id + '"');
  console.log('Popup ID ' + id + ':', found ? '✓ Found in popup' : '✗ Missing in popup');
  if (!found) allFound = false;
});

const appFunctions = [
  'loginWithGoogle',
  'openGoogleAccountPicker',
  'selectGoogleAccountForStep2',
  'goToGoogleModalPasswordStep',
  'goToGoogleModalAccountStep',
  'onToggleModalKeepLogin',
  'verifyWithGoogleInModal',
  'handleGoogleAuthSuccess',
  'autoFillRegistrationOTP',
  'verifyRegistrationOTP',
  'handleRegisterWithOTP',
  'handleLogin'
];

appFunctions.forEach(fn => {
  const found = app.includes('function ' + fn) || app.includes('window.' + fn + ' =');
  console.log(fn + ':', found ? '✓ Defined in app.js' : '✗ Missing in app.js');
  if (!found) allFound = false;
});

if (allFound) {
  console.log('\n>>> ALL 37 MULTI-STEP POPUP & DOM VERIFICATIONS PASSED 100% <<<');
} else {
  console.error('\n>>> FAILURES DETECTED <<<');
  process.exit(1);
}
