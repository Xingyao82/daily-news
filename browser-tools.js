const { chromium } = require('playwright');

/**
 * 智能网页搜索工具 - 使用无头浏览器
 * 可以抓取任何网页，包括需要JavaScript渲染的内容
 */

async function searchFlights(from, to, options = {}) {
    console.log(`🔍 搜索航班: ${from} → ${to}`);
    
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    });
    const page = await context.newPage();
    
    try {
        // 使用 Google Flights 搜索
        const searchUrl = `https://www.google.com/travel/flights?q=Flights%20from%20${encodeURIComponent(from)}%20to%20${encodeURIComponent(to)}`;
        console.log(`🌐 访问: ${searchUrl}`);
        
        await page.goto(searchUrl, { waitUntil: 'networkidle', timeout: 30000 });
        
        // 等待页面加载
        await page.waitForTimeout(5000);
        
        // 截图保存
        await page.screenshot({ path: `/tmp/flight-search-${Date.now()}.png`, fullPage: true });
        
        // 尝试提取价格信息
        const prices = await page.locator('[class*="price"], [class*=" Price"]').first().textContent().catch(() => '未找到价格');
        
        console.log(`💰 价格信息: ${prices}`);
        
        // 获取页面标题和主要内容
        const title = await page.title();
        const content = await page.locator('body').textContent();
        
        await browser.close();
        
        return {
            success: true,
            title,
            prices,
            screenshot: `/tmp/flight-search-${Date.now()}.png`,
            content: content.substring(0, 2000)
        };
        
    } catch (error) {
        await browser.close();
        return {
            success: false,
            error: error.message
        };
    }
}

async function scrapeWebPage(url, options = {}) {
    console.log(`🌐 抓取网页: ${url}`);
    
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    });
    const page = await context.newPage();
    
    try {
        await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForTimeout(3000);
        
        // 截图
        const screenshotPath = `/tmp/web-screenshot-${Date.now()}.png`;
        await page.screenshot({ path: screenshotPath, fullPage: options.fullPage });
        
        // 提取内容
        const title = await page.title();
        const text = await page.locator('body').textContent();
        const links = await page.locator('a[href]').evaluateAll(links => 
            links.map(a => ({ text: a.textContent.trim(), href: a.href })).slice(0, 20)
        );
        
        await browser.close();
        
        return {
            success: true,
            title,
            text: text.substring(0, 5000),
            links,
            screenshot: screenshotPath
        };
        
    } catch (error) {
        await browser.close();
        return {
            success: false,
            error: error.message
        };
    }
}

// 命令行调用
const command = process.argv[2];
const arg1 = process.argv[3];
const arg2 = process.argv[4];

(async () => {
    switch (command) {
        case 'flight':
            const result = await searchFlights(arg1, arg2);
            console.log(JSON.stringify(result, null, 2));
            break;
            
        case 'scrape':
            const data = await scrapeWebPage(arg1);
            console.log(JSON.stringify(data, null, 2));
            break;
            
        default:
            console.log(`
使用方法:
  node browser-tools.js flight "北京" "洛杉矶"     - 搜索航班
  node browser-tools.js scrape "https://..."       - 抓取网页
            `);
    }
})();
