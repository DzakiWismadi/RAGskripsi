const { chromium } = require('playwright');

async function testDashboard() {
    console.log('🚀 Starting Dashboard Tests...\n');
    
    const browser = await chromium.launch({ 
        headless: false,
        slowMo: 500 // Slow down actions for better visibility
    });
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Navigate to dashboard
    console.log('📍 Navigating to http://127.0.0.1:5000');
    await page.goto('http://127.0.0.1:5000');
    await page.waitForLoadState('networkidle');
    
    // Get first table link and navigate to it
    console.log('📍 Looking for tables...');
    const tableLinks = await page.locator('a[href*="/table/"]').all();
    
    if (tableLinks.length === 0) {
        console.log('❌ No tables found! Please create a table first.');
        await browser.close();
        return;
    }
    
    console.log(`✅ Found ${tableLinks.length} table(s). Navigating to first table...`);
    await tableLinks[0].click();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Test 1: Edit Button Functionality
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('TEST 1: Edit Button Functionality');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    try {
        // Wait for table to load
        await page.waitForSelector('table tbody tr', { timeout: 10000 });
        
        // Find first edit button
        const editButton = page.locator('button.edit-btn').first();
        const isEditVisible = await editButton.isVisible();
        
        if (isEditVisible) {
            console.log('✅ Edit button found');
            
            // Get query data before clicking edit
            const firstRow = page.locator('table tbody tr').first();
            const queryIdText = await firstRow.locator('td:nth-child(2)').textContent();
            const queryTextPreview = await firstRow.locator('td:nth-child(3)').textContent();
            const groundTruthText = await firstRow.locator('td:nth-child(4)').textContent();
            
            console.log(`📝 Original Query ID: ${queryIdText?.trim()}`);
            console.log(`📝 Query Preview: ${queryTextPreview?.trim()}`);
            console.log(`📝 Ground Truth: ${groundTruthText?.trim()}`);
            
        // Click edit button
        console.log('🖱️  Clicking Edit button...');
        await editButton.click();
        
        // Wait for modal to appear - Bootstrap modal check
        await page.waitForSelector('.modal.show', { timeout: 5000 });
        console.log('✅ Edit modal opened');
            
            // Check modal title
            const modalTitle = await page.locator('#queryModalTitle').textContent();
            console.log(`📋 Modal Title: ${modalTitle?.trim()}`);
            
            // Verify form fields are populated
            const queryIdValue = await page.locator('#queryId').inputValue();
            const queryTextValue = await page.locator('#queryText').inputValue();
            const groundTruthValue = await page.locator('#groundTruth').inputValue();
            
            console.log('\n🔍 Checking if modal is populated correctly:');
            console.log(`   Query ID field: ${queryIdValue ? '✅ Filled' : '❌ Empty'}`);
            console.log(`   Query Text field: ${queryTextValue ? '✅ Filled (' + queryTextValue.length + ' chars)' : '❌ Empty'}`);
            console.log(`   Ground Truth field: ${groundTruthValue ? '✅ Filled' : '❌ Empty'}`);
            
            if (queryIdValue && queryTextValue) {
                console.log('\n✅ TEST 1 PASSED: Edit button works and modal is populated');
                
                // Test editing and saving
                console.log('\n🖊️  Testing edit functionality...');
                const newQueryText = queryTextValue + ' [EDITED]';
                await page.locator('#queryText').clear();
                await page.locator('#queryText').fill(newQueryText);
                console.log(`✏️  Modified query text to: ${newQueryText.substring(0, 50)}...`);
                
                // Click save
                console.log('💾 Clicking Save button...');
                await page.locator('#addQueryModal .btn-primary').click();
                
                // Wait for page reload
                await page.waitForLoadState('networkidle');
                await page.waitForTimeout(2000);
                
                // Verify the edit was saved
                const updatedQueryText = await firstRow.locator('td:nth-child(3)').textContent();
                if (updatedQueryText?.includes('[EDITED]')) {
                    console.log('✅ Changes saved successfully!');
                } else {
                    console.log('⚠️  Changes may not have been saved');
                }
            } else {
                console.log('\n❌ TEST 1 FAILED: Modal fields not populated correctly');
            }
        } else {
            console.log('❌ Edit button not found');
        }
    } catch (error) {
        console.log(`❌ TEST 1 ERROR: ${error.message}`);
    }
    
    // Test 2: Copy & Paste JSON Feature (with selection)
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('TEST 2: Copy & Paste JSON (with selection)');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    try {
        // Select some queries
        console.log('🖱️  Selecting queries...');
        const checkboxes = await page.locator('.query-checkbox').all();
        
        if (checkboxes.length >= 2) {
            // Select first 2 queries
            await checkboxes[0].check();
            await checkboxes[1].check();
            console.log(`✅ Selected 2 queries`);
            
            // Click Copy & Paste JSON button
            console.log('🖱️  Clicking Copy & Paste JSON button...');
            await page.locator('button:has-text("Copy & Paste JSON")').click();
            
            // Wait for modal
            await page.waitForSelector('#jsonPreviewModal.show', { timeout: 5000 });
            console.log('✅ JSON Preview modal opened');
            
            // Get JSON content
            const jsonContent = await page.locator('#jsonPreview').inputValue();
            const jsonData = JSON.parse(jsonContent);
            
            console.log(`\n📄 JSON Data Analysis:`);
            console.log(`   Number of items: ${jsonData.length}`);
            
            if (jsonData.length === 2) {
                console.log('✅ Correct number of items (2 selected queries)');
                
                // Check JSON structure
                const firstItem = jsonData[0];
                const hasCorrectStructure = 
                    'query_id' in firstItem && 
                    'query' in firstItem && 
                    'ground_truth_ranked' in firstItem;
                
                console.log(`\n🔍 JSON Structure Check:`);
                console.log(`   Has query_id: ${'query_id' in firstItem ? '✅' : '❌'}`);
                console.log(`   Has query: ${'query' in firstItem ? '✅' : '❌'}`);
                console.log(`   Has ground_truth_ranked: ${'ground_truth_ranked' in firstItem ? '✅' : '❌'}`);
                
                if (hasCorrectStructure) {
                    console.log(`\n📋 Sample JSON item:`);
                    console.log(JSON.stringify(firstItem, null, 2));
                    
                    // Test copy to clipboard
                    console.log('\n📋 Testing Copy to Clipboard button...');
                    
                    // Setup dialog handler for alert
                    page.on('dialog', async dialog => {
                        console.log(`✅ Alert appeared: "${dialog.message()}"`);
                        await dialog.accept();
                    });
                    
                    await page.locator('button:has-text("Copy to Clipboard")').click();
                    await page.waitForTimeout(1000);
                    
                    console.log('✅ TEST 2 PASSED: Copy & Paste JSON works with selection');
                } else {
                    console.log('❌ TEST 2 FAILED: JSON structure is incorrect');
                }
            } else {
                console.log(`❌ TEST 2 FAILED: Expected 2 items, got ${jsonData.length}`);
            }
            
            // Close modal
            await page.locator('#jsonPreviewModal .btn-secondary').click();
            await page.waitForTimeout(1000);
        } else {
            console.log('⚠️  Not enough queries to test selection (need at least 2)');
        }
    } catch (error) {
        console.log(`❌ TEST 2 ERROR: ${error.message}`);
    }
    
    // Test 3: Copy & Paste JSON (without selection)
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('TEST 3: Copy & Paste JSON (no selection)');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    try {
        // Deselect all
        console.log('🖱️  Deselecting all queries...');
        const checkedBoxes = await page.locator('.query-checkbox:checked').all();
        for (const box of checkedBoxes) {
            await box.uncheck();
        }
        await page.waitForTimeout(500);
        
        const selectedCount = await page.locator('.query-checkbox:checked').count();
        if (selectedCount === 0) {
            console.log('✅ All queries deselected');
            
            // Click Copy & Paste JSON button
            console.log('🖱️  Clicking Copy & Paste JSON button...');
            await page.locator('button:has-text("Copy & Paste JSON")').click();
            
            // Wait for modal
            await page.waitForSelector('#jsonPreviewModal.show', { timeout: 5000 });
            console.log('✅ JSON Preview modal opened');
            
            // Get JSON content
            const jsonContent = await page.locator('#jsonPreview').inputValue();
            const jsonData = JSON.parse(jsonContent);
            
            console.log(`\n📄 JSON Data Analysis:`);
            console.log(`   Total queries exported: ${jsonData.length}`);
            
            // Count total rows in table
            const totalRows = await page.locator('table tbody tr').count();
            console.log(`   Total rows in table: ${totalRows}`);
            
            if (jsonData.length === totalRows) {
                console.log('✅ TEST 3 PASSED: All queries exported when no selection');
            } else {
                console.log(`⚠️  Warning: Exported ${jsonData.length} items but table has ${totalRows} rows`);
            }
            
            // Close modal
            await page.locator('#jsonPreviewModal .btn-secondary').click();
            await page.waitForTimeout(1000);
        } else {
            console.log(`❌ Could not deselect all queries (${selectedCount} still selected)`);
        }
    } catch (error) {
        console.log(`❌ TEST 3 ERROR: ${error.message}`);
    }
    
    // Test 4: Row Selection by Clicking
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('TEST 4: Row Selection by Clicking');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    try {
        // Get first row checkbox
        const firstRowCheckbox = page.locator('table tbody tr:first-child .query-checkbox');
        const firstRow = page.locator('table tbody tr:first-child');
        
        // Initial state
        let isChecked = await firstRowCheckbox.isChecked();
        console.log(`📊 Initial checkbox state: ${isChecked ? 'Checked' : 'Unchecked'}`);
        
        // Click on the row (not on checkbox or buttons)
        console.log('🖱️  Clicking on first row (query text area)...');
        await firstRow.locator('td:nth-child(3)').click();
        await page.waitForTimeout(500);
        
        isChecked = await firstRowCheckbox.isChecked();
        console.log(`📊 After first click: ${isChecked ? 'Checked' : 'Unchecked'}`);
        
        // The checkbox should toggle from unchecked to checked
        if (isChecked) {
            console.log('✅ Checkbox toggled from unchecked to checked');
            
            // Click again to toggle back
            console.log('🖱️  Clicking row again to toggle off...');
            await firstRow.locator('td:nth-child(3)').click();
            await page.waitForTimeout(500);
            
            isChecked = await firstRowCheckbox.isChecked();
            console.log(`📊 After second click: ${isChecked ? 'Checked' : 'Unchecked'}`);
            
            if (!isChecked) {
                console.log('✅ TEST 4 PASSED: Row clicking toggles checkbox correctly');
            } else {
                console.log('⚠️  Checkbox did not toggle back to unchecked');
            }
        }
        
        // Test selecting multiple rows
        console.log('\n🖱️  Testing multiple row selection...');
        const rows = await page.locator('table tbody tr').all();
        const rowsToClick = Math.min(3, rows.length);
        
        for (let i = 0; i < rowsToClick; i++) {
            await rows[i].locator('td:nth-child(3)').click();
            await page.waitForTimeout(300);
        }
        
        const selectedCount = await page.locator('.query-checkbox:checked').count();
        console.log(`✅ Selected ${selectedCount} rows by clicking`);
        
        if (selectedCount === rowsToClick) {
            console.log('✅ Multiple row selection works correctly');
        } else {
            console.log(`⚠️  Expected ${rowsToClick} selected, got ${selectedCount}`);
        }
    } catch (error) {
        console.log(`❌ TEST 4 ERROR: ${error.message}`);
    }
    
    // Test 5: JSON Format Validation
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('TEST 5: JSON Format Validation');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    try {
        // Select a query and export JSON
        await page.locator('.query-checkbox').first().check();
        await page.locator('button:has-text("Copy & Paste JSON")').click();
        await page.waitForSelector('#jsonPreviewModal.show', { timeout: 5000 });
        
        const jsonContent = await page.locator('#jsonPreview').inputValue();
        console.log('\n📄 Raw JSON Content (first 500 chars):');
        console.log(jsonContent.substring(0, 500) + '...');
        
        // Parse and validate
        const jsonData = JSON.parse(jsonContent);
        
        console.log('\n🔍 Detailed JSON Validation:');
        console.log(`   Valid JSON: ✅`);
        console.log(`   Array: ${Array.isArray(jsonData) ? '✅' : '❌'}`);
        console.log(`   Items: ${jsonData.length}`);
        
        if (jsonData.length > 0) {
            const sample = jsonData[0];
            console.log('\n📋 Sample item structure:');
            console.log(`   query_id: ${sample.query_id ? '✅ (' + typeof sample.query_id + ')' : '❌'}`);
            console.log(`   query: ${sample.query ? '✅ (' + typeof sample.query + ')' : '❌'}`);
            console.log(`   ground_truth_ranked: ${sample.ground_truth_ranked ? '✅ (' + typeof sample.ground_truth_ranked + ')' : '❌'}`);
            
            // Validate types
            const isValid = 
                typeof sample.query_id === 'string' &&
                typeof sample.query === 'string' &&
                Array.isArray(sample.ground_truth_ranked);
            
            if (isValid) {
                console.log('\n✅ TEST 5 PASSED: JSON format is valid and correctly structured');
                console.log('\n📋 Full sample item:');
                console.log(JSON.stringify(sample, null, 2));
            } else {
                console.log('\n❌ TEST 5 FAILED: JSON structure has type issues');
            }
        }
    } catch (error) {
        console.log(`❌ TEST 5 ERROR: ${error.message}`);
    }
    
    // Summary
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🎉 ALL TESTS COMPLETED');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    await page.waitForTimeout(5000);
    await browser.close();
}

// Run tests
testDashboard().catch(console.error);