// API配置
const API_CONFIG = {
    // 使用本地代理服务器避免CORS问题
    baseUrl: 'http://localhost:8001/api/images/generations',
    // API密钥由代理服务器处理，前端不需要发送
    apiKey: null
};

// DOM元素
const elements = {
    prompt: document.getElementById('prompt'),
    referenceImage: document.getElementById('referenceImage'),
    fileUploadArea: document.getElementById('fileUploadArea'),
    previewContainer: document.getElementById('previewContainer'),
    toggleAdvanced: document.getElementById('toggleAdvanced'),
    advancedPanel: document.getElementById('advancedPanel'),
    model: document.getElementById('model'),
    size: document.getElementById('size'),
    numImages: document.getElementById('numImages'),
    guidanceScale: document.getElementById('guidanceScale'),
    guidanceValue: document.getElementById('guidanceValue'),
    steps: document.getElementById('steps'),
    stepsValue: document.getElementById('stepsValue'),
    strength: document.getElementById('strength'),
    strengthValue: document.getElementById('strengthValue'),
    generateBtn: document.getElementById('generateBtn'),
    resultSection: document.getElementById('resultSection'),
    loadingIndicator: document.getElementById('loadingIndicator'),
    resultContent: document.getElementById('resultContent'),
    errorMessage: document.getElementById('errorMessage')
};

// 全局变量
let uploadedImages = [];

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    updateSliderValues();
});

// 事件监听器初始化
function initializeEventListeners() {
    // 高级设置切换
    elements.toggleAdvanced.addEventListener('click', toggleAdvancedSettings);
    
    // 滑块值更新
    elements.guidanceScale.addEventListener('input', updateSliderValues);
    elements.steps.addEventListener('input', updateSliderValues);
    elements.strength.addEventListener('input', updateSliderValues);
    
    // 文件上传
    elements.referenceImage.addEventListener('change', handleFileSelect);
    elements.fileUploadArea.addEventListener('dragover', handleDragOver);
    elements.fileUploadArea.addEventListener('drop', handleFileDrop);
    elements.fileUploadArea.addEventListener('dragleave', handleDragLeave);
    
    // 生成按钮
    elements.generateBtn.addEventListener('click', generateImage);
}

// 切换高级设置
function toggleAdvancedSettings() {
    const panel = elements.advancedPanel;
    const button = elements.toggleAdvanced;
    
    if (panel.classList.contains('open')) {
        panel.classList.remove('open');
        button.classList.remove('active');
    } else {
        panel.classList.add('open');
        button.classList.add('active');
    }
}

// 更新滑块显示值
function updateSliderValues() {
    elements.guidanceValue.textContent = elements.guidanceScale.value;
    elements.stepsValue.textContent = elements.steps.value;
    elements.strengthValue.textContent = elements.strength.value;
}

// 处理文件选择
function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    processFiles(files);
}

// 处理拖拽
function handleDragOver(event) {
    event.preventDefault();
    elements.fileUploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    elements.fileUploadArea.classList.remove('dragover');
}

function handleFileDrop(event) {
    event.preventDefault();
    elements.fileUploadArea.classList.remove('dragover');
    
    const files = Array.from(event.dataTransfer.files);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length > 0) {
        processFiles(imageFiles);
    }
}

// 处理文件
function processFiles(files) {
    files.forEach(file => {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const imageData = e.target.result;
                uploadedImages.push(imageData);
                addImagePreview(imageData, uploadedImages.length - 1);
            };
            reader.readAsDataURL(file);
        }
    });
}

