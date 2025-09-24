// 测试实时显示功能
console.log("测试实时图片显示功能...");

// 模拟实时API响应
async function simulateRealtimeResponse() {
    console.log("\n模拟实时响应处理...");
    
    // 模拟5个不同的响应时间
    const mockResponses = [
        { delay: 1000, data: [{ url: "https://example.com/img1.jpg" }] },
        { delay: 2000, data: [{ url: "https://example.com/img2.jpg" }] },
        { delay: 1500, data: [{ url: "https://example.com/img3.jpg" }] },
        { delay: 3000, data: [{ url: "https://example.com/img4.jpg" }] },
        { delay: 1000, data: [{ url: "https://example.com/img5.jpg" }] }
    ];
    
    let completed = 0;
    const total = mockResponses.length;
    
    console.log(`开始处理 ${total} 个响应...`);
    
    // 创建所有请求的Promise
    const requests = mockResponses.map((response, index) => 
        new Promise(resolve => {
            setTimeout(() => {
                completed++;
                console.log(`✅ 响应 ${index + 1} 完成 (${completed}/${total})`);
                console.log(`   图片 ${index + 1}: ${response.data[0].url}`);
                
                // 模拟实时显示
                simulateDisplayImage(response.data, index + 1, completed, total);
                
                resolve({ response: response.data, index });
            }, response.delay);
        })
    );
    
    try {
        await Promise.all(requests);
        console.log(`✅ 所有请求完成，共 ${completed} 个响应`);
    } catch (error) {
        console.error('处理请求时发生错误:', error);
    }
}

// 模拟实时显示图片
function simulateDisplayImage(images, responseIndex, completedCount, totalCount) {
    console.log(`📊 实时显示: 响应 ${responseIndex} -> 图片 ${completedCount}/${totalCount}`);
    images.forEach((img, imgIndex) => {
        console.log(`   🖼️  显示图片 ${imgIndex + 1}: ${img.url}`);
    });
}

// 运行测试
simulateRealtimeResponse();

// 测试修改后的displayImagesSequentially函数
function testDisplayImagesSequentially() {
    console.log("\n测试displayImagesSequentially函数...");
    
    const mockImages = [
        { url: "https://example.com/test1.jpg" },
        { url: "https://example.com/test2.jpg" },
        { url: "https://example.com/test3.jpg" }
    ];
    
    // 模拟参数
    const mockProgressContainer = {
        querySelector: () => ({
            textContent: '',
            style: { width: '0%' }
        })
    };
    
    const mockResultGrid = {
        appendChild: () => {}
    };
    
    // 测试函数
    displayImagesSequentially(mockImages, 3, mockProgressContainer, mockResultGrid, 0)
        .then(() => {
            console.log("✅ displayImagesSequentially 测试完成");
        })
        .catch(error => {
            console.error("❌ displayImagesSequentially 测试失败:", error);
        });
}

// 从script.js中复制displayImagesSequentially函数用于测试
async function displayImagesSequentially(images, targetCount, progressContainer, resultGrid, startIndex = 0) {
    let completed = startIndex;
    const total = Math.min(images.length, targetCount) + startIndex;
    
    console.log(`开始显示图片: ${startIndex} -> ${total} (共 ${images.length} 张图片)`);
    
    for (let i = 0; i < images.length; i++) {
        try {
            // 模拟实时显示效果（每张图片显示间隔0.5秒）
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // 更新进度
            completed++;
            console.log(`更新进度: ${completed}/${total}`);
            
            // 显示当前图片
            console.log(`显示图片 ${completed}: ${images[i].url}`);
            
        } catch (error) {
            console.error(`显示第 ${completed + 1} 张图片失败:`, error);
        }
    }
    
    console.log(`图片显示完成: ${completed}/${total} 张图片成功显示`);
    return completed;
}