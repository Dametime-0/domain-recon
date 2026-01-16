import json
import csv
from colorama import init, Fore, Back
from datetime import datetime

# 初始化彩色输出
init(autoreset=True)

def print_colored_result(result):
    """彩色打印单条结果到终端"""
    print(f"\n{Back.BLUE}{Fore.WHITE}[结果] {result['sub_domain']}")
    print(f"{Fore.WHITE}状态码：{result['status_code']}")
    print(f"{Fore.WHITE}开放端口：{result['open_ports'] if result['open_ports'] else '无'}")
    print(f"{Fore.WHITE}页面标题：{result['title']}")

def save_results_to_file(results, domain, output_file, output_format):
    """保存结果到文件（支持 TXT/JSON/CSV）"""
    try:
        if output_format == "txt":
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"扫描时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"目标域名：{domain}\n")
                f.write("="*80 + "\n")
                for item in results:
                    f.write(f"子域名：{item['sub_domain']}\n")
                    f.write(f"状态码：{item['status_code']}\n")
                    f.write(f"开放端口：{item['open_ports']}\n")
                    f.write(f"页面标题：{item['title']}\n")
                    f.write("-"*80 + "\n")
        elif output_format == "json":
            output_data = {
                "scan_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "target_domain": domain,
                "results": results
            }
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=4)
        elif output_format == "csv":
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ["sub_domain", "status_code", "open_ports", "title"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for item in results:
                    # 处理端口列表为字符串（CSV 不支持列表）
                    item["open_ports"] = ",".join(map(str, item["open_ports"]))
                    writer.writerow(item)
        print(f"{Fore.GREEN}[+] 结果已保存到：{output_file}（格式：{output_format}）")
    except Exception as e:
        print(f"{Fore.RED}[-] 保存文件失败：{str(e)}")