class TavilySearchTool:
    """Tavily搜索工具的简单模拟实现"""
    
    def invoke(self, request):
        """
        执行搜索请求。
        
        Args:
            request: 搜索请求
            
        Returns:
            搜索结果列表
        """
        # 实际实现中，这里会调用Tavily API
        # 当前只是返回模拟数据
        return [
            {
                "title": "模拟搜索结果 1",
                "content": "这是一个模拟的搜索结果内容。"
            },
            {
                "title": "模拟搜索结果 2",
                "content": "这是另一个模拟的搜索结果内容。"
            }
        ]

# 创建一个实例供导入使用
tavily_tool = TavilySearchTool()
