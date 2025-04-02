/**
 * Integration utilities for the Chart Rendering Agent
 * 
 * This file provides functions to integrate with the Chart Rendering Agent described in the test file.
 * It handles sending data analysis results to the agent and processing the agent's response.
 */
import { processChartAgentOutput } from './chart-renderer';
import type { ChartProps } from '@/types/chart';

/**
 * Calls the chart rendering agent with analysis data
 * 
 * @param analysisData String containing data analysis results
 * @returns Promise resolving to chart props
 */
export async function callChartRenderingAgent(analysisData: string): Promise<ChartProps | null> {
  try {
    // In a real implementation, this would call your agent API
    // For now, we'll mock the response based on keywords in the input
    
    // Example API call (commented out):
    // const response = await fetch('/api/agents/chart-renderer', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    //   body: JSON.stringify({ analysisData }),
    // });
    // 
    // if (!response.ok) {
    //   throw new Error(`Agent API error: ${response.status}`);
    // }
    // 
    // const result = await response.json();
    // return processChartAgentOutput(result.output);
    
    // For now, let's simulate a response
    const mockOutput = mockChartRenderingAgentResponse(analysisData);
    return processChartAgentOutput(mockOutput);
  } catch (error) {
    console.error('Error calling chart rendering agent:', error);
    return null;
  }
}

/**
 * Simulate a response from the chart rendering agent based on keywords
 * 
 * @param analysisData String containing data analysis results
 * @returns Simulated agent output
 */
