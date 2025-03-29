import json
import logging

logger = logging.getLogger(__name__)

try:
    import json_repair
    JSON_REPAIR_AVAILABLE = True
except ImportError:
    JSON_REPAIR_AVAILABLE = False
    logger.warning("json_repair 库未安装，JSON修复功能将受限")


def repair_json_output(content):
    """
    尝试修复可能损坏的JSON输出。
    
    Args:
        content: 输入内容
        
    Returns:
        修复后的内容
    """
    # 如果内容不是字符串，直接返回
    if not isinstance(content, str):
        return content
        
    # 首先尝试直接解析
    try:
        json.loads(content)
        return content  # 如果成功解析，说明JSON是有效的
    except json.JSONDecodeError:
        pass
        
    # 尝试使用json_repair修复
    if JSON_REPAIR_AVAILABLE:
        try:
            repaired = json_repair.loads(content)
            return json.dumps(repaired)
        except Exception as e:
            logger.warning(f"JSON修复失败: {e}")
            
    # 如果无法修复，返回原始内容
    return content
