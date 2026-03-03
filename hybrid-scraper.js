const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

/**
 * 智能混合抓取工具
 * 策略：优先浏览器 → 失败再API → 缓存防重复
 * API限额管理：Brave Search 1次/分钟
 */

const CONFIG = {
    api: {
        brave: {
            enabled: true,
            rateLimit: 60000, // 1分钟
            lastCall: 0,
            dailyQuota: 2000,
            usedToday: 0
        }
    },
    browser: {
        headless: true,
        timeout: 30000,
        retries: 2
    },
    cache: {
        enabled: true,
        ttl: 3600000, // 1小时
        dir: '/tmp/web-cache'
    }
};

// 确保缓存目录存在
if (!fs.existsSync(CONFIG.cache.dir)) {
    fs.mkdirSync(CONFIG.cache.dir, { recursive: true });
}

/**
 * API限额管理
 */
class RateLimiter {
    static async checkBraveQuota() {
        const now = Date.now();
        const timeSinceLastCall = now - CONFIG.api.brave.lastCall;
        
        // 检查频率限制
        if (timeSinceLastCall < CONFIG.api.brave.rateLimit) {
            const waitTime = CONFIG.api.brave.rateLimit - timeSinceLastCall;
            console.log(`⏳ API限额：需等待 ${Math.ceil(waitTime/1000)} 秒`);
            return { allowed: false, waitTime };
        }
        
        // 检查日配额
        if (CONFIG.api.brave.usedToday >= CONFIG.api.brave.dailyQuota) {
            console.log('❌ API日配额已用完');
            return { allowed: false, quotaExceeded: true };
        }
        
        return { allowed: true };
    }
    
    static async useBrave() {
        CONFIG.api.brave.lastCall = Date.now();
        CONFIG.api.brave.usedToday++;
        console.log(`📊 API使用：${CONFIG.api.brave.usedToday}/${CONFIG.api.brave.dailyQuota}`);
    }
    
    static getStatus() {
        return {
            brave: {
                used: CONFIG.api.brave.usedToday,
                quota: CONFIG.api.brave.dailyQuota,
                remaining: CONFIG.api.brave.dailyQuota - CONFIG.api.brave.usedToday,
                lastCall: new Date(CONFIG.api.brave.lastCall).toLocaleString()
            }
        };
    }
}

/**
 * 缓存管理
 */
class Cache {
    static getCacheKey(url) {
        return url.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 100);
    }
    
    static getCachePath(url) {
        return path.join(CONFIG.cache.dir, `${this.getCacheKey(url)}.json`);
    }
    
    static get(url) {
        if (!CONFIG.cache.enabled) return null;
        
        const cachePath = this.getCachePath(url);
        if (!fs.existsSync(cachePath)) return null;
        
        try {
            const data = JSON.parse(fs.readFileSync(cachePath, 'utf8'));
            const age = Date.now() - data.timestamp;
            
            if (age > CONFIG.cache.ttl) {
                console.log('🗑️ 缓存已过期');
                fs.unlinkSync(cachePath);
                return null;
            }
            
            console.log('✅ 命中缓存');
            return data.content;
        } catch (e) {
            return null;
        }
    }
    
    static set(url, content) {
        if (!CONFIG.cache.enabled) return;
        
        const cachePath = this.getCachePath(url);
        fs.writeFileSync(cachePath, JSON.stringify({
            url,
            timestamp: Date.now(),
            content
        }));
    }
}

/**
 * 浏览器抓取（优先）
 */
