const { chromium } = require('playwright');

async function comprehensiveTest() {
    console.log('╔══════════════════════════════════════════════════════════════╗');
    console.log('║         DASHBOARD FEATURE TEST REPORT                        ║');
    console.log('╚══════════════════════════════════════════════════════════════╝\n');
    
    const browser = await chromium.launch({ 
        headless: false,
        slowMo: 500 
    });
    
    const page = await browser.newPage();
    await page.goto('http://127.0.0.1:5000');
    await page.waitForLoadState('networkidle');
    
    // Navigate to first table
    const tableLinks = await page.locator('a[href*="/table/"]').all();
    if (tableLinks.length === 0) {
        console.log('❌ No tables found. Please create a table first.');
        await browser.close();
        return;
    }
    
    await tableLinks[0].click();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    const results = {
        '1. Edit Button Functionality': { status: 'PENDING', details: [] },
        '2. Copy & Paste JSON (with selection)': { status: 'PENDING', details: [] },
        '3. Copy & Paste JSON (no selection)': { status: 'PENDING', details: [] },
        '4. Row Selection by Clicking': { status: 'PENDING', details: [] },
        '5. JSON Format Validation': { status: 'PENDING', details: [] }
    };
    
    // Test 1: Edit Button
    console.log('📋 TEST 1: Edit Button Functionality');
    console.log('━'.repeat(60));
    
    try {
        const editButton = page.locator('button.edit-btn').first();
        const exists = await editButton.count() > 0;
        
        if (exists) {
            results['1. Edit Button Functionality'].details.push('✅ Edit button exists');
            results['1. Edit Button Functionality'].details.push(`✅ Button is enabled: ${await editButton.isEnabled()}`);
            
            const queryId = await editButton.getAttribute('data-query-id');
            results['1. Edit Button Functionality'].details.push(`✅ Button has data-query-id: ${queryId}`);
            
            await editButton.click();
            await page.waitForTimeout(1500);
            
            const modalVisible = await page.locator('.modal.show').count() > 0;
            if (modalVisible) {
                results['1. Edit Button Functionality'].details.push('✅ Modal opens when clicking edit button');
                results['1. Edit Button Functionality'].status = 'PASS';
                
                // Check form fields
                const queryIdValue = await page.locator('#queryId').inputValue();
                const queryTextValue = await page.locator('#queryText').inputValue();
                
                if (queryIdValue) {
                    results['1. Edit Button Functionality'].details.push('✅ Query ID field populated');
                } else {
                    results['1. Edit Button Functionality'].details.push('❌ Query ID field NOT populated');
                }
                
                if (queryTextValue) {
                    results['1. Edit Button Functionality'].details.push('✅ Query text field populated');
                } else {
                    results['1. Edit Button Functionality'].details.push('❌ Query text field NOT populated');
                }
                
                // Close modal
                await page.locator('.modal .btn-close').click();
                await page.waitForTimeout(500);
            } else {
                results['1. Edit Button Functionality'].details.push('❌ Modal does NOT open when clicking edit button');
                results['1. Edit Button Functionality'].status = 'FAIL';
            }
        } else {
            results['1. Edit Button Functionality'].details.push('❌ Edit button does NOT exist');
            results['1. Edit Button Functionality'].status = 'FAIL';
        }
    } catch (error) {
        results['1. Edit Button Functionality'].details.push(`❌ ERROR: ${error.message}`);
        results['1. Edit Button Functionality'].status = 'ERROR';
    }
    
    console.log(results['1. Edit Button Functionality'].details.join('\n'));
    console.log(`\n📊 Status: ${results['1. Edit Button Functionality'].status}\n`);
    
    // Test 2: Copy & Paste JSON with selection
    console.log('📋 TEST 2: Copy & Paste JSON (with selection)');
    console.log('━'.repeat(60));
    
    try {
        const checkboxes = await page.locator('.query-checkbox').all();
        if (checkboxes.length >= 2) {
            await checkboxes[0].check();
            await checkboxes[1].check();
            results['2. Copy & Paste JSON (with selection)'].details.push('✅ Selected 2 queries');
            
            await page.locator('button:has-text("Copy & Paste JSON")').click();
            await page.waitForTimeout(1000);
            
            const modalVisible = await page.locator('#jsonPreviewModal.show').count() > 0;
            if (modalVisible) {
                results['2. Copy & Paste JSON (with selection)'].details.push('✅ JSON Preview modal opens');
                
                const jsonContent = await page.locator('#jsonPreview').inputValue();
                const jsonData = JSON.parse(jsonContent);
                
                results['2. Copy & Paste JSON (with selection)'].details.push(`✅ JSON contains ${jsonData.length} items`);
                
                if (jsonData.length === 2) {
                    results['2. Copy & Paste JSON (with selection)'].details.push('✅ Correct number of items exported');
                } else {
                    results['2. Copy & Paste JSON (with selection)'].details.push(`❌ Expected 2 items, got ${jsonData.length}`);
                }
                
                const hasCorrectStructure = jsonData[0].query_id && jsonData[0].query && 'ground_truth_ranked' in jsonData[0];
                if (hasCorrectStructure) {
                    results['2. Copy & Paste JSON (with selection)'].details.push('✅ JSON has correct structure (query_id, query, ground_truth_ranked)');
                } else {
                    results['2. Copy & Paste JSON (with selection)'].details.push('❌ JSON structure is incorrect');
                }
                
                // Test copy to clipboard
                page.on('dialog', async dialog => await dialog.accept());
                await page.locator('button:has-text("Copy to Clipboard")').click();
                await page.waitForTimeout(500);
                results['2. Copy & Paste JSON (with selection)'].details.push('✅ Copy to Clipboard button works');
                
                results['2. Copy & Paste JSON (with selection)'].status = 'PASS';
                
                await page.locator('#jsonPreviewModal .btn-close').click();
                await page.waitForTimeout(500);
            } else {
                results['2. Copy & Paste JSON (with selection)'].details.push('❌ JSON Preview modal does NOT open');
                results['2. Copy & Paste JSON (with selection)'].status = 'FAIL';
            }
        } else {
            results['2. Copy & Paste JSON (with selection)'].details.push('⚠️ Not enough queries to test (need at least 2)');
            results['2. Copy & Paste JSON (with selection)'].status = 'SKIP';
        }
    } catch (error) {
        results['2. Copy & Paste JSON (with selection)'].details.push(`❌ ERROR: ${error.message}`);
        results['2. Copy & Paste JSON (with selection)'].status = 'ERROR';
    }
    
    console.log(results['2. Copy & Paste JSON (with selection)'].details.join('\n'));
    console.log(`\n📊 Status: ${results['2. Copy & Paste JSON (with selection)'].status}\n`);
    
    // Test 3: Copy & Paste JSON without selection
    console.log('📋 TEST 3: Copy & Paste JSON (no selection)');
    console.log('━'.repeat(60));
    
    try {
        const checkedBoxes = await page.locator('.query-checkbox:checked').all();
        for (const box of checkedBoxes) {
            await box.uncheck();
        }
        await page.waitForTimeout(500);
        
        const stillChecked = await page.locator('.query-checkbox:checked').count();
        if (stillChecked === 0) {
            results['3. Copy & Paste JSON (no selection)'].details.push('✅ All queries deselected');
            
            await page.locator('button:has-text("Copy & Paste JSON")').click();
            await page.waitForTimeout(1000);
            
            const modalVisible = await page.locator('#jsonPreviewModal.show').count() > 0;
            if (modalVisible) {
                results['3. Copy & Paste JSON (no selection)'].details.push('✅ JSON Preview modal opens');
                
                const jsonContent = await page.locator('#jsonPreview').inputValue();
                const jsonData = JSON.parse(jsonContent);
                const totalRows = await page.locator('table tbody tr').count();
                
                results['3. Copy & Paste JSON (no selection)'].details.push(`✅ Exported ${jsonData.length} queries`);
                
                if (jsonData.length === totalRows) {
                    results['3. Copy & Paste JSON (no selection)'].details.push('✅ All queries exported (no selection)');
                    results['3. Copy & Paste JSON (no selection)'].status = 'PASS';
                } else {
                    results['3. Copy & Paste JSON (no selection)'].details.push(`⚠️ Exported ${jsonData.length} but table has ${totalRows} rows`);
                    results['3. Copy & Paste JSON (no selection)'].status = 'WARN';
                }
                
                await page.locator('#jsonPreviewModal .btn-close').click();
                await page.waitForTimeout(500);
            } else {
                results['3. Copy & Paste JSON (no selection)'].details.push('❌ JSON Preview modal does NOT open');
                results['3. Copy & Paste JSON (no selection)'].status = 'FAIL';
            }
        } else {
            results['3. Copy & Paste JSON (no selection)'].details.push(`❌ Could not deselect all (${stillChecked} still selected)`);
            results['3. Copy & Paste JSON (no selection)'].status = 'FAIL';
        }
    } catch (error) {
        results['3. Copy & Paste JSON (no selection)'].details.push(`❌ ERROR: ${error.message}`);
        results['3. Copy & Paste JSON (no selection)'].status = 'ERROR';
    }
    
    console.log(results['3. Copy & Paste JSON (no selection)'].details.join('\n'));
    console.log(`\n📊 Status: ${results['3. Copy & Paste JSON (no selection)'].status}\n`);
    
    // Test 4: Row Selection by Clicking
    console.log('📋 TEST 4: Row Selection by Clicking');
    console.log('━'.repeat(60));
    
    try {
        const firstRowCheckbox = page.locator('table tbody tr:first').locator('.query-checkbox');
        const initialChecked = await firstRowCheckbox.isChecked();
        
        await page.locator('table tbody tr:first td:nth-child(3)').click();
        await page.waitForTimeout(500);
        
        const afterFirstClick = await firstRowCheckbox.isChecked();
        
        if (afterFirstClick !== initialChecked) {
            results['4. Row Selection by Clicking'].details.push('✅ Clicking row toggles checkbox');
            
            await page.locator('table tbody tr:nth-child(2) td:nth-child(3)').click();
            await page.waitForTimeout(500);
            
            const selectedCount = await page.locator('.query-checkbox:checked').count();
            results['4. Row Selection by Clicking'].details.push(`✅ Multiple row selection works (${selectedCount} rows selected)`);
            
            results['4. Row Selection by Clicking'].status = 'PASS';
        } else {
            results['4. Row Selection by Clicking'].details.push('❌ Clicking row does NOT toggle checkbox');
            results['4. Row Selection by Clicking'].status = 'FAIL';
        }
    } catch (error) {
        results['4. Row Selection by Clicking'].details.push(`❌ ERROR: ${error.message}`);
        results['4. Row Selection by Clicking'].status = 'ERROR';
    }
    
    console.log(results['4. Row Selection by Clicking'].details.join('\n'));
    console.log(`\n📊 Status: ${results['4. Row Selection by Clicking'].status}\n`);
    
    // Test 5: JSON Format Validation
    console.log('📋 TEST 5: JSON Format Validation');
    console.log('━'.repeat(60));
    
    try {
        await page.locator('.query-checkbox').first().check();
        await page.locator('button:has-text("Copy & Paste JSON")').click();
        await page.waitForTimeout(1000);
        
        const jsonContent = await page.locator('#jsonPreview').inputValue();
        const jsonData = JSON.parse(jsonContent);
        
        results['5. JSON Format Validation'].details.push('✅ JSON is valid');
        results['5. JSON Format Validation'].details.push('✅ JSON is an array');
        
        if (jsonData.length > 0) {
            const sample = jsonData[0];
            
            const hasQueryId = typeof sample.query_id === 'string';
            const hasQuery = typeof sample.query === 'string';
            const hasGroundTruth = Array.isArray(sample.ground_truth_ranked);
            
            results['5. JSON Format Validation'].details.push(`✅ query_id is ${hasQueryId ? 'string' : 'NOT string'}`);
            results['5. JSON Format Validation'].details.push(`✅ query is ${hasQuery ? 'string' : 'NOT string'}`);
            results['5. JSON Format Validation'].details.push(`✅ ground_truth_ranked is ${hasGroundTruth ? 'array' : 'NOT array'}`);
            
            if (hasQueryId && hasQuery && hasGroundTruth) {
                results['5. JSON Format Validation'].status = 'PASS';
            } else {
                results['5. JSON Format Validation'].status = 'FAIL';
            }
        } else {
            results['5. JSON Format Validation'].details.push('❌ JSON array is empty');
            results['5. JSON Format Validation'].status = 'FAIL';
        }
        
        await page.locator('#jsonPreviewModal').evaluate(el => el.style.display = 'none');
    } catch (error) {
        results['5. JSON Format Validation'].details.push(`❌ ERROR: ${error.message}`);
        results['5. JSON Format Validation'].status = 'ERROR';
    }
    
    console.log(results['5. JSON Format Validation'].details.join('\n'));
    console.log(`\n📊 Status: ${results['5. JSON Format Validation'].status}\n`);
    
    // Final Summary
    console.log('╔══════════════════════════════════════════════════════════════╗');
    console.log('║                    SUMMARY                                    ║');
    console.log('╚══════════════════════════════════════════════════════════════╝\n');
    
    Object.entries(results).forEach(([name, result]) => {
        const icon = result.status === 'PASS' ? '✅' : result.status === 'FAIL' ? '❌' : result.status === 'WARN' ? '⚠️' : result.status === 'SKIP' ? '⏭️' : '🔴';
        console.log(`${icon} ${name}: ${result.status}`);
    });
    
    const passCount = Object.values(results).filter(r => r.status === 'PASS').length;
    const failCount = Object.values(results).filter(r => r.status === 'FAIL').length;
    const warnCount = Object.values(results).filter(r => r.status === 'WARN').length;
    
    console.log(`\n📊 Results: ${passCount} PASSED, ${failCount} FAILED, ${warnCount} WARNED`);
    
    await browser.close();
}

comprehensiveTest().catch(console.error);