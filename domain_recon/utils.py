from colorama import Fore
import argparse

def parse_arguments():
    """解析命令行参数（新增自定义端口、代理、输出格式）"""
    parser = argparse.ArgumentParser(description="基于 Requests 的轻量级域名信息收集工具（新手友好版）")
    parser.add_argument("-d", "--domain", required=True, help="目标域名（如：baidu.com）")
    parser.add_argument("-w", "--wordlist", default="subdomains.txt", help="子域名字典路径（默认：subdomains.txt）")
    parser.add_argument("-o", "--output", help="结果保存文件（如：result.txt）")
    parser.add_argument("-p", "--ports", help="自定义扫描端口（逗号分隔，如：80,443,8080）")
    parser.add_argument("-f", "--format", default="txt", choices=["txt", "json", "csv"], help="输出文件格式（默认：txt）")
    parser.add_argument("--proxy", help="代理地址（如：http://127.0.0.1:8080）")
    return parser.parse_args()

def get_proxy_config(proxy):
    """配置代理（支持 HTTP/HTTPS 代理）"""
    if not proxy:
        return None
    return {
        "http": proxy,
        "https": proxy
    }

def load_subdomain_wordlist(wordlist_path):
    """加载子域名字典（处理异常）"""
    try:
        with open(wordlist_path, 'r', encoding='utf-8') as f:
            subdomains = [line.strip() for line in f if line.strip()]
        if not subdomains:
            raise ValueError("字典文件为空")
        return subdomains
    except FileNotFoundError:
        print(f"{Fore.RED}[-] 字典文件不存在：{wordlist_path}")
        exit(1)
    except Exception as e:
        print(f"{Fore.RED}[-] 加载字典失败：{str(e)}")
        exit(1)