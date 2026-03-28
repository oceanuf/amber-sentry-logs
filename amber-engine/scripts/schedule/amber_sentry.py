#!/usr/bin/env python3
"""
琥珀哨兵 (Amber Sentry) - 逻辑流监听与自动写入守护进程
版本: 1.0.0
创建时间: 2026-03-25
作者: 工程师 Cheese
团队: Cheese Intelligence Team

核心功能:
1. 监控逻辑流输入（缓冲区文件）
2. 解析特定定界符的命令块
3. 自动生成任务文件到need_to_do目录
4. 确保文件权限644和时间戳对齐

协议: [2613-068号] "琥珀哨兵"技术方案
"""

import os
import re
import time
import logging
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [AMBER_SENTRY] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class AmberSentry:
    """琥珀哨兵核心类"""
    
    def __init__(self, buffer_path=None, output_dir=None):
        """
        初始化哨兵
        
        Args:
            buffer_path: 监听缓冲区文件路径
            output_dir: 输出目录 (need_to_do)
        """
        # 默认路径
        self.buffer_path = buffer_path or "../amber_buffer.log"
        self.output_dir = output_dir or "./schedule/need_to_do"
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 上一次处理的文件大小（用于增量读取）
        self.last_size = 0
        
        # 命令块正则表达式
        self.command_pattern = re.compile(
            r'### AMBER_COMMAND_START ###\s*(.*?)\s*### AMBER_COMMAND_END ###',
            re.DOTALL
        )
        
        # 字段解析正则
        self.id_pattern = re.compile(r'ID:\s*(\S+)')
        self.target_pattern = re.compile(r'TARGET:\s*(\S+)')
        self.content_pattern = re.compile(r'CONTENT:\s*(.*)', re.DOTALL)
        
        logger.info(f"🔧 琥珀哨兵初始化完成")
        logger.info(f"  缓冲区: {self.buffer_path}")
        logger.info(f"  输出目录: {self.output_dir}")
    
    def parse_command_block(self, block):
        """
        解析命令块
        
        Args:
            block: 命令块文本
            
        Returns:
            dict: 解析后的命令数据，包含id, target, content
        """
        try:
            # 解析ID
            id_match = self.id_pattern.search(block)
            command_id = id_match.group(1) if id_match else "UNKNOWN"
            
            # 解析TARGET
            target_match = self.target_pattern.search(block)
            target_path = target_match.group(1) if target_match else None
            
            # 解析CONTENT
            content_match = self.content_pattern.search(block)
            content = content_match.group(1).strip() if content_match else ""
            
            # 如果TARGET是相对路径，转换为绝对路径
            if target_path and not os.path.isabs(target_path):
                # 尝试基于输出目录解析
                target_path = os.path.join(self.output_dir, os.path.basename(target_path))
            
            return {
                "id": command_id,
                "target": target_path,
                "content": content,
                "raw_block": block
            }
            
        except Exception as e:
            logger.error(f"解析命令块失败: {e}")
            return None
    
    def write_command_file(self, command_data):
        """
        将命令内容写入目标文件
        
        Args:
            command_data: 解析后的命令数据
            
        Returns:
            bool: 是否成功
        """
        try:
            target_path = command_data["target"]
            content = command_data["content"]
            command_id = command_data["id"]
            
            if not target_path:
                logger.error(f"命令 {command_id} 缺少TARGET字段")
                return False
            
            # 写入文件
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # 设置权限644
            os.chmod(target_path, 0o644)
            
            # 获取文件状态
            stat_info = os.stat(target_path)
            file_size = stat_info.st_size
            
            logger.info(f"📝 命令写入完成: {command_id}")
            logger.info(f"  目标文件: {target_path}")
            logger.info(f"  文件大小: {file_size} bytes")
            logger.info(f"  文件权限: {oct(stat_info.st_mode & 0o777)}")
            
            # 验证时间戳（如果有的话）
            self.validate_timestamp(content, target_path)
            
            return True
            
        except Exception as e:
            logger.error(f"写入命令文件失败: {e}")
            return False
    
    def validate_timestamp(self, content, filepath):
        """
        验证内容中的时间戳是否对齐
        
        Args:
            content: 文件内容
            filepath: 文件路径
        """
        # 查找内容中的时间戳模式
        ts_pattern = r'\[TS:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\]'
        ts_matches = re.findall(ts_pattern, content)
        
        if ts_matches:
            content_ts = ts_matches[0]
            file_ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            logger.info(f"⏰ 时间戳验证: 内容TS={content_ts}, 文件TS={file_ts}")
            
            if content_ts == file_ts:
                logger.info("✅ 时间戳对齐验证通过")
            else:
                logger.warning(f"⚠️  时间戳未对齐: 内容({content_ts}) ≠ 系统({file_ts})")
    
    def process_buffer(self):
        """
        处理缓冲区文件中的新内容
        
        Returns:
            int: 处理的命令数量
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(self.buffer_path):
                logger.warning(f"缓冲区文件不存在: {self.buffer_path}")
                return 0
            
            # 获取当前文件大小
            current_size = os.path.getsize(self.buffer_path)
            
            # 如果文件大小没有变化，直接返回
            if current_size <= self.last_size:
                return 0
            
            logger.info(f"📊 检测到缓冲区变化: {self.last_size} → {current_size} bytes")
            
            # 读取新增内容
            with open(self.buffer_path, "r", encoding="utf-8") as f:
                f.seek(self.last_size)
                new_content = f.read(current_size - self.last_size)
            
            # 更新上一次文件大小
            self.last_size = current_size
            
            # 查找命令块
            command_blocks = self.command_pattern.findall(new_content)
            
            if not command_blocks:
                logger.info("📭 未找到命令块")
                return 0
            
            logger.info(f"📦 找到 {len(command_blocks)} 个命令块")
            
            # 处理每个命令块
            processed_count = 0
            for block in command_blocks:
                command_data = self.parse_command_block(block)
                
                if command_data:
                    logger.info(f"📄 解析命令: {command_data['id']}")
                    
                    if self.write_command_file(command_data):
                        processed_count += 1
                        logger.info(f"✅ 命令处理完成: {command_data['id']}")
                    else:
                        logger.error(f"❌ 命令处理失败: {command_data['id']}")
                else:
                    logger.error(f"❌ 命令解析失败")
            
            return processed_count
            
        except Exception as e:
            logger.error(f"处理缓冲区失败: {e}")
            return 0
    
    def run_daemon(self, interval=10):
        """
        运行哨兵守护进程
        
        Args:
            interval: 轮询间隔（秒）
        """
        logger.info(f"🚀 琥珀哨兵守护进程启动")
        logger.info(f"  轮询间隔: {interval}秒")
        logger.info(f"  按Ctrl+C停止")
        
        try:
            while True:
                # 处理缓冲区
                processed = self.process_buffer()
                
                if processed > 0:
                    logger.info(f"🔄 本轮处理完成: {processed}个命令")
                
                # 等待下一次轮询
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 接收到停止信号，哨兵停止运行")
        except Exception as e:
            logger.error(f"🚨 守护进程异常: {e}")
    
    def run_once(self):
        """
        单次运行模式（用于测试）
        """
        logger.info("🧪 单次运行模式启动")
        processed = self.process_buffer()
        logger.info(f"📊 单次运行完成: 处理{processed}个命令")
        return processed


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='琥珀哨兵 - 逻辑流监听守护进程')
    parser.add_argument('--daemon', action='store_true', help='以守护进程模式运行')
    parser.add_argument('--interval', type=int, default=10, help='轮询间隔（秒，仅守护进程模式）')
    parser.add_argument('--buffer', type=str, help='缓冲区文件路径')
    parser.add_argument('--output', type=str, help='输出目录路径')
    
    args = parser.parse_args()
    
    # 创建哨兵实例
    sentry = AmberSentry(
        buffer_path=args.buffer,
        output_dir=args.output
    )
    
    if args.daemon:
        sentry.run_daemon(interval=args.interval)
    else:
        sentry.run_once()


if __name__ == "__main__":
    main()