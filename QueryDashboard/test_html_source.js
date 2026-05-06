const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
    console.log('🔍 Inspecting HTML source...');
    
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        await page.goto('http://127.0.0.1:5000/table/1', { waitUntil: 'networkidle' });
        await page.waitForTimeout(2000);
        
        // Get the HTML content of the table body
        const tableHTML = await page.$eval('tbody', el => el.innerHTML);
        
        console.log('📋 Table HTML (first 2000 chars):');
        console.log(tableHTML.substring(0, 2000));
        
        // Find the first edit button HTML
        const editButtonHTML = await page.$eval('.edit-btn', el => el.outerHTML);
        
        console.log('\n📋 First edit button HTML:');
        console.log(editButtonHTML);
        
        // Save to file for inspection
        fs.writeFileSync('debug_table_html.html', tableHTML);
        fs.writeFileSync('debug_button_html.html', editButtonHTML);
        
        console.log('\n✅ HTML saved to debug_table_html.html and debug_button_html.html');
        
    } catch (error) {
        console.log(`💥 Error: ${error.message}`);
    } finally {
        await browser.close();
    }
})();
