// 测试多图片生成功能
console.log("测试多图片生成功能...");

// 模拟API响应
const mockResponse = {
    data: [
        { url: "https://example.com/image1.jpg" },
        { url: "https://example.com/image2.jpg" },
        { url: "https://example.com/image3.jpg" }
    ]
};

// 测试提取图片函数
function extractImagesFromResponse(response) {
    // 常见结构: { data: [ { url }, { url } ] }
    if (Array.isArray(response?.data)) {
        const arr = response.data;
        // 如果是字符串数组，转成对象数组
        if (arr.length > 0 && typeof arr[0] === 'string') {
            return arr.map((u) => ({ url: u }));
        }
        // 如果是对象数组，且对象内含 images，再展开
        if (arr.length > 0 && arr[0] && Array.isArray(arr[0].images)) {
            return arr.flatMap((item) => {
                return item.images.map((img) => (typeof img === 'string' ? { url: img } : img));
            });
        }
        return arr;
    }

    // 其他可能: { images: [...] }
    if (Array.isArray(response?.images)) {
        return response.images.map((img) => (typeof img === 'string' ? { url: img } : img));
    }

    // 其他可能: { data: { images: [...] } }
    if (response?.data && Array.isArray(response.data.images)) {
        return response.data.images.map((img) => (typeof img === 'string' ? { url: img } : img));
    }

    // 兜底: 如果存在单一 url 或 b64_json
    if (response?.url || response?.b64_json) {
        return [response];
    }

    return [];
}

// 测试函数
const images = extractImagesFromResponse(mockResponse);
console.log(`提取到 ${images.length} 张图片:`);
images.forEach((img, index) => {
    console.log(`图片 ${index + 1}: ${img.url}`);
});

// 测试并发请求模拟
async function simulateConcurrentRequests() {
    console.log("\n模拟并发请求...");
    
    const mockRequests = [
        Promise.resolve({ data: [{ url: "https://example.com/img1.jpg" }] }),
        Promise.resolve({ data: [{ url: "https://example.com/img2.jpg" }] }),
        Promise.resolve({ data: [{ url: "https://example.com/img3.jpg" }] })
    ];
    
    try {
        const responses = await Promise.all(mockRequests);
        console.log(`收到 ${responses.length} 个响应`);
        
        let allImages = [];
        responses.forEach((response, index) => {
            const extracted = extractImagesFromResponse(response);
            console.log(`响应 ${index + 1}: ${extracted.length} 张图片`);
            allImages = allImages.concat(extracted);
        });
        
        console.log(`总共解析到 ${allImages.length} 张图片`);
    } catch (error) {
        console.error('并发请求失败:', error);
    }
}

// 运行测试
simulateConcurrentRequests();