async function scrapeWithBrowser(url, options = {}) {
    console.log(`🌐 浏览器抓取: ${url.substring(0, 60)}...`);
    
    const browser = await chromium.launch({ 
        headless: CONFIG.browser.headless 
    });
    
    try {
        const context = await browser.newContext({
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        });
        
        const page = await context.newPage();
        
        // 设置超时
        await page.goto(url, { 
            waitUntil: 'networkidle', 
            timeout: CONFIG.browser.timeout 
        });
        
        // 额外等待动态内容
        await page.waitForTimeout(options.waitFor || 3000);
        
        // 提取内容
        const result = {
            success: true,
            method: 'browser',
            title: await page.title(),
            text: await page.locator('body').textContent(),
            links: await page.locator('a[href]').evaluateAll(links => 
                links.slice(0, 20).map(a => ({ 
                    text: a.textContent?.trim().substring(0, 50), 
                    href: a.href 
                }))
            ),
            timestamp: new Date().toISOString()
        };
        
        await browser.close();
        return result;
        
    } catch (error) {
        await browser.close();
        return {
            success: false,
            method: 'browser',
            error: error.message
        };
    }
}

/**
 * API抓取（后备）
 */
async function scrapeWithAPI(query) {
    const quotaCheck = await RateLimiter.checkBraveQuota();
    
    if (!quotaCheck.allowed) {
        return {
            success: false,
            method: 'api',
            error: quotaCheck.quotaExceeded 
                ? 'API日配额已用完' 
                : `API频率限制，需等待${Math.ceil(quotaCheck.waitTime/1000)}秒`
        };
    }
    
    console.log(`🔍 API搜索: ${query}`);
    
    // 这里模拟API调用（实际需接入Brave Search）
    // 为演示，返回一个占位结果
    await RateLimiter.useBrave();
    
    return {
        success: true,
        method: 'api',
        query,
        results: [], // 实际接入API后填充
        note: 'API结果（实际需接入Brave Search API）',
        timestamp: new Date().toISOString()
    };
}

/**
 * 智能抓取主函数
 * 策略：缓存 → 浏览器 → API
 */
async function smartScrape(target, options = {}) {
    console.log('🚀 开始智能抓取...');
    console.log('');
    
    const url = target.startsWith('http') ? target : `https://${target}`;
    
    // 1. 检查缓存
    const cached = Cache.get(url);
    if (cached && !options.noCache) {
        return { ...cached, fromCache: true };
    }
    
    // 2. 尝试浏览器抓取（优先）
    let result = await scrapeWithBrowser(url, options);
    
    // 3. 浏览器失败，再试API（如果是搜索类请求）
    if (!result.success && options.fallbackToAPI) {
        console.log('⚠️ 浏览器失败，尝试API后备...');
        result = await scrapeWithAPI(target);
    }
    
    // 4. 缓存成功结果
    if (result.success) {
        Cache.set(url, result);
    }
    
    return result;
}

/**
 * 显示API限额状态
 */
function showQuotaStatus() {
    const status = RateLimiter.getStatus();
    console.log('');
    console.log('📊 API限额状态');
    console.log('==============');
    console.log(`Brave Search: ${status.brave.used}/${status.brave.quota} (剩余 ${status.brave.remaining})`);
    console.log(`上次调用: ${status.brave.lastCall}`);
    console.log('');
}

// 命令行接口
const command = process.argv[2];
const target = process.argv[3];

(async () => {
    switch (command) {
        case 'scrape':
            if (!target) {
                console.log('用法: node hybrid-scraper.js scrape <URL>');
                process.exit(1);
            }
            const result = await smartScrape(target, { fallbackToAPI: true });
            console.log(JSON.stringify(result, null, 2));
            break;
            
        case 'quota':
            showQuotaStatus();
            break;
            
        default:
            console.log(`
智能混合抓取工具 (API限额管理版)

用法:
  node hybrid-scraper.js scrape <URL>     - 智能抓取网页
  node hybrid-scraper.js quota            - 查看API限额状态

策略:
  1. 优先检查缓存
  2. 使用浏览器抓取（无限制）
  3. 浏览器失败则回退到API（有频率限制）
  4. 缓存成功结果

API限额:
  - Brave Search: 1次/分钟, 日配额2000次
            `);
    }
})();

module.exports = { smartScrape, RateLimiter, Cache };
