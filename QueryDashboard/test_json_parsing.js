const { chromium } = require('playwright');

(async () => {
    console.log('🔍 Testing JSON parsing in edit button...');
    
    const browser = await chromium.launch({
        headless: false,
        slowMo: 1000
    });
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        // Navigate to table page directly
        await page.goto('http://127.0.0.1:5000/table/1', { waitUntil: 'networkidle' });
        
        // Wait for page to load
        await page.waitForTimeout(2000);
        
        // Get the first edit button
        const editButton = await page.$('.edit-btn');
        if (!editButton) {
            console.log('❌ No edit button found');
            return;
        }
        
        // Get data attributes
        const dataId = await editButton.getAttribute('data-id');
        const dataQueryId = await editButton.getAttribute('data-query-id');
        const dataQueryText = await editButton.getAttribute('data-query-text');
        const dataGroundTruth = await editButton.getAttribute('data-ground-truth');
        
        console.log('📋 Data attributes:');
        console.log(`data-id: ${dataId}`);
        console.log(`data-query-id: ${dataQueryId}`);
        console.log(`data-query-text: ${dataQueryText.substring(0, 100)}...`);
        console.log(`data-ground-truth: ${dataGroundTruth}`);
        
        // Test JSON parsing in browser context
        const jsonTestResult = await page.evaluate((groundTruthStr) => {
            try {
                console.log('Attempting to parse:', groundTruthStr);
                const parsed = JSON.parse(groundTruthStr);
                console.log('Parsing successful:', parsed);
                return { success: true, data: parsed };
            } catch (e) {
                console.log('Parsing failed:', e.message);
                return { success: false, error: e.message };
            }
        }, dataGroundTruth);
        
        console.log('JSON parsing result:', jsonTestResult);
        
        // Now click and see what happens
        console.log('✏️ Clicking edit button...');
        await editButton.click();
        
        await page.waitForTimeout(2000);
        
        // Check console
        const consoleLogs = [];
        page.on('console', msg => {
            consoleLogs.push({ type: msg.type(), text: msg.text() });
        });
        
        // Check if modal appeared
        const modal = await page.$('#addQueryModal');
        const modalVisible = await modal.isVisible();
        console.log(`Modal visible: ${modalVisible}`);
        
        if (modalVisible) {
            console.log('✅ Modal opened successfully!');
            
            // Check field values
            const queryIdValue = await page.$eval('#queryId', el => el.value);
            const queryTextValue = await page.$eval('#queryText', el => el.value);
            const groundTruthValue = await page.$eval('#groundTruth', el => el.value);
            
            console.log('📋 Field values:');
            console.log(`Query ID: ${queryIdValue}`);
            console.log(`Query Text: ${queryTextValue.substring(0, 100)}...`);
            console.log(`Ground Truth: ${groundTruthValue}`);
        } else {
            console.log('❌ Modal did not open');
        }
        
    } catch (error) {
        console.log(`💥 Error: ${error.message}`);
        console.log(error.stack);
    } finally {
        await browser.close();
    }
})();
