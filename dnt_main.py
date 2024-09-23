import threading
from start_lam_banh import start_game_thread

# Định nghĩa số lượng tối đa các luồng
MAX_THREADS = 5  # Có thể điều chỉnh theo nhu cầu

# Danh sách các profile hoặc đường dẫn profile
profiles = ["./profiles/profile2"]

def main():
    threads = []
    for profile in profiles:
        # Khởi động một luồng cho mỗi profile
        thread = threading.Thread(target=start_game_thread, args=(profile,))
        threads.append(thread)
        thread.start()
        if len(threads) >= MAX_THREADS:
            break
    
    # Chờ cho tất cả các luồng hoàn thành
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
