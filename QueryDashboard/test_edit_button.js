const { chromium } = require('playwright');

async function testEditButton() {
    console.log('🔍 Testing Edit Button Functionality...\n');
    
    const browser = await chromium.launch({ 
        headless: false,
        slowMo: 1000 
    });
    
    const page = await browser.newPage();
    await page.goto('http://127.0.0.1:5000');
    await page.waitForLoadState('networkidle');
    
    // Navigate to first table
    const tableLink = page.locator('a[href*="/table/"]').first();
    await tableLink.click();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check if edit button exists and get its attributes
    const editButton = page.locator('button.edit-btn').first();
    
    console.log('📋 Edit Button Attributes:');
    console.log('   Visible:', await editButton.isVisible());
    console.log('   Enabled:', await editButton.isEnabled());
    console.log('   Text:', await editButton.textContent());
    console.log('   Data ID:', await editButton.getAttribute('data-id'));
    console.log('   Data Query ID:', await editButton.getAttribute('data-query-id'));
    
    // Check if click listener is attached
    console.log('\n🖱️  Clicking Edit button...');
    await editButton.click();
    
    // Wait a moment and check for modal
    await page.waitForTimeout(2000);
    
    // Check all possible modal selectors
    console.log('\n🔍 Checking for modal:');
    console.log('   .modal.show:', await page.locator('.modal.show').count() > 0);
    console.log('   #addQueryModal.show:', await page.locator('#addQueryModal.show').count() > 0);
    console.log('   .modal (visible):', await page.locator('.modal').filter({ hasText: 'Edit Query' }).count() > 0);
    
    // Try to find any modal
    const modals = await page.locator('.modal').all();
    console.log(`\n   Total modals found: ${modals.length}`);
    
    // Check if any modal is visible
    for (let i = 0; i < modals.length; i++) {
        const isVisible = await modals[i].isVisible();
        console.log(`   Modal ${i + 1} visible: ${isVisible}`);
        
        if (isVisible) {
            const text = await modals[i].textContent();
            console.log(`   Modal ${i + 1} text: ${text.substring(0, 100)}...`);
        }
    }
    
    // Check modal by title
    const editQueryModal = page.locator('.modal').filter({ hasText: 'Edit Query' });
    console.log('\n🔍 Edit Query Modal:');
    console.log('   Found:', await editQueryModal.count() > 0);
    console.log('   Visible:', await editQueryModal.isVisible());
    
    await page.waitForTimeout(5000);
    await browser.close();
}

testEditButton().catch(console.error);