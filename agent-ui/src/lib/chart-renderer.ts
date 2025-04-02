/**
 * Chart renderer utility for the Chart Rendering Agent
 * 
 * This utility provides functions to process the output from the chart rendering agent
 * and convert it to the format expected by the Chart component.
 */
import type { ChartProps, ChartType, DataSource, FieldConfig } from '@/types/chart';

interface ChartAgentOutput {
  type: ChartType;
  dataSource: {
    table: string;
    field: string[];
  };
  dimensions: Array<{
    field: string;
    name: string;
  }>;
  measures: Array<{
    field: string;
    name: string;
  }>;
  series?: {
    field: string;
    name: string;
  };
  config: {
    title: string;
    height?: number;
    colors?: string[];
    stacked?: boolean;
    fillOpacity?: number;
    sizeField?: string;
    [key: string]: any;
  };
}

/**
 * Converts chart agent output to chart component props
 * 
 * @param agentOutput The JSON output from the chart rendering agent
 * @returns Chart component props
 */
export function convertAgentOutputToChartProps(agentOutput: ChartAgentOutput): ChartProps {
  return {
    type: agentOutput.type,
    dataSource: agentOutput.dataSource,
    dimensions: agentOutput.dimensions,
    measures: agentOutput.measures,
    series: agentOutput.series,
    config: agentOutput.config
  };
}

/**
 * Validates chart agent output
 * 
 * @param output The JSON output to validate
 * @returns True if valid, false otherwise
 */
export function validateChartAgentOutput(output: any): output is ChartAgentOutput {
  if (!output || typeof output !== 'object') {
    return false;
  }
  
  // Check required properties
  if (!output.type || !output.dataSource || !output.dimensions || !output.measures || !output.config) {
    return false;
  }
  
  // Check type is a valid chart type
  const validTypes: ChartType[] = [
    'bar', 'line', 'pie', 'scatter', 'area', 'heatmap', 'radar', 'funnel'
  ];
  if (!validTypes.includes(output.type)) {
    return false;
  }
  
  // Check dataSource
  if (!output.dataSource.table || !Array.isArray(output.dataSource.field)) {
    return false;
  }
  
  // Check dimensions
  if (!Array.isArray(output.dimensions) || output.dimensions.length === 0) {
    return false;
  }
  
  for (const dim of output.dimensions) {
    if (!dim.field || !dim.name) {
      return false;
    }
  }
  
  // Check measures
  if (!Array.isArray(output.measures) || output.measures.length === 0) {
    return false;
  }
  
  for (const measure of output.measures) {
    if (!measure.field || !measure.name) {
      return false;
    }
  }
  
  // Check series (optional)
  if (output.series && (!output.series.field || !output.series.name)) {
    return false;
  }
  
  // Check config
  if (!output.config.title) {
    return false;
  }
  
  return true;
}

/**
 * Processes chart rendering agent output text
 * 
 * @param agentOutputText The raw text output from the chart rendering agent
 * @returns Chart component props or null if invalid
 */
export function processChartAgentOutput(agentOutputText: string): ChartProps | null {
  try {
    // Try to extract JSON from the text
    const jsonMatch = agentOutputText.match(/```json\s*([\s\S]*?)\s*```/) || 
                       agentOutputText.match(/\{[\s\S]*\}/);
    
    if (!jsonMatch) {
      console.error('No JSON found in agent output');
      return null;
    }
    
    const jsonString = jsonMatch[1] || jsonMatch[0];
    const parsedOutput = JSON.parse(jsonString);
    
    if (!validateChartAgentOutput(parsedOutput)) {
      console.error('Invalid chart agent output format');
      return null;
    }
    
    return convertAgentOutputToChartProps(parsedOutput);
  } catch (error) {
    console.error('Error processing chart agent output:', error);
    return null;
  }
}

/**
 * Tests chart agent output with a test case from the imported test file
 * 
 * @param testCaseName Name of the test case to run
 * @returns Processed chart props
 */
