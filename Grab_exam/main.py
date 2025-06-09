import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd

class YamolScraper:
    def __init__(self, headless=True):
        """
        初始化爬蟲
        Args:
            headless (bool): 是否使用無頭模式運行瀏覽器
        """
        self.driver = None
        self.headless = headless
        self.setup_driver()
    
    def setup_driver(self):
        """設置Chrome瀏覽器驅動"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # 反檢測設置
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # 更真實的User-Agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # 執行反檢測腳本
            self.driver.execute_script("""
                // 隱藏webdriver標識
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // 重寫console方法以避免檢測
                const originalLog = console.log;
                console.log = function() {};
                console.clear = function() {};
                console.debug = function() {};
                
                // 禁用debugger檢測
                const originalEval = window.eval;
                window.eval = function(str) {
                    if (str.includes('debugger')) {
                        return;
                    }
                    return originalEval.call(this, str);
                };
                
                // 阻止DevTools檢測
                setInterval(function() {
                    const devtools = {open: false, orientation: null};
                    const threshold = 160;
                    if (window.outerWidth - window.innerWidth > threshold || 
                        window.outerHeight - window.innerHeight > threshold) {
                        devtools.open = true;
                        devtools.orientation = window.outerWidth - window.innerWidth > threshold ? 'vertical' : 'horizontal';
                    }
                }, 500);
            """)
            
            self.driver.implicitly_wait(10)
            
        except Exception as e:
            print(f"Chrome驅動設置失敗: {e}")
            print("請確保已安裝ChromeDriver並正確設置路徑")
            raise
    
    def scrape_all_questions(self, base_url, start_id=3399058, total_questions=1):
        """
        抓取所有題目 (循環抓取每一題)
        Args:
            base_url (str): 基礎URL
            start_id (int): 起始題目ID
            total_questions (int): 總題目數量
        Returns:
            list: 包含所有題目信息的字典列表
        """
        all_questions = []
        
        for i in range(total_questions):
            current_id = start_id + i
            question_url = f"{base_url}?info=item.{current_id}"
            
            print(f"\n正在抓取第 {i+1}/{total_questions} 題 (ID: {current_id})")
            print(f"URL: {question_url}")
            
            try:
                question_data = self.scrape_single_question(question_url, i+1)
                if question_data:
                    all_questions.append(question_data)
                    print(question_data)
                    print(f"✓ 第 {i+1} 題抓取成功")
                else:
                    print(f"✗ 第 {i+1} 題抓取失敗")
                
                # 避免請求過於頻繁
                time.sleep(2)
                
            except Exception as e:
                print(f"✗ 第 {i+1} 題發生錯誤: {e}")
                continue
        
        return all_questions
    
    def scrape_single_question(self, url, question_num):
        """
        抓取單個題目
        Args:
            url (str): 題目頁面URL
            question_num (int): 題目編號
        Returns:
            dict: 題目信息字典
        """
        try:
            self.driver.get(url)
            
            # 注入反檢測腳本
            self.driver.execute_script("""
                // 阻止常見的反爬蟲檢測
                if (typeof window.devtools !== 'undefined') {
                    window.devtools = {open: false};
                }
                
                // 禁用右鍵檢查
                document.addEventListener('contextmenu', function(e) {
                    e.stopPropagation();
                }, true);
                
                // 禁用F12檢測
                document.addEventListener('keydown', function(e) {
                    if (e.keyCode === 123) { // F12
                        e.stopPropagation();
                    }
                }, true);
            """)
            
            # 等待頁面載入
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            
            # 滾動頁面確保內容載入
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # 獲取頁面內容
            page_source = self.driver.page_source
            
            # 嘗試不同的選擇器來找到題目內容
            question_data = {
                'question_number': question_num,
                'question_id': url.split('item.')[1] if 'item.' in url else '',
                'question_text': '',
                'options': [],
                'correct_answer': '',
                'explanation': '',
                'url': url
            }
            
            # 嘗試獲取題目文字
            question_selectors = [
                '.question-content',
                '.question-text',
                '[class*="question"]',
                '.content',
                '.item-content',
                'h3',
                'h4',
                '.card-body'
            ]
            
            question_text = ""
            for selector in question_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 10:  # 過濾太短的文字
                            question_text = text
                            break
                    if question_text:
                        break
                except:
                    continue
            
            # 如果找不到特定元素，抓取整個body內容
            if not question_text:
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                    # 簡單處理，取前500字符作為題目內容
                    question_text = body_text[:500] if body_text else "無法獲取題目內容"
                except:
                    question_text = "無法獲取題目內容"
            
            question_data['question_text'] = question_text
            
            # 嘗試獲取選項
            option_selectors = [
                '.option',
                '.choice',
                '[class*="option"]',
                '[class*="choice"]',
                'li',
                '.answer-choice'
            ]
            
            options = []
            for selector in option_selectors:
                try:
                    option_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    temp_options = []
                    for opt in option_elements:
                        text = opt.text.strip()
                        if text and len(text) < 200:  # 過濾過長的文字
                            temp_options.append(text)
                    
                    if temp_options and len(temp_options) >= 2:  # 至少要有2個選項
                        options = temp_options
                        break
                except:
                    continue
            
            question_data['options'] = options
            
            # 嘗試獲取正確答案
            answer_selectors = [
                '.correct-answer',
                '.answer',
                '[class*="correct"]',
                '[class*="answer"]',
                '.solution'
            ]
            
            correct_answer = ""
            for selector in answer_selectors:
                try:
                    answer_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    correct_answer = answer_elem.text.strip()
                    if correct_answer:
                        break
                except:
                    continue
            
            question_data['correct_answer'] = correct_answer
            
            # 嘗試獲取解析
            explanation_selectors = [
                '.explanation',
                '.解析',
                '[class*="explanation"]',
                '[class*="解析"]',
                '.detail'
            ]
            
            explanation = ""
            for selector in explanation_selectors:
                try:
                    explanation_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    explanation = explanation_elem.text.strip()
                    if explanation:
                        break
                except:
                    continue
            
            question_data['explanation'] = explanation
            
            return question_data
            
        except Exception as e:
            print(f"抓取題目時發生錯誤: {e}")
            return None
    
    def extract_question_data(self, element, question_num):
        """
        從題目元素中提取題目和答案信息
        Args:
            element: 題目元素
            question_num: 題目編號
        Returns:
            dict: 題目信息字典
        """
        question_data = {
            'question_number': question_num,
            'question_text': '',
            'options': [],
            'correct_answer': '',
            'explanation': ''
        }
        
        try:
            # 獲取題目文字
            question_text = element.text.strip()
            question_data['question_text'] = question_text
            
            # 嘗試尋找選項
            option_selectors = [
                '.option',
                '.choice',
                '[class*="option"]',
                '[class*="choice"]',
                'li'
            ]
            
            for selector in option_selectors:
                try:
                    options = element.find_elements(By.CSS_SELECTOR, selector)
                    if options:
                        question_data['options'] = [opt.text.strip() for opt in options if opt.text.strip()]
                        break
                except:
                    continue
            
            # 嘗試尋找正確答案
            answer_selectors = [
                '.correct-answer',
                '.answer',
                '[class*="correct"]',
                '[class*="answer"]'
            ]
            
            for selector in answer_selectors:
                try:
                    answer_element = element.find_element(By.CSS_SELECTOR, selector)
                    question_data['correct_answer'] = answer_element.text.strip()
                    break
                except:
                    continue
            
            # 嘗試尋找解析
            explanation_selectors = [
                '.explanation',
                '.解析',
                '[class*="explanation"]',
                '[class*="解析"]'
            ]
            
            for selector in explanation_selectors:
                try:
                    explanation_element = element.find_element(By.CSS_SELECTOR, selector)
                    question_data['explanation'] = explanation_element.text.strip()
                    break
                except:
                    continue
            
        except Exception as e:
            print(f"提取題目數據時出錯: {e}")
        
        print(question_data)
        return question_data
    
    def save_to_json(self, data, filename='yamol_questions.json'):
        """將數據保存為JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"數據已保存至 {filename}")
    
    def save_to_excel(self, data, filename='yamol_questions.xlsx'):
        """將數據保存為Excel文件"""
        if data:
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False, encoding='utf-8')
            print(f"數據已保存至 {filename}")
        else:
            print("沒有數據可保存")
    
    def close(self):
        """關閉瀏覽器驅動"""
        if self.driver:
            self.driver.quit()

