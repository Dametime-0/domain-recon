import requests
import socket
import urllib3
from concurrent.futures import ThreadPoolExecutor
from .utils import get_proxy_config
from bs4 import BeautifulSoup

# 关闭SSL证书验证警告（优化用户体验）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 全局配置
DEFAULT_TIMEOUT = 5
DEFAULT_MAX_THREADS = 10
DEFAULT_COMMON_PORTS = [80, 443, 22, 8080, 3389, 8443, 8000, 9000]


def get_page_title(url, proxy=None):
    """获取页面标题（最终稳定版，支持静态解析+容错）"""
    try:
        proxies = get_proxy_config(proxy)
        # 模拟Chrome浏览器完整请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }
        # 禁用自动重定向，手动处理301/302（避免标题丢失）
        resp = requests.get(
            url,
            timeout=DEFAULT_TIMEOUT,
            allow_redirects=False,
            proxies=proxies,
            headers=headers,
            verify=False,
            stream=False
        )

        # 手动处理重定向
        if resp.status_code in [301, 302] and 'Location' in resp.headers:
            redirect_url = resp.headers['Location']
            if not redirect_url.startswith('http'):
                redirect_url = f"{url.split('://')[0]}://{url.split('://')[1].split('/')[0]}{redirect_url}"
            resp = requests.get(
                redirect_url,
                timeout=DEFAULT_TIMEOUT,
                headers=headers,
                proxies=proxies,
                verify=False
            )

        # 强制UTF-8编码，避免乱码
        resp.encoding = 'utf-8'
        # 使用Python内置解析器（无需额外依赖，兼容所有环境）
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 多方式获取标题（层层兜底，避免No Title）
        title = ""
        # 方式1：优先解析title标签
        title_tag = soup.find('title')
        if title_tag and title_tag.text.strip():
            title = title_tag.text.strip()
        # 方式2：解析og:title（社交标签）
        elif soup.find('meta', property='og:title'):
            title = soup.find('meta', property='og:title')['content'].strip()
        # 方式3：解析description（兜底，修复参数冲突问题）
        elif soup.find('meta', attrs={'name': 'description'}):
            title = soup.find('meta', attrs={'name': 'description'})['content'].strip()

        return title if title else "No Title"
    except Exception as e:
        return f"获取失败: {str(e)[:50]}"


def scan_port(host, port):
    """扫描单个端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(DEFAULT_TIMEOUT)
        result = sock.connect_ex((host, port))
        sock.close()
        return port if result == 0 else None
    except Exception:
        return None


def scan_subdomain(domain, sub, proxy=None):
    """扫描单个子域名是否存活（优先HTTP，适配小众域名）"""
    sub_domain = f"{sub}.{domain}".strip()
    try:
        proxies = get_proxy_config(proxy)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        # 先试HTTP，再试HTTPS（兼容更多域名）
        for scheme in ['http', 'https']:
            url = f"{scheme}://{sub_domain}"
            resp = requests.head(
                url,
                timeout=DEFAULT_TIMEOUT,
                allow_redirects=True,
                proxies=proxies,
                headers=headers,
                verify=False
            )
            if resp.status_code in range(200, 400):
                return {
                    "sub_domain": sub_domain,
                    "scheme": scheme,
                    "status_code": resp.status_code
                }
        return None
    except Exception:
        return None


def batch_scan_subdomains(domain, subdomains, proxy=None, progress_bar=None):
    """批量扫描子域名（带进度条）"""
    results = []
    with ThreadPoolExecutor(max_workers=DEFAULT_MAX_THREADS) as executor:
        future_to_sub = {executor.submit(scan_subdomain, domain, sub, proxy): sub for sub in subdomains}
        for future in future_to_sub:
            result = future.result()
            if progress_bar:
                progress_bar.update(1)
            if result:
                results.append(result)
    return results


def batch_scan_ports_and_title(subdomain_results, ports, proxy=None, progress_bar=None):
    """批量扫描端口+标题（带进度条）"""
    final_results = []
    with ThreadPoolExecutor(max_workers=DEFAULT_MAX_THREADS) as executor:
        for item in subdomain_results:
            host = item["sub_domain"]
            # 扫描端口
            port_futures = [executor.submit(scan_port, host, port) for port in ports]
            open_ports = []
            for f in port_futures:
                p = f.result()
                if p:
                    open_ports.append(p)
                if progress_bar:
                    progress_bar.update(1)
            # 获取标题
            title = get_page_title(f"{item['scheme']}://{host}", proxy)
            # 整合结果
            final_item = {
                "sub_domain": host,
                "status_code": item["status_code"],
                "open_ports": open_ports,
                "title": title
            }
            final_results.append(final_item)
    return final_results