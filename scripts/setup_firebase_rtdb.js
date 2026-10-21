const path = require('path');
const toolsPath = 'C:/Users/HP/AppData/Roaming/npm/node_modules/firebase-tools';

async function main() {
    try {
        const { createInstance, checkInstanceNameAvailable, DatabaseInstanceType, DatabaseLocation } = require(path.join(toolsPath, 'lib/management/database.js'));
        const projectId = 'nexus-gaming-arena-28be9';
        const location = DatabaseLocation.US_CENTRAL1;
        let instanceName = `${projectId}-default-rtdb`;
        
        console.log(`Checking availability for RTDB instance: ${instanceName} in ${location}...`);
        const checkOutput = await checkInstanceNameAvailable(projectId, instanceName, DatabaseInstanceType.DEFAULT_DATABASE, location);
        console.log('Check output:', checkOutput);

        if (!checkOutput.available) {
            if (checkOutput.suggestedIds && checkOutput.suggestedIds.length > 0) {
                instanceName = checkOutput.suggestedIds[0];
                console.log(`Using suggested instance name: ${instanceName}`);
            } else {
                throw new Error('No available instance name suggested');
            }
        }

        console.log(`Creating default RTDB instance: ${instanceName}...`);
        const result = await createInstance(projectId, instanceName, location, DatabaseInstanceType.DEFAULT_DATABASE);
        console.log('Created RTDB instance successfully:', result);
    } catch (err) {
        console.error('Error setting up RTDB:', err);
    }
}

main();