def main():
    """主函數"""
    base_url = "https://app.yamol.tw/exam/125609"
    start_id = 3399058  # 第一題的ID
    total_questions = 80  # 總共80題
    
    print(f"準備抓取 {total_questions} 題，從ID {start_id} 開始")
    print(f"第1題: {base_url}?info=item.{start_id}")
    print(f"第80題: {base_url}?info=item.{start_id + total_questions - 1}")
    print("-" * 60)
    
    # 創建爬蟲實例
    scraper = YamolScraper(headless=False)  # 設為False可以看到瀏覽器運行過程
    
    try:
        # 抓取所有題目數據
        questions = scraper.scrape_all_questions(base_url, start_id, total_questions)
        
        if questions:
            print(f"\n{'='*60}")
            print(f"抓取完成！成功獲取 {len(questions)}/{total_questions} 題")
            print(f"{'='*60}")
            
            # 顯示統計信息
            successful_questions = [q for q in questions if q['question_text'] != '無法獲取題目內容']
            questions_with_options = [q for q in questions if q['options']]
            questions_with_answers = [q for q in questions if q['correct_answer']]
            
            print(f"成功獲取題目內容: {len(successful_questions)} 題")
            print(f"成功獲取選項: {len(questions_with_options)} 題") 
            print(f"成功獲取答案: {len(questions_with_answers)} 題")
            
            # 顯示第一題和最後一題的內容作為示例
            if questions:
                print(f"\n第1題內容示例:")
                print("-" * 40)
                first_question = questions[0]
                for key, value in first_question.items():
                    if key == 'options' and value:
                        print(f"{key}: {', '.join(value[:3])}{'...' if len(value) > 3 else ''}")
                    else:
                        display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                        print(f"{key}: {display_value}")
                
                if len(questions) > 1:
                    print(f"\n第{len(questions)}題內容示例:")
                    print("-" * 40)
                    last_question = questions[-1]
                    for key, value in last_question.items():
                        if key == 'options' and value:
                            print(f"{key}: {', '.join(value[:3])}{'...' if len(value) > 3 else ''}")
                        else:
                            display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                            print(f"{key}: {display_value}")
            
            # 保存數據
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            json_filename = f'yamol_questions_{timestamp}.json'
            excel_filename = f'yamol_questions_{timestamp}.xlsx'
            
            scraper.save_to_json(questions, json_filename)
            scraper.save_to_excel(questions, excel_filename)
            
        else:
            print("未能抓取到任何題目數據")
            
    except Exception as e:
        print(f"執行過程中發生錯誤: {e}")
    
    finally:
        # 關閉瀏覽器
        scraper.close()

if __name__ == "__main__":
    # 安裝所需套件的說明
    print("阿摩線上測驗爬蟲 - 125609考試 (80題)")
    print("=" * 50)
    print("請確保已安裝以下套件:")
    print("pip install selenium pandas openpyxl")
    print("並下載對應版本的ChromeDriver")
    print("=" * 50)
    
    # 詢問用戶是否要修改參數
    print("\n預設參數:")
    print("- 起始ID: 3399058 (第1題)")
    print("- 題目數量: 80題")
    print("- 結束ID: 3399137 (第80題)")
    
    user_input = input("\n是否使用預設參數？(y/n，直接按Enter使用預設): ").strip().lower()
    
    if user_input == 'n':
        try:
            start_id = int(input("請輸入起始ID (預設3399058): ") or 3399058)
            total_questions = int(input("請輸入題目數量 (預設80): ") or 80)
            print(f"將抓取從ID {start_id} 開始的 {total_questions} 題")
        except ValueError:
            print("輸入格式錯誤，使用預設參數")
            start_id = 3399058
            total_questions = 80
    
    print(f"\n開始執行...")
    main()