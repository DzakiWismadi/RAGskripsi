const { chromium } = require('playwright');

async function testManual() {
    console.log('🔍 Manual Testing...\n');
    
    const browser = await chromium.launch({ 
        headless: false,
        slowMo: 2000 
    });
    
    const page = await browser.newPage();
    await page.goto('http://127.0.0.1:5000');
    await page.waitForLoadState('networkidle');
    
    // Navigate to first table
    const tableLink = page.locator('a[href*="/table/"]').first();
    await tableLink.click();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    console.log('✅ Page loaded. Now testing manually...');
    console.log('📋 Testing Copy & Paste JSON feature:');
    
    // Select first query
    await page.locator('.query-checkbox').first().check();
    console.log('✅ Selected first query');
    
    // Click Copy & Paste JSON
    await page.locator('button:has-text("Copy & Paste JSON")').click();
    await page.waitForTimeout(2000);
    
    // Check if modal appeared
    const modalVisible = await page.locator('#jsonPreviewModal').isVisible();
    console.log(`Modal visible: ${modalVisible}`);
    
    if (modalVisible) {
        const jsonText = await page.locator('#jsonPreview').inputValue();
        console.log('JSON content length:', jsonText.length);
        
        // Click copy button
        await page.locator('button:has-text("Copy to Clipboard")').click();
        await page.waitForTimeout(2000);
        
        // Close modal
        await page.locator('#jsonPreviewModal .btn-close').click();
        await page.waitForTimeout(1000);
    }
    
    console.log('\n📋 Testing row selection by clicking:');
    
    // Click on a row
    await page.locator('table tbody tr:nth-child(2) td:nth-child(3)').click();
    await page.waitForTimeout(500);
    
    const selectedCount = await page.locator('.query-checkbox:checked').count();
    console.log(`Selected rows: ${selectedCount}`);
    
    console.log('\n✅ Testing complete. Browser will stay open for 30 seconds...');
    await page.waitForTimeout(30000);
    await browser.close();
}

testManual().catch(console.error);