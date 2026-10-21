const path = require('path');
const toolsPath = 'C:/Users/HP/AppData/Roaming/npm/node_modules/firebase-tools';

async function main() {
    try {
        const { getGlobalDefaultAccount, setRefreshToken } = require(path.join(toolsPath, 'lib/auth.js'));
        const account = getGlobalDefaultAccount();
        if (account && account.tokens) {
            setRefreshToken(account.tokens.refresh_token);
        }

        const { Client } = require(path.join(toolsPath, 'lib/apiv2.js'));
        const { firebaseStorageOrigin } = require(path.join(toolsPath, 'lib/api.js'));
        const projectId = 'nexus-gaming-arena-28be9';
        
        const client = new Client({
            urlPrefix: firebaseStorageOrigin(),
            apiVersion: 'v1alpha'
        });

        console.log('Checking defaultBucket on firebasestorage.googleapis.com...');
        try {
            const res = await client.get(`/projects/${projectId}/defaultBucket`);
            console.log('defaultBucket result:', res.body);
        } catch (e) {
            console.log('GET defaultBucket failed with status:', e.status, e.message);
            console.log('Trying to POST/create defaultBucket...');
            try {
                const postRes = await client.post(`/projects/${projectId}/defaultBucket`, {
                    location: 'us-central1'
                });
                console.log('POST defaultBucket succeeded:', postRes.body);
            } catch (postErr) {
                console.log('POST defaultBucket failed:', postErr.status, postErr.message, postErr.context?.body);
            }
        }
    } catch (err) {
        console.error('Fatal error:', err);
    }
}

main();
