from domain_recon.scanner import (
    batch_scan_subdomains,
    batch_scan_ports_and_title,
    DEFAULT_COMMON_PORTS
)
from domain_recon.output import print_colored_result, save_results_to_file
from domain_recon.utils import parse_arguments, load_subdomain_wordlist
from colorama import Fore
from tqdm import tqdm  # 进度条库
from datetime import datetime


def main():
    # 1. 解析参数
    args = parse_arguments()
    print(f"{Fore.CYAN}[+] 开始扫描 {args.domain} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 2. 处理端口参数（自定义端口 / 默认端口）
    ports = DEFAULT_COMMON_PORTS
    if args.ports:
        try:
            ports = [int(p.strip()) for p in args.ports.split(",")]
            print(f"{Fore.CYAN}[+] 自定义扫描端口：{ports}")
        except ValueError:
            print(f"{Fore.RED}[-] 端口格式错误，请输入数字（逗号分隔）")
            exit(1)

    # 3. 加载子域名字典
    subdomains = load_subdomain_wordlist(args.wordlist)
    print(f"{Fore.CYAN}[+] 加载子域名字典：{len(subdomains)} 个条目")

    # 4. 扫描子域名（带进度条）
    with tqdm(total=len(subdomains), desc="扫描子域名", ncols=80) as pbar:
        subdomain_results = batch_scan_subdomains(args.domain, subdomains, args.proxy, pbar)

    if not subdomain_results:
        print(f"{Fore.RED}[-] 未发现存活子域名")
        return
    print(f"{Fore.GREEN}[+] 发现存活子域名：{len(subdomain_results)} 个")

    # 5. 扫描端口+标题（带进度条）
    total_port_tasks = len(subdomain_results) * len(ports)
    with tqdm(total=total_port_tasks, desc="扫描端口+标题", ncols=80) as pbar:
        final_results = batch_scan_ports_and_title(subdomain_results, ports, args.proxy, pbar)

    # 6. 终端输出结果
    for result in final_results:
        print_colored_result(result)

    # 7. 保存结果到文件（如果指定）
    if args.output:
        save_results_to_file(final_results, args.domain, args.output, args.format)

    print(f"\n{Fore.CYAN}[+] 扫描完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    # 安装 tqdm（如果未安装）
    try:
        from tqdm import tqdm
    except ImportError:
        print(f"{Fore.YELLOW}[*] 正在安装进度条库 tqdm...")
        import subprocess
        import sys

        subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
        from tqdm import tqdm  # 重新导入
    main()