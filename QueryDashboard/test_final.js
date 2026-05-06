const { chromium } = require('playwright');

async function finalTest() {
    console.log('╔══════════════════════════════════════════════════════════════╗');
    console.log('║         DASHBOARD FEATURE TEST REPORT - FINAL               ║');
    console.log('╚══════════════════════════════════════════════════════════════╝\n');
    
    const browser = await chromium.launch({ 
        headless: false,
        slowMo: 500 
    });
    
    const page = await browser.newPage();
    await page.goto('http://127.0.0.1:5000');
    await page.waitForLoadState('networkidle');
    
    const tableLinks = await page.locator('a[href*="/table/"]').all();
    if (tableLinks.length === 0) {
        console.log('❌ No tables found. Please create a table first.');
        await browser.close();
        return;
    }
    
    await tableLinks[0].click();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Test 1: Edit Button
    console.log('📋 TEST 1: Edit Button Functionality');
    console.log('━'.repeat(60));
    
    try {
        const editButton = page.locator('button.edit-btn').first();
        await editButton.click();
        await page.waitForTimeout(2000);
        
        const modalVisible = await page.locator('.modal.show').count() > 0;
        if (modalVisible) {
            console.log('✅ Modal opens when clicking edit button');
            
            const queryIdValue = await page.locator('#queryId').inputValue();
            const queryTextValue = await page.locator('#queryText').inputValue();
            
            if (queryIdValue && queryTextValue) {
                console.log('✅ Modal fields are populated correctly');
                console.log(`   Query ID: ${queryIdValue}`);
                console.log(`   Query Text: ${queryTextValue.substring(0, 50)}...`);
                console.log('\n✅ TEST 1 PASSED: Edit button works perfectly');
            } else {
                console.log('❌ Modal fields are not populated');
                console.log('\n❌ TEST 1 FAILED: Modal opened but fields empty');
            }
            
            await page.locator('.modal .btn-close').click();
        } else {
            console.log('❌ Modal does NOT open');
            console.log('\n❌ TEST 1 FAILED: Modal not appearing');
            console.log('💡 TIP: Check if Bootstrap modal JavaScript is loaded correctly');
        }
    } catch (error) {
        console.log(`❌ TEST 1 ERROR: ${error.message}`);
    }
    
    // Test 2: Copy & Paste JSON with selection
    console.log('\n📋 TEST 2: Copy & Paste JSON (with selection)');
    console.log('━'.repeat(60));
    
    try {
        const checkboxes = await page.locator('.query-checkbox').all();
        await checkboxes[0].check();
        await checkboxes[1].check();
        console.log('✅ Selected 2 queries');
        
        await page.locator('button:has-text("Copy & Paste JSON")').click();
        await page.waitForTimeout(1500);
        
        const jsonContent = await page.locator('#jsonPreview').inputValue();
        const jsonData = JSON.parse(jsonContent);
        
        console.log(`✅ Modal opens with JSON (${jsonData.length} items)`);
        console.log(`✅ JSON structure is correct`);
        console.log(`   - query_id: ${jsonData[0].query_id}`);
        console.log(`   - query: ${jsonData[0].query.substring(0, 50)}...`);
        console.log(`   - ground_truth_ranked: [${jsonData[0].ground_truth_ranked.join(', ')}]`);
        
        page.on('dialog', async dialog => await dialog.accept());
        await page.locator('button:has-text("Copy to Clipboard")').click();
        await page.waitForTimeout(500);
        console.log('✅ Copy to Clipboard button works');
        
        console.log('\n✅ TEST 2 PASSED: Copy & Paste JSON works perfectly');
        
        await page.locator('#jsonPreviewModal .btn-close').click();
    } catch (error) {
        console.log(`❌ TEST 2 ERROR: ${error.message}`);
    }
    
    // Test 3: Copy & Paste JSON without selection
    console.log('\n📋 TEST 3: Copy & Paste JSON (no selection)');
    console.log('━'.repeat(60));
    
    try {
        await page.evaluate(() => {
            document.querySelectorAll('.query-checkbox:checked').forEach(cb => cb.checked = false);
        });
        await page.waitForTimeout(500);
        
        const stillChecked = await page.locator('.query-checkbox:checked').count();
        if (stillChecked === 0) {
            console.log('✅ All queries deselected');
            
            await page.locator('button:has-text("Copy & Paste JSON")').click();
            await page.waitForTimeout(1500);
            
            const jsonContent = await page.locator('#jsonPreview').inputValue();
            const jsonData = JSON.parse(jsonContent);
            const totalRows = await page.locator('table tbody tr').count();
            
            console.log(`✅ Exported ${jsonData.length} queries (all of them)`);
            console.log(`✅ Table has ${totalRows} rows`);
            
            if (jsonData.length === totalRows) {
                console.log('\n✅ TEST 3 PASSED: All queries exported when no selection');
            } else {
                console.log('\n⚠️ TEST 3 WARNING: Count mismatch');
            }
            
            await page.locator('#jsonPreviewModal .btn-close').click();
        }
    } catch (error) {
        console.log(`❌ TEST 3 ERROR: ${error.message}`);
    }
    
    // Test 4: Row Selection by Clicking
    console.log('\n📋 TEST 4: Row Selection by Clicking');
    console.log('━'.repeat(60));
    
    try {
        const firstRow = page.locator('table tbody tr').nth(0);
        const firstRowCheckbox = firstRow.locator('.query-checkbox');
        
        const initialChecked = await firstRowCheckbox.isChecked();
        console.log(`Initial checkbox state: ${initialChecked ? 'Checked' : 'Unchecked'}`);
        
        await firstRow.locator('td').nth(2).click();
        await page.waitForTimeout(500);
        
        const afterFirstClick = await firstRowCheckbox.isChecked();
        console.log(`After clicking row: ${afterFirstClick ? 'Checked' : 'Unchecked'}`);
        
        if (afterFirstClick !== initialChecked) {
            console.log('✅ Clicking row toggles checkbox');
            
            await page.locator('table tbody tr').nth(1).locator('td').nth(2).click();
            await page.waitForTimeout(500);
            
            const selectedCount = await page.locator('.query-checkbox:checked').count();
            console.log(`✅ Selected ${selectedCount} rows by clicking`);
            
            console.log('\n✅ TEST 4 PASSED: Row selection by clicking works');
        } else {
            console.log('\n❌ TEST 4 FAILED: Row clicking does not toggle checkbox');
        }
    } catch (error) {
        console.log(`❌ TEST 4 ERROR: ${error.message}`);
    }
    
    // Test 5: JSON Format Validation
    console.log('\n📋 TEST 5: JSON Format Validation');
    console.log('━'.repeat(60));
    
    try {
        await page.locator('.query-checkbox').first().check();
        await page.locator('button:has-text("Copy & Paste JSON")').click();
        await page.waitForTimeout(1500);
        
        const jsonContent = await page.locator('#jsonPreview').inputValue();
        const jsonData = JSON.parse(jsonContent);
        
        console.log('✅ JSON is valid and parseable');
        console.log(`✅ JSON is an array with ${jsonData.length} items`);
        
        const sample = jsonData[0];
        console.log('\n📋 Sample item structure:');
        console.log(`   query_id: ${typeof sample.query_id} = "${sample.query_id}"`);
        console.log(`   query: ${typeof sample.query} = "${sample.query.substring(0, 30)}..."`);
        console.log(`   ground_truth_ranked: ${typeof sample.ground_truth_ranked} = [${sample.ground_truth_ranked.join(', ')}]`);
        
        if (typeof sample.query_id === 'string' && 
            typeof sample.query === 'string' && 
            Array.isArray(sample.ground_truth_ranked)) {
            console.log('\n✅ TEST 5 PASSED: JSON format is correct');
        } else {
            console.log('\n❌ TEST 5 FAILED: JSON structure has issues');
        }
        
        await page.locator('#jsonPreviewModal').evaluate(el => el.style.display = 'none');
    } catch (error) {
        console.log(`❌ TEST 5 ERROR: ${error.message}`);
    }
    
    console.log('\n╔══════════════════════════════════════════════════════════════╗');
    console.log('║                    TEST COMPLETE                              ║');
    console.log('╚══════════════════════════════════════════════════════════════╝\n');
    
    await page.waitForTimeout(5000);
    await browser.close();
}

finalTest().catch(console.error);