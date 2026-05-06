const { chromium } = require('playwright');

(async () => {
    console.log('Starting comprehensive edit button test...');
    
    // Launch browser with console logging
    const browser = await chromium.launch({
        headless: false,
        slowMo: 500 // Slow down actions for better visibility
    });
    
    const context = await browser.newContext({
        viewport: { width: 1280, height: 720 }
    });
    
    const page = await context.newPage();
    
    // Collect console messages
    const consoleMessages = [];
    const errors = [];
    const warnings = [];
    
    page.on('console', msg => {
        const type = msg.type();
        const text = msg.text();
        consoleMessages.push({ type, text });
        
        if (type === 'error') {
            errors.push(text);
            console.log(`🔴 CONSOLE ERROR: ${text}`);
        } else if (type === 'warning') {
            warnings.push(text);
            console.log(`⚠️  CONSOLE WARNING: ${text}`);
        } else {
            console.log(`📋 CONSOLE ${type.toUpperCase()}: ${text}`);
        }
    });
    
    page.on('pageerror', error => {
        console.log(`💥 PAGE ERROR: ${error.message}`);
        errors.push(`PAGE ERROR: ${error.message}`);
    });
    
    try {
        // Navigate to the main page
        console.log('🌐 Navigating to http://127.0.0.1:5000');
        await page.goto('http://127.0.0.1:5000', { waitUntil: 'networkidle' });
        
        // Take screenshot of main page
        await page.screenshot({ path: 'screenshots/01-main-page.png' });
        console.log('✅ Main page loaded, screenshot saved');
        
        // Look for any table link
        console.log('🔍 Looking for tables...');
        const tableLinks = await page.$$('a[href*="/table/"]');
        
        if (tableLinks.length === 0) {
            console.log('❌ No tables found! Creating a test table first...');
            
            // Create a test table
            await page.click('button:has-text("Create Table")');
            await page.fill('input[name="name"]', 'Test Table for Edit');
            await page.click('button:has-text("Create")');
            await page.waitForTimeout(1000);
        }
        
        // Get table links again
        const updatedTableLinks = await page.$$('a[href*="/table/"]');
        
        if (updatedTableLinks.length === 0) {
            console.log('❌ Still no tables found. Please create a table first.');
            return;
        }
        
        console.log(`✅ Found ${updatedTableLinks.length} table(s)`);
        
        // Click on the first table
        const firstTableLink = updatedTableLinks[0];
        const tableUrl = await firstTableLink.getAttribute('href');
        console.log(`📂 Navigating to table: ${tableUrl}`);
        
        await firstTableLink.click();
        await page.waitForLoadState('networkidle');
        
        // Take screenshot of table page
        await page.screenshot({ path: 'screenshots/02-table-page.png' });
        console.log('✅ Table page loaded, screenshot saved');
        
        // Check if there are any queries
        console.log('🔍 Looking for queries in the table...');
        const editButtons = await page.$$('.edit-btn');
        
        if (editButtons.length === 0) {
            console.log('❌ No queries found! Creating a test query first...');
            
            // Create a test query
            await page.click('button:has-text("Add Query")');
            await page.waitForTimeout(500);
            await page.fill('#queryId', 'TEST-001');
            await page.fill('#queryText', 'This is a test query for editing functionality.');
            await page.fill('#groundTruth', 'A.6.1, A.6.2');
            await page.click('button:has-text("Save")');
            await page.waitForTimeout(1000);
            
            // Get edit buttons again
            const updatedEditButtons = await page.$$('.edit-btn');
            if (updatedEditButtons.length === 0) {
                console.log('❌ Still no queries found after creating one.');
                return;
            }
        }
        
        // Get edit buttons again
        const finalEditButtons = await page.$$('.edit-btn');
        console.log(`✅ Found ${finalEditButtons.length} query/queries) with edit buttons`);
        
        // Clear console messages before clicking edit
        consoleMessages.length = 0;
        errors.length = 0;
        warnings.length = 0;
        
        // Get the first edit button and extract its data attributes
        const firstEditButton = finalEditButtons[0];
        const dataId = await firstEditButton.getAttribute('data-id');
        const dataQueryId = await firstEditButton.getAttribute('data-query-id');
        const dataQueryText = await firstEditButton.getAttribute('data-query-text');
        const dataGroundTruth = await firstEditButton.getAttribute('data-ground-truth');
        
        console.log('📋 Edit button data attributes:');
        console.log(`   - data-id: ${dataId}`);
        console.log(`   - data-query-id: ${dataQueryId}`);
        console.log(`   - data-query-text: ${dataQueryText.substring(0, 100)}...`);
        console.log(`   - data-ground-truth: ${dataGroundTruth.substring(0, 100)}...`);
        
        // Take screenshot before clicking edit
        await page.screenshot({ path: 'screenshots/03-before-edit-click.png' });
        
        console.log('✏️  Clicking the first edit button...');
        await firstEditButton.click();
        
        // Wait for modal to appear
        await page.waitForTimeout(1000);
        
        // Take screenshot after clicking edit
        await page.screenshot({ path: 'screenshots/04-after-edit-click.png' });
        
        // Check if modal is visible
        console.log('🔍 Checking if edit modal opened...');
        const modal = await page.$('#addQueryModal');
        const modalVisible = await modal.isVisible();
        
        if (modalVisible) {
            console.log('✅ Modal is visible!');
        } else {
            console.log('❌ Modal is NOT visible!');
        }
        
        // Check if modal has 'show' class
        const modalHasShowClass = await modal.evaluate(el => el.classList.contains('show'));
        console.log(`   Modal has 'show' class: ${modalHasShowClass}`);
        
        // Check modal display style
        const modalDisplayStyle = await modal.evaluate(el => window.getComputedStyle(el).display);
        console.log(`   Modal display style: ${modalDisplayStyle}`);
        
        // Check body for modal-open class
        const bodyHasModalOpen = await page.evaluate(() => document.body.classList.contains('modal-open'));
        console.log(`   Body has 'modal-open' class: ${bodyHasModalOpen}`);
        
        if (modalVisible) {
            // Check if fields are populated
            console.log('🔍 Checking if fields are populated...');
            
            const modalTitle = await page.$('#queryModalTitle');
            const titleText = await modalTitle.textContent();
            console.log(`   Modal title: "${titleText}"`);
            
            const editQueryId = await page.$('#editQueryId');
            const editQueryIdValue = await editQueryId.inputValue();
            console.log(`   Hidden editQueryId: "${editQueryIdValue}"`);
            
            const queryIdField = await page.$('#queryId');
            const queryIdValue = await queryIdField.inputValue();
            console.log(`   Query ID field: "${queryIdValue}"`);
            
            const queryTextField = await page.$('#queryText');
            const queryTextValue = await queryTextField.inputValue();
            console.log(`   Query Text field: "${queryTextValue.substring(0, 100)}${queryTextValue.length > 100 ? '...' : ''}"`);
            
            const groundTruthField = await page.$('#groundTruth');
            const groundTruthValue = await groundTruthField.inputValue();
            console.log(`   Ground Truth field: "${groundTruthValue}"`);
            
            // Verify field values
            console.log('✅ Verifying field values...');
            const fieldsPopulated = editQueryIdValue && queryIdValue && queryTextValue;
            
            if (fieldsPopulated) {
                console.log('✅ All fields are populated correctly!');
            } else {
                console.log('❌ Some fields are not empty:');
                console.log(`   editQueryId: ${editQueryIdValue ? '✅' : '❌'}`);
                console.log(`   queryId: ${queryIdValue ? '✅' : '❌'}`);
                console.log(`   queryText: ${queryTextValue ? '✅' : '❌'}`);
            }
            
            // Try making a small edit
            console.log('✏️  Making a small edit to the query...');
            const editedText = queryTextValue + ' (Edited)';
            await queryTextField.fill(editedText);
            
            // Take screenshot before saving
            await page.screenshot({ path: 'screenshots/05-after-editing-text.png' });
            
            console.log('💾 Saving the edit...');
            
            // Setup network monitoring
            let saveRequestCompleted = false;
            let saveResponse = null;
            
            page.on('response', async response => {
                const url = response.url();
                if (url.includes('/api/queries/') && response.request().method() === 'PUT') {
                    saveRequestResponseCompleted = true;
                    saveResponse = response;
                    console.log(`📡 Save API response status: ${response.status()}`);
                    
                    try {
                        const body = await response.text();
                        console.log(`📡 Save API response body: ${body}`);
                    } catch (e) {
                        console.log(`📡 Could not read response body`);
                    }
                }
            });
            
            await page.click('button:has-text("Save")');
            
            // Wait for save to complete and page to reload
            await page.waitForTimeout(2000);
            
            console.log('✅ Save clicked');
            
        } else {
            console.log('❌ Modal did not open, skipping field checks and edit save');
        }
        
    } catch (error) {
        console.log(`💥 Test error: ${error.message}`);
        console.log(error.stack);
    } finally {
        // Summary report
        console.log('\n========================================');
        console.log('📊 TEST SUMMARY');
        console.log('========================================');
        console.log(`Total console messages: ${consoleMessages.length}`);
        console.log(`Errors: ${errors.length}`);
        console.log(`Warnings: ${warnings.length}`);
        
        if (errors.length > 0) {
            console.log('\n❌ ERRORS:');
            errors.forEach((err, i) => console.log(`   ${i + 1}. ${err}`));
        }
        
        if (warnings.length > 0) {
            console.log('\n⚠️  WARNINGS:');
            warnings.forEach((warn, i) => console.log(`   ${i + 1}. ${warn}`));
        }
        
        console.log('\n✅ All console messages:');
        consoleMessages.forEach((msg, i) => {
            console.log(`   ${i + 1}. [${msg.type.toUpperCase()}] ${msg.text}`);
        });
        
        console.log('\n📸 Screenshots saved to:');
        console.log('   - screenshots/01-main-page.png');
        console.log('   - screenshots/02-table-page.png');
        console.log('   - screenshots/03-before-edit-click.png');
        console.log('   - screenshots/04-after-edit-click.png');
        console.log('   - screenshots/05-after-editing-text.png');
        
        await browser.close();
    }
})();
