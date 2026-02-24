const { chromium } = require('playwright');
const fs = require('fs');
const RSS = require('rss');

(async () => {

    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    console.log("访问 IMF 英文博客列表...");

    await page.goto('https://www.imf.org/en/blogs', {
        waitUntil: 'domcontentloaded',
        timeout: 60000
    });

    await page.waitForTimeout(2000);

    const links = await page.$$eval(
    'a[href*="/en/blogs/articles/"]',
    as => [...new Set(as.map(a => a.href))].slice(0, 10)
);

    console.log(`找到 ${links.length} 篇文章`);

    const feed = new RSS({
        title: 'IMF English Blogs',
        description: 'Latest IMF English blog articles',
        feed_url: 'https://cfoandy.github.io/imf-rss/imf.xml',
        site_url: 'https://www.imf.org/en/blogs',
        language: 'en'
    });

    for (const link of links) {
        try {

            console.log(`抓取文章: ${link}`);

            await page.goto(link, {
                waitUntil: 'domcontentloaded',
                timeout: 60000
            });

            await page.waitForTimeout(2000);

            const title = await page.$eval('h1', el => el.innerText.trim());

            const content = await page.$eval(
                '.article-body, main',
                el => el.innerHTML
            );

            const pubDate = await page.$eval(
                'time',
                el => el.getAttribute('datetime')
            ).catch(() => new Date().toISOString());

            feed.item({
                title,
                url: link,
                date: pubDate,
                description: content,
                custom_elements: [
                    { 'content:encoded': { _cdata: content } }
                ]
            });

        } catch (err) {
            console.log("跳过异常文章");
        }
    }

    fs.writeFileSync('imf.xml', feed.xml({ indent: true }));

    console.log("RSS 已生成");

    await browser.close();

})();