export function testChartAgent(testCaseName: string): ChartProps | null {
  // These are sample outputs that match the test cases in the imported file
  const testCases: Record<string, ChartAgentOutput> = {
    'monthly_sales_trend': {
      "type": "line",
      "dataSource": {
        "table": "sales_quarterly_data",
        "field": ["month", "category", "sales", "profit", "customers"]
      },
      "dimensions": [
        {
          "field": "month",
          "name": "月份"
        }
      ],
      "measures": [
        {
          "field": "sales",
          "name": "销售额"
        }
      ],
      "series": {
        "field": "category",
        "name": "类别"
      },
      "config": {
        "title": "月度销售趋势",
        "height": 350,
        "colors": ["#4e79a7", "#f28e2c"]
      }
    },
    'product_category_distribution': {
      "type": "pie",
      "dataSource": {
        "table": "product_sales",
        "field": ["category", "total_sales", "percentage"]
      },
      "dimensions": [
        {
          "field": "category",
          "name": "产品类别"
        }
      ],
      "measures": [
        {
          "field": "percentage",
          "name": "占比"
        }
      ],
      "config": {
        "title": "产品类别销售占比",
        "height": 350,
        "colors": ["#4e79a7", "#f28e2c", "#e15759", "#76b7b2", "#59a14f"]
      }
    },
    'sales_profit_correlation': {
      "type": "scatter",
      "dataSource": {
        "table": "store_performance",
        "field": ["store_id", "region", "sales", "profit", "area", "employees"]
      },
      "dimensions": [
        {
          "field": "sales",
          "name": "销售额"
        }
      ],
      "measures": [
        {
          "field": "profit",
          "name": "利润"
        }
      ],
      "series": {
        "field": "region",
        "name": "区域"
      },
      "config": {
        "title": "销售额与利润相关性分析",
        "height": 400,
        "sizeField": "area"
      }
    },
    'customer_retention_funnel': {
      "type": "funnel",
      "dataSource": {
        "table": "customer_journey",
        "field": ["stage", "customers", "conversion_rate"]
      },
      "dimensions": [
        {
          "field": "stage",
          "name": "阶段"
        }
      ],
      "measures": [
        {
          "field": "customers",
          "name": "客户数"
        }
      ],
      "config": {
        "title": "客户转化漏斗",
        "height": 400
      }
    },
    'performance_radar': {
      "type": "radar",
      "dataSource": {
        "table": "product_performance",
        "field": ["product_line", "sales_score", "profit_score", "satisfaction_score", "market_share_score", "growth_score"]
      },
      "dimensions": [
        {
          "field": "product_line",
          "name": "产品线"
        }
      ],
      "measures": [
        {
          "field": "sales_score",
          "name": "销售额"
        },
        {
          "field": "profit_score",
          "name": "利润率"
        },
        {
          "field": "satisfaction_score",
          "name": "客户满意度"
        },
        {
          "field": "market_share_score",
          "name": "市场份额"
        },
        {
          "field": "growth_score",
          "name": "增长率"
        }
      ],
      "config": {
        "title": "产品多维度表现评估",
        "height": 400
      }
    },
    'website_traffic_area': {
      "type": "area",
      "dataSource": {
        "table": "website_analytics",
        "field": ["month", "channel", "visits"]
      },
      "dimensions": [
        {
          "field": "month",
          "name": "月份"
        }
      ],
      "measures": [
        {
          "field": "visits",
          "name": "访问量"
        }
      ],
      "series": {
        "field": "channel",
        "name": "渠道"
      },
      "config": {
        "title": "网站流量趋势",
        "height": 350,
        "stacked": true,
        "fillOpacity": 0.7
      }
    },
    'regional_heatmap': {
      "type": "heatmap",
      "dataSource": {
        "table": "regional_sales",
        "field": ["province", "city", "sales_density", "store_count"]
      },
      "dimensions": [
        {
          "field": "province",
          "name": "省份"
        },
        {
          "field": "city",
          "name": "城市"
        }
      ],
      "measures": [
        {
          "field": "sales_density",
          "name": "销售密度"
        }
      ],
      "config": {
        "title": "区域销售密度热力图",
        "height": 500
      }
    },
    'age_group_analysis': {
      "type": "bar",
      "dataSource": {
        "table": "customer_age_analysis",
        "field": ["age_group", "average_spend", "purchase_frequency", "online_ratio"]
      },
      "dimensions": [
        {
          "field": "age_group",
          "name": "年龄段"
        }
      ],
      "measures": [
        {
          "field": "average_spend",
          "name": "平均消费"
        },
        {
          "field": "purchase_frequency",
          "name": "购买频次"
        },
        {
          "field": "online_ratio",
          "name": "线上购买比例"
        }
      ],
      "config": {
        "title": "不同年龄段消费行为分析",
        "height": 400
      }
    }
  };

  return testCases[testCaseName] ? convertAgentOutputToChartProps(testCases[testCaseName]) : null;
}

/**
 * Processes raw chart agent input and generates charts based on natural language description
 * 
 * @param agentInput Natural language input describing the desired chart
 * @returns Chart component props or null if processing fails
 */
export async function generateChartFromDescription(agentInput: string): Promise<ChartProps | null> {
  try {
    // Here we would call the actual chart rendering agent API
    // For now, we'll simulate it with a mock response based on keywords in the input
    const lowerInput = agentInput.toLowerCase();
    
    if (lowerInput.includes('sale') && lowerInput.includes('trend')) {
      return testChartAgent('monthly_sales_trend');
    }
    
    if (lowerInput.includes('category') && (lowerInput.includes('distribution') || lowerInput.includes('proportion'))) {
      return testChartAgent('product_category_distribution');
    }
    
    if ((lowerInput.includes('correlation') || lowerInput.includes('relationship')) && 
        lowerInput.includes('profit')) {
      return testChartAgent('sales_profit_correlation');
    }
    
    if (lowerInput.includes('funnel') || lowerInput.includes('conversion')) {
      return testChartAgent('customer_retention_funnel');
    }
    
    if (lowerInput.includes('radar') || 
        (lowerInput.includes('dimension') && lowerInput.includes('performance'))) {
      return testChartAgent('performance_radar');
    }
    
    if (lowerInput.includes('traffic') || lowerInput.includes('visit')) {
      return testChartAgent('website_traffic_area');
    }
    
    if (lowerInput.includes('heat') || lowerInput.includes('regional')) {
      return testChartAgent('regional_heatmap');
    }
    
    if (lowerInput.includes('age') || lowerInput.includes('group')) {
      return testChartAgent('age_group_analysis');
    }
    
    // Default fallback
    return testChartAgent('monthly_sales_trend');
  } catch (error) {
    console.error('Error generating chart from description:', error);
    return null;
  }
}