function mockChartRenderingAgentResponse(analysisData: string): string {
  const lowerInput = analysisData.toLowerCase();
  let chartType = 'line';
  let chartTitle = '数据可视化';
  
  // Determine chart type based on keywords
  if (lowerInput.includes('占比') || lowerInput.includes('比例') || lowerInput.includes('percentage')) {
    chartType = 'pie';
    chartTitle = '类别占比分析';
  } else if (lowerInput.includes('相关') || lowerInput.includes('关系') || lowerInput.includes('correlation')) {
    chartType = 'scatter';
    chartTitle = '相关性分析';
  } else if (lowerInput.includes('转化') || lowerInput.includes('漏斗') || lowerInput.includes('funnel')) {
    chartType = 'funnel';
    chartTitle = '转化漏斗分析';
  } else if (lowerInput.includes('雷达') || lowerInput.includes('多维') || lowerInput.includes('radar')) {
    chartType = 'radar';
    chartTitle = '多维度分析';
  } else if (lowerInput.includes('热力') || lowerInput.includes('密度') || lowerInput.includes('heat')) {
    chartType = 'heatmap';
    chartTitle = '热力图分析';
  } else if (lowerInput.includes('累计') || lowerInput.includes('area')) {
    chartType = 'area';
    chartTitle = '累计趋势分析';
  } else if (lowerInput.includes('柱状') || lowerInput.includes('类别比较') || lowerInput.includes('bar')) {
    chartType = 'bar';
    chartTitle = '类别比较分析';
  } else {
    chartType = 'line';
    chartTitle = '趋势分析';
  }
  
  // Extract table name if present
  const tableNameMatch = analysisData.match(/表\s+(\w+)/) || 
                           analysisData.match(/数据源(?:是|为)?\s*(\w+)/) ||
                           analysisData.match(/来源(?:于|是)?\s*(\w+)/);
  
  const tableName = tableNameMatch ? tableNameMatch[1] : 'data_table';
  
  // Extract potential field names
  const fieldRegex = /["|'|「|」|【|】](\w+)["|'|「|」|【|】]/g;
  const potentialFields = [];
  let match;
  
  while ((match = fieldRegex.exec(analysisData)) !== null) {
    potentialFields.push(match[1]);
  }
  
  // If no fields were found with regex, extract words that might be fields
  if (potentialFields.length < 3) {
    const words = analysisData.split(/[\s,，.。:：]+/);
    for (const word of words) {
      if (word.length > 1 && /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(word)) {
        potentialFields.push(word);
      }
    }
  }
  
  // Ensure we have at least some fields
  const fields = potentialFields.length > 0 ? 
    [...new Set(potentialFields)].slice(0, 5) : 
    ['category', 'month', 'value', 'name', 'count'];
  
  // Create a chart configuration based on chart type
  let chartConfig;
  
  switch (chartType) {
    case 'pie':
      chartConfig = {
        type: chartType,
        dataSource: {
          table: tableName,
          field: fields
        },
        dimensions: [
          {
            field: fields[0] || 'category',
            name: '类别'
          }
        ],
        measures: [
          {
            field: fields[1] || 'value',
            name: '数值'
          }
        ],
        config: {
          title: chartTitle,
          height: 350
        }
      };
      break;
      
    case 'scatter':
      chartConfig = {
        type: chartType,
        dataSource: {
          table: tableName,
          field: fields
        },
        dimensions: [
          {
            field: fields[0] || 'x',
            name: 'X轴'
          }
        ],
        measures: [
          {
            field: fields[1] || 'y',
            name: 'Y轴'
          }
        ],
        series: fields.length > 2 ? {
          field: fields[2],
          name: '系列'
        } : undefined,
        config: {
          title: chartTitle,
          height: 400
        }
      };
      break;
      
    case 'radar':
      chartConfig = {
        type: chartType,
        dataSource: {
          table: tableName,
          field: fields
        },
        dimensions: [
          {
            field: fields[0] || 'category',
            name: '类别'
          }
        ],
        measures: fields.slice(1, 5).map((field, index) => ({
          field,
          name: `指标${index + 1}`
        })),
        config: {
          title: chartTitle,
          height: 400
        }
      };
      break;
      
    default:
      // For line, bar, area, heatmap, funnel
      chartConfig = {
        type: chartType,
        dataSource: {
          table: tableName,
          field: fields
        },
        dimensions: [
          {
            field: fields[0] || 'category',
            name: '维度'
          }
        ],
        measures: [
          {
            field: fields[1] || 'value',
            name: '数值'
          }
        ],
        series: fields.length > 2 ? {
          field: fields[2],
          name: '系列'
        } : undefined,
        config: {
          title: chartTitle,
          height: 350
        }
      };
  }
  
  return JSON.stringify(chartConfig, null, 2);
}

/**
 * Generates test data for a specific chart configuration
 * 
 * @param chartProps Chart configuration
 * @returns Generated test data
 */
export function generateTestDataForChart(chartProps: ChartProps): any[] {
  const { type, dimensions, measures, series } = chartProps;
  const sampleSize = 10;
  const result = [];
  
  // Helper function to generate random values
  const randomValue = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min;
  const randomPercentage = () => randomValue(1, 100);
  
  // Generate dimension values
  const dimensionValues = dimensions.map(dim => {
    if (dim.name.includes('月') || dim.field.includes('month')) {
      return Array.from({ length: 12 }, (_, i) => `${i + 1}月`);
    }
    if (dim.name.includes('类别') || dim.name.includes('产品') || dim.field.includes('category')) {
      return ['电子产品', '家居用品', '服装', '食品', '其他'];
    }
    if (dim.name.includes('区域') || dim.field.includes('region')) {
      return ['北区', '南区', '东区', '西区'];
    }
    if (dim.name.includes('阶段') || dim.field.includes('stage')) {
      return ['浏览网站', '加入购物车', '开始结账', '完成支付', '复购'];
    }
    if (dim.name.includes('年龄') || dim.field.includes('age')) {
      return ['18-24岁', '25-34岁', '35-44岁', '45-54岁', '55-64岁', '65岁以上'];
    }
    return Array.from({ length: sampleSize }, (_, i) => `选项${i + 1}`);
  });
  
  // Generate series values if applicable
  const seriesValues = series 
    ? series.name.includes('渠道') || series.field.includes('channel')
      ? ['自然搜索', '社交媒体', '直接访问']
      : series.name.includes('类别') || series.field.includes('category')
        ? ['电子产品', '家居用品', '服装', '食品']
        : series.name.includes('区域') || series.field.includes('region')
          ? ['北区', '南区', '东区', '西区']
          : Array.from({ length: 3 }, (_, i) => `系列${i + 1}`)
    : null;
  
  // Generate data based on chart type
  switch (type) {
    case 'pie':
      // For pie charts, we need category and value pairs
      return dimensionValues[0].map(dimValue => {
        const entry: any = {
          [dimensions[0].field]: dimValue,
          [measures[0].field]: randomValue(100, 1000)
        };
        return entry;
      });
      
    case 'funnel':
      // For funnel charts, we typically have decreasing values
      return dimensionValues[0].map((dimValue, index) => {
        const baseValue = 1000;
        const decreaseFactor = 0.7; // Each step retains 70% of previous
        const value = Math.round(baseValue * Math.pow(decreaseFactor, index));
        const entry: any = {
          [dimensions[0].field]: dimValue,
          [measures[0].field]: value
        };
        return entry;
      });
      
    case 'radar':
      // For radar charts, we need multiple measures for each dimension
      if (dimensionValues[0] && measures.length > 1) {
        return dimensionValues[0].map(dimValue => {
          const entry: any = {
            [dimensions[0].field]: dimValue
          };
          measures.forEach(measure => {
            entry[measure.field] = randomValue(50, 100);
          });
          return entry;
        });
      }
      break;
      
    case 'scatter':
      // For scatter plots, we need x, y coordinates and optional series
      if (seriesValues) {
        const result: any[] = [];
        for (const serVal of seriesValues) {
          for (let i = 0; i < sampleSize; i++) {
            const entry: any = {
              [dimensions[0].field]: randomValue(100, 1000),
              [measures[0].field]: randomValue(100, 1000),
              [series.field]: serVal
            };
            result.push(entry);
          }
        }
        return result;
      } else {
        return Array.from({ length: sampleSize }, () => ({
          [dimensions[0].field]: randomValue(100, 1000),
          [measures[0].field]: randomValue(100, 1000)
        }));
      }
      
    case 'heatmap':
      // For heatmaps, we need a grid of values
      if (dimensions.length >= 2) {
        const dim1Values = dimensionValues[0] || ['A', 'B', 'C', 'D'];
        const dim2Values = dimensionValues[1] || ['1', '2', '3', '4'];
        
        const result: any[] = [];
        for (const val1 of dim1Values) {
          for (const val2 of dim2Values) {
            const entry: any = {
              [dimensions[0].field]: val1,
              [dimensions[1].field]: val2,
              [measures[0].field]: randomValue(1, 100)
            };
            result.push(entry);
          }
        }
        return result;
      }
      break;
      
    default:
      // For line, bar, area charts
      if (seriesValues) {
        // For charts with series
        const result: any[] = [];
        for (const dimValue of dimensionValues[0]) {
          for (const serValue of seriesValues) {
            const entry: any = {
              [dimensions[0].field]: dimValue,
              [series.field]: serValue
            };
            measures.forEach(measure => {
              entry[measure.field] = randomValue(100, 1000);
            });
            result.push(entry);
          }
        }
        return result;
      } else {
        // For charts without series
        return dimensionValues[0].map(dimValue => {
          const entry: any = {
            [dimensions[0].field]: dimValue
          };
          measures.forEach(measure => {
            entry[measure.field] = randomValue(100, 1000);
          });
          return entry;
        });
      }
  }
  
  // Default fallback
  return Array.from({ length: sampleSize }, (_, i) => ({
    dimension: `Dimension ${i + 1}`,
    value: randomValue(100, 1000)
  }));
}

/**
 * Integrates with the Chart Rendering Agent API
 * 
 * @param agentApi The base URL of the chart rendering agent API
 * @param analysisData The data analysis to visualize
 * @returns Promise resolving to chart props
 */
export async function integrateWithChartRenderingAgent(
  agentApi: string,
  analysisData: string
): Promise<ChartProps | null> {
  try {
    // Actual API call would be here
    const response = await fetch(`${agentApi}/render-chart`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        analysisData,
        // You could include additional parameters here
        format: 'json',
        version: '1.0'
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Chart rendering agent API error: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Process the agent's response
    return processChartAgentOutput(result.output);
  } catch (error) {
    console.error('Error integrating with chart rendering agent:', error);
    // Fallback to mock response if API fails
    return callChartRenderingAgent(analysisData);
  }
}
