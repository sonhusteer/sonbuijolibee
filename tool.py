from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
import urllib.request
import json
import sys
import msvcrt

def get_input_timeout(prompt, default_min, default_max, timeout=5):
    print(f"{prompt} (mặc định ngẫu nhiên từ {default_min}-{default_max}, tự động chọn sau {timeout}s): ", end='', flush=True)
    start_time = time.time()
    input_str = ""
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getwche()
            if char in ('\r', '\n'):
                print()
                break
            elif char == '\x08': # backspace
                input_str = input_str[:-1]
                print(' \x08', end='', flush=True)
            else:
                input_str += char
        if time.time() - start_time > timeout:
            print("\nHết thời gian chờ! Tự động sử dụng giá trị mặc định.")
            break
        time.sleep(0.05)
    
    if input_str.strip().isdigit():
        return int(input_str.strip())
    return random.randint(default_min, default_max)


def human_typing(element, text):
    """Gõ từng phím một giống người thật (delay ngẫu nhiên), đôi khi gõ sai và sửa lại"""
    for char in text:
        # 3% cơ hội gõ nhầm 1 ký tự rồi xóa đi gõ lại (typing mistake)
        if random.random() < 0.03 and char.isalpha():
            wrong_char = random.choice("abcdefghijklmnopqrstuvwxyz")
            element.send_keys(wrong_char)
            time.sleep(random.uniform(0.1, 0.3))
            element.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.2, 0.5))
        element.send_keys(char)
        time.sleep(random.uniform(0.04, 0.15))
    # Ngập ngừng 1 chút sau khi gõ xong (thói quen người dùng tự đọc lại chữ đã gõ)
    time.sleep(random.uniform(0.5, 1.5))


def get_dynamic_keyword():
    """Tự động lấy từ khóa tìm kiếm có thật từ Internet thông qua Autocomplete API"""
    try:
        # Lấy một hoặc hai chữ cái ngẫu nhiên (ví dụ 'a', 'b', 'tr', 'nh'...)
        chars = random.choice("abcdefghijklmnopqrstuvwxyz")
        if random.random() > 0.5:
            chars += random.choice("abcdefghijklmnopqrstuvwxyz")
        # Gọi thử API gợi ý tìm kiếm của Google cho ký tự này
        url = f"http://suggestqueries.google.com/complete/search?client=chrome&q={chars}&hl=vi"
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            suggestions = data[1]
            if suggestions:
                return random.choice(suggestions)
    except Exception:
        pass
    # Phương án dự phòng (fallback) lỡ API không phản hồi
    return random.choice(
        [
            "tin tức mới nhất",
            "du lịch trải nghiệm",
            "thời tiết hôm nay",
            "giá vàng trong nước",
        ]
    )


# Random số lượng tìm kiếm thay vì ngày nào cũng gõ đúng 30 - 20 (Dễ bị lộ pattern), hoặc cho phép người dùng tự nhập
NUM_PC = get_input_timeout("Nhập số lượt tìm kiếm PC", 26, 30, timeout=5)
NUM_MOBILE = get_input_timeout("Nhập số lượt tìm kiếm Mobile", 20, 24, timeout=5)


def human_delay(min_sec=4, max_sec=10):
    time.sleep(random.uniform(min_sec, max_sec))


def human_scroll(driver, min_distance=300, max_distance=800, direction="down"):
    """Cuộn trang mượt mà như người dùng vuốt trên điện thoại hoặc lăn chuột"""
    distance = random.randint(min_distance, max_distance)
    steps = random.randint(10, 25)
    step_amount = distance / steps
    for _ in range(steps):
        # Trọng số ngẫu nhiên để mô phỏng ngón tay vuốt mượt nhưng không đều
        scroll_val = step_amount * random.uniform(0.8, 1.2)
        if direction == "up":
            scroll_val = -scroll_val
        driver.execute_script(f"window.scrollBy(0, {scroll_val});")
        time.sleep(random.uniform(0.02, 0.08))


def setup_driver(is_mobile=False):
    options = Options()
    # Tạo thư mục lưu đăng nhập
    profile_dir = os.path.join(
        os.getcwd(), "edge_profile"
    )
    options.add_argument(f"user-data-dir={profile_dir}")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option(
        "excludeSwitches", ["enable-automation", "enable-logging"]
    )
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")
    # Chạy ngầm: cửa sổ thật (không headless) nhưng thu nhỏ và đẩy ra ngoài màn hình
    options.add_argument("--window-size=1280,900")
    options.add_argument("--window-position=-2400,-2400")
    options.add_argument("--start-minimized")
    options.add_argument("--disable-notifications")
    if is_mobile:
        # Cấu hình Mobile an toàn (không dùng deviceName để tránh lỗi "must be a valid device")
        user_agent_mobile = "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 EdgA/116.0.0.0"
        mobile_emulation = {
            "deviceMetrics": {"width": 412, "height": 915, "pixelRatio": 3.0},
            "userAgent": user_agent_mobile,
            "clientHints": {"platform": "Android", "mobile": True},
        }
        options.add_experimental_option("mobileEmulation", mobile_emulation)
    # Tự động tải driver thông qua Selenium (bản 4.6+)
    driver = webdriver.Edge(options=options)
    try:
        driver.minimize_window()
    except Exception:
        pass
    return driver