// 添加图片预览
function addImagePreview(imageSrc, index) {
    const previewItem = document.createElement('div');
    previewItem.className = 'preview-item';
    previewItem.innerHTML = `
        <img src="${imageSrc}" alt="预览图片">
        <button class="remove-btn" onclick="removeImage(${index})">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    elements.previewContainer.appendChild(previewItem);
}

// 移除图片
function removeImage(index) {
    uploadedImages.splice(index, 1);
    updateImagePreviews();
}

// 更新图片预览
function updateImagePreviews() {
    elements.previewContainer.innerHTML = '';
    uploadedImages.forEach((imageSrc, index) => {
        addImagePreview(imageSrc, index);
    });
}

// 生成图像
async function generateImage() {
    const prompt = elements.prompt.value.trim();

    if (!prompt) {
        showError('请输入图像描述');
        elements.prompt.focus();
        return;
    }

    if (prompt.length < 5) {
        showError('图像描述太短，请提供更详细的描述（至少5个字符）');
        elements.prompt.focus();
        return;
    }
    
    // 禁用按钮并显示加载状态
    elements.generateBtn.disabled = true;
    setFormDisabled(true);
    showLoading();
    hideError();
    hideResult();
    
    try {
        const requestData = buildRequestData(prompt);
        const response = await callImageGenerationAPI(requestData);
        
        if (response.data && response.data.length > 0) {
            displayResults(response.data, response);
        } else {
            throw new Error('API返回的数据格式不正确');
        }
        
    } catch (error) {
        console.error('生成图像失败:', error);
        showError(error.message || '生成图像时发生错误，请稍后重试');
    } finally {
        elements.generateBtn.disabled = false;
        setFormDisabled(false);
        hideLoading();
    }
}

// 构建请求数据
function buildRequestData(prompt) {
    const data = {
        model: elements.model.value,
        prompt: prompt,
        n: parseInt(elements.numImages.value),
        size: elements.size.value,
        response_format: 'url',
        guidance_scale: parseFloat(elements.guidanceScale.value),
        num_inference_steps: parseInt(elements.steps.value),
        strength: parseFloat(elements.strength.value)
    };

    // 检查上传的图片
    console.log('='.repeat(60));
    console.log('📤 构建API请求数据:');
    console.log(`模型: ${data.model}`);
    console.log(`提示词: ${data.prompt.substring(0, 50)}...`);
    console.log(`图片数量: ${data.n}`);
    console.log(`尺寸: ${data.size}`);
    console.log(`上传的图片数组长度: ${uploadedImages.length}`);

    // 添加图片数据
    if (uploadedImages.length === 1) {
        data.imageDataUrl = uploadedImages[0];
        console.log('🖼️  添加单张图片数据:');
        console.log(`   imageDataUrl: ${uploadedImages[0].length} 字符`);
        console.log(`   图片格式: ${uploadedImages[0].substring(0, 30)}...`);
    } else if (uploadedImages.length > 1) {
        data.imageDataUrls = uploadedImages;
        console.log('🖼️  添加多张图片数据:');
        console.log(`   imageDataUrls: ${uploadedImages.length} 张图片`);
        uploadedImages.forEach((img, i) => {
            console.log(`   图片${i+1}: ${img.length} 字符`);
        });
    } else {
        console.log('❌ 未上传图片');
    }

    console.log('='.repeat(60));

    return data;
}

// 调用API
async function callImageGenerationAPI(requestData) {
    const headers = {
        'Content-Type': 'application/json'
    };

    // 如果有API密钥，添加到请求头（用于直接调用API的情况）
    if (API_CONFIG.apiKey) {
        headers['Authorization'] = `Bearer ${API_CONFIG.apiKey}`;
    }

    const response = await fetch(API_CONFIG.baseUrl, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(requestData)
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP错误: ${response.status}`);
    }

    return await response.json();
}

// 显示结果
function displayResults(images, responseData) {
    const resultGrid = document.createElement('div');
    resultGrid.className = 'result-grid';
    
    images.forEach((image, index) => {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        
        const imageUrl = image.url || `data:image/png;base64,${image.b64_json}`;
        
        resultItem.innerHTML = `
            <img src="${imageUrl}" alt="生成的图像 ${index + 1}" loading="lazy">
            <button class="download-btn" onclick="downloadImage('${imageUrl}', '生成图像_${index + 1}')">
                <i class="fas fa-download"></i> 下载
            </button>
        `;
        
        resultGrid.appendChild(resultItem);
    });
    
    // 添加API信息
    if (responseData.cost !== undefined) {
        const infoDiv = document.createElement('div');
        infoDiv.className = 'api-info';
        infoDiv.innerHTML = `
            <p><strong>消耗费用:</strong> ${responseData.cost}</p>
            <p><strong>剩余余额:</strong> ${responseData.remainingBalance}</p>
        `;
        resultGrid.appendChild(infoDiv);
    }
    
    elements.resultContent.innerHTML = '';
    elements.resultContent.appendChild(resultGrid);
    showResult();
}

// 下载图片
function downloadImage(imageUrl, filename) {
    try {
        // 如果是base64数据，直接下载
        if (imageUrl.startsWith('data:')) {
            const link = document.createElement('a');
            link.href = imageUrl;
            link.download = `${filename}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            // 如果是URL，需要先获取图片数据
            fetch(imageUrl)
                .then(response => response.blob())
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = `${filename}.png`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    window.URL.revokeObjectURL(url);
                })
                .catch(error => {
                    console.error('下载失败:', error);
                    // 如果跨域下载失败，尝试在新窗口打开
                    window.open(imageUrl, '_blank');
                });
        }
    } catch (error) {
        console.error('下载失败:', error);
        // 如果下载失败，尝试在新窗口打开
        window.open(imageUrl, '_blank');
    }
}

// 显示/隐藏状态函数
function showLoading() {
    elements.loadingIndicator.classList.add('show');
}

function hideLoading() {
    elements.loadingIndicator.classList.remove('show');
}

function showResult() {
    elements.resultContent.classList.add('show');
}

function hideResult() {
    elements.resultContent.classList.remove('show');
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorMessage.classList.add('show');
}

function hideError() {
    elements.errorMessage.classList.remove('show');
}

// 设置表单禁用状态
function setFormDisabled(disabled) {
    elements.prompt.disabled = disabled;
    elements.referenceImage.disabled = disabled;
    elements.model.disabled = disabled;
    elements.size.disabled = disabled;
    elements.numImages.disabled = disabled;
    elements.guidanceScale.disabled = disabled;
    elements.steps.disabled = disabled;
    elements.strength.disabled = disabled;
    elements.toggleAdvanced.disabled = disabled;
}

// 设置提示示例
function setPromptExample(element) {
    elements.prompt.value = element.textContent;
    elements.prompt.focus();
}