def run_bing_searches(is_mobile=False):
    mode = "📱 MOBILE" if is_mobile else "💻 PC"
    total_searches = NUM_MOBILE if is_mobile else NUM_PC
    print(f"\n🚀 Bắt đầu tool kiếm điểm bằng {mode} ({total_searches} lần tìm kiếm)")
    try:
        driver = setup_driver(is_mobile)
    except Exception as e:
        print(f"❌ Lỗi khởi tạo trình duyệt ({mode}):\n{e}")
        return
    try:
        print(
            "⏳ Đang mở Bing chạy ngầm (cửa sổ thu nhỏ). Đăng nhập sẵn trong profile thì không cần mở cửa sổ."
        )
        driver.get("https://www.bing.com")
        human_delay(
            6, 36
        )  # Trễ lâu ở lần đầu để có thể đăng nhập / bypass check nếu có
        for i in range(1, total_searches + 1):
            try:
                wait = WebDriverWait(driver, 10)
                # Quét các selector phổ biến của ô tìm kiếm Bing cho cả PC lẫn điện thoại
                search_selectors = [
                    (By.ID, "sb_form_q"),
                    (By.NAME, "q"),
                    (By.ID, "sa_1_q"),
                ]
                search_box = None
                for by_type, sel in search_selectors:
                    try:
                        search_box = wait.until(
                            EC.presence_of_element_located((by_type, sel))
                        )
                        if search_box.is_displayed():
                            break
                    except:
                        pass
                if not search_box:
                    print(
                        f"⚠️ [{i}/{total_searches}] Không tìm thấy ô search tab. Thử tải lại trang..."
                    )
                    driver.refresh()
                    human_delay(5, 8)
                    continue
                # Tạo từ khóa tìm kiếm có ý nghĩa từ Autocomplete, không dùng mảng tạo sẵn nữa.
                keyword = get_dynamic_keyword()
                # 3 cách xóa chữ cũ: Bôi đen -> Xóa, Bôi đen -> Gõ đè, hoặc Bấm nút X (clear)
                clear_method = random.choice(["ctrl_a_del", "ctrl_a_type", "clear"])
                if clear_method == "ctrl_a_del":
                    search_box.send_keys(Keys.CONTROL + "a")
                    time.sleep(random.uniform(0.2, 0.5))
                    search_box.send_keys(Keys.BACKSPACE)
                elif clear_method == "ctrl_a_type":
                    search_box.send_keys(Keys.CONTROL + "a")
                    time.sleep(random.uniform(0.2, 0.5))
                else:
                    search_box.clear()  # Giả lập bấm dấu X (thường là clear text)
                time.sleep(random.uniform(0.3, 0.8))
                # Gõ từ khóa liên tục từng chữ một, đôi khi gõ phím nhầm
                human_typing(search_box, keyword)
                # Việc kết thúc lệnh tìm kiếm: Không phải lúc nào cũng bấm ENTER
                if random.random() < 0.7:
                    search_box.send_keys(Keys.RETURN)
                else:
                    try:
                        # Thử click vào biểu tượng kính lúp (cách khác để nhấn "Tìm")
                        search_btn = driver.find_element(By.ID, "sb_form_go")
                        driver.execute_script("arguments[0].click();", search_btn)
                    except:
                        search_box.send_keys(Keys.RETURN)
                print(f"✅ {mode} [{i}/{total_searches}] Đã tìm: '{keyword}'")
                
                # Chờ kết quả tìm kiếm tải xong (Tối đa 7 giây)
                try:
                    WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.ID, "b_results")))
                except:
                    pass

                # Chờ kết quả tải xong và cuộn chậm từ từ xuống đọc tin (Cuộn mượt)
                human_delay(2, 4)
                human_scroll(
                    driver, min_distance=300, max_distance=800, direction="down"
                )
                human_delay(1, 3)
                
                # 60% xác suất click vào 1 trang web thực tế, xử lý tốt cho cả Điện thoại/PC
                if random.random() < 0.6:
                    try:
                        # Gom chung cấu trúc cho thẻ chứa link của Bing cả trên PC và Mobile
                        results = driver.find_elements(
                            By.CSS_SELECTOR,
                            "#b_results h2 a, #b_results .b_algo a, #b_results .b_title a, #b_results div.b_title a, .b_algo h2 a"
                        )
                        
                        # Lấy các link hợp lệ (Lọc bỏ link rác)
                        valid_results = []
                        for link in results:
                            try:
                                href = link.get_attribute('href')
                                if href and href.startswith('http'):
                                    # Chấp nhận link thật HOẶC link được Bing bọc qua /ck/ (tracking click)
                                    if "bing.com" in href and "/ck/" not in href:
                                        continue
                                    if "microsoft.com/rewards" in href:
                                        continue
                                    valid_results.append(link)
                            except:
                                pass
                                
                        if valid_results:
                            random_link = random.choice(valid_results[:5])
                            original_window = driver.current_window_handle
                            
                            try:
                                href_to_open = random_link.get_attribute('href')
                            except:
                                href_to_open = ""
                            
                            # Cuộn màn hình đúng chỗ cái link đó trước khi bấm
                            try:
                                driver.execute_script(
                                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                    random_link,
                                )
                            except:
                                pass
                            human_delay(1, 3)
                            
                            print(f"   -> 📱/💻 Mở link để đọc ({len(valid_results)} kq tìm thấy)...")
                            
                            # Phương pháp click tự nhiên thay vì dùng window.open (bị trình duyệt chặn pop-up ở PC)
                            # Control + Click để mở tab mới an toàn hơn
                            from selenium.webdriver.common.action_chains import ActionChains
                            try:
                                actions = ActionChains(driver)
                                actions.key_down(Keys.CONTROL).click(random_link).key_up(Keys.CONTROL).perform()
                            except:
                                # Backup nếu Control+Click lỗi
                                driver.execute_script(f"window.open('{href_to_open}', '_blank');")
                            
                            human_delay(1, 2)
                            
                            # Chuyển focus sang tab mới mở
                            if len(driver.window_handles) > 1:
                                driver.switch_to.window(driver.window_handles[-1])
                            
                            # Giả lập thời gian vào trang mới: đọc đứng im 1 lúc -> lướt xuống dài -> dừng đọc -> lướt lên
                            human_delay(3, 7)
                            human_scroll(
                                driver,
                                min_distance=400,
                                max_distance=1000,
                                direction="down",
                            )
                            human_delay(2, 5)
                            
                            if random.random() < 0.5:
                                human_scroll(
                                    driver,
                                    min_distance=200,
                                    max_distance=600,
                                    direction="up",
                                )
                                human_delay(1, 4)
                                
                            # Luôn đóng thẻ (Close Tab) và quay về tab tìm kiếm đầu tiên
                            if len(driver.window_handles) > 1:
                                driver.close()
                                driver.switch_to.window(original_window)
                            human_delay(2, 4)
                        else:
                            print("   -> Không tìm thấy link tự nhiên hợp lệ nào để click.")
                    except Exception as e:
                        # Đề phòng lỗi kẹt Thẻ, thử chuyển bề Tab đầu tiên
                        try:
                            driver.switch_to.window(driver.window_handles[0])
                        except:
                            pass
                        print(
                            "   -> Bỏ qua đọc trang do mạng chậm. Đọc lướt tiếp..."
                        )
                        
                # Việc lướt vô định thêm ở cuối trước khi sang lần tìm kiếm mới
                if random.random() < 0.4:
                    human_scroll(
                        driver,
                        min_distance=200,
                        max_distance=500,
                        direction=random.choice(["up", "down"]),
                    )
                    human_delay(2, 4)
            except Exception as e:
                print(
                    "⚠️ Lỗi trong vòng lặp tìm kiếm. Tự động chuyển qua tìm kiếm tại trang chủ..."
                )
                driver.get("https://www.bing.com")
                driver.get("https://www.bing.com")
                human_delay(3, 6)
    finally:
        driver.quit()
        print(f"🛑 Đã đóng trình duyệt {mode}.")


if __name__ == "__main__":
    print("=" * 60)
    print("TOOL AUTO SEARCH BING REWARDS - PHIÊN BẢN ỔN ĐỊNH")
    print("Tự động chống ban và vượt qua kiểm tra môi trường")
    print("=" * 60)
    # Chạy lần lượt cả 2 với khoảng nghỉ dài để an toàn
    run_bing_searches(is_mobile=False)  # PC
    print("\n⏳ Đang nghỉ xả hơi (15s) tránh bị bot Microsoft quét liên tục...")
    human_delay(12, 18)
    run_bing_searches(is_mobile=True)  # Điện thoại
    print("\n🎉 HOÀN THÀNH TOÀN BỘ TÁC VỤ!")
    print("👉 Hãy truy cập https://rewards.microsoft.com để kiểm tra điểm.")
