/**
 * Chart data transformer utility
 * Converts raw database data into chart-specific formats
 */
import type { ChartType, FieldConfig } from '@/types/chart';

/**
 * Transform raw database data into the format required by each chart type
 * 
 * @param data Raw data from database
 * @param chartType Type of chart to format for
 * @param dimensions Dimension fields configuration
 * @param measures Measure fields configuration
 * @param series Optional series field configuration
 * @returns Formatted data for chart visualization
 */
export function transformChartData(
  data: any[],
  chartType: ChartType,
  dimensions: FieldConfig[],
  measures: FieldConfig[],
  series?: FieldConfig
): any {
  if (!data || data.length === 0) {
    return [];
  }
  
  // Handle different chart types with appropriate formatting
  switch (chartType) {
    case 'line':
    case 'bar':
    case 'area':
      return transformCategoryChart(data, dimensions, measures, series);
      
    case 'pie':
      return transformPieChart(data, dimensions[0], measures[0]);
      
    case 'scatter':
      return transformScatterChart(data, dimensions[0], measures[0], series);
      
    case 'heatmap':
      return transformHeatmapChart(data, dimensions, measures);
      
    case 'radar':
      return transformRadarChart(data, dimensions, measures, series);
      
    case 'funnel':
      return transformFunnelChart(data, dimensions[0], measures[0]);
      
    default:
      // Default to simple array return if type is not recognized
      return data;
  }
}

/**
 * Transform data for category-based charts (line, bar, area)
 */
function transformCategoryChart(
  data: any[],
  dimensions: FieldConfig[],
  measures: FieldConfig[],
  series?: FieldConfig
): any {
  const dimensionField = dimensions[0].field;
  
  if (series?.field) {
    // With series: create multi-series data
    const groupedData = groupDataBySeries(data, dimensionField, measures, series);
    return groupedData;
  } else {
    // Without series: simple category chart
    return data.map(row => {
      const entry: any = { [dimensionField]: row[dimensionField] };
      measures.forEach(measure => {
        entry[measure.name] = row[measure.field];
      });
      return entry;
    });
  }
}

/**
 * Group data by series for multi-series charts
 */
function groupDataBySeries(
  data: any[],
  dimensionField: string,
  measures: FieldConfig[],
  series: FieldConfig
): any[] {
  // Get unique dimension values and series values
  const dimensionValues = [...new Set(data.map(item => item[dimensionField]))];
  const seriesValues = [...new Set(data.map(item => item[series.field]))];
  
  // Create a lookup map for quick access to data
  const dataMap: Record<string, Record<string, number>> = {};
  
  data.forEach(row => {
    const dimValue = String(row[dimensionField]);
    const seriesValue = String(row[series.field]);
    
    if (!dataMap[dimValue]) {
      dataMap[dimValue] = {};
    }
    
    measures.forEach(measure => {
      dataMap[dimValue][`${seriesValue}_${measure.field}`] = row[measure.field];
    });
  });
  
  // Convert to array format expected by charts
  return dimensionValues.map(dimValue => {
    const entry: any = { [dimensionField]: dimValue };
    
    seriesValues.forEach(serValue => {
      measures.forEach(measure => {
        const key = `${serValue}_${measure.field}`;
        entry[serValue] = dataMap[dimValue]?.[key] ?? 0;
      });
    });
    
    return entry;
  });
}

/**
 * Transform data for pie charts
 */
function transformPieChart(
  data: any[],
  dimension: FieldConfig,
  measure: FieldConfig
): any {
  return data.map(row => ({
    name: row[dimension.field],
    value: row[measure.field]
  }));
}

/**
 * Transform data for scatter charts
 */
function transformScatterChart(
  data: any[],
  dimension: FieldConfig,
  measure: FieldConfig,
  series?: FieldConfig
): any {
  if (series?.field) {
    // Group by series for different scatter groups
    const seriesGroups: Record<string, any[]> = {};
    
    data.forEach(row => {
      const seriesValue = String(row[series.field]);
      
      if (!seriesGroups[seriesValue]) {
        seriesGroups[seriesValue] = [];
      }
      
      seriesGroups[seriesValue].push({
        x: row[dimension.field],
        y: row[measure.field],
        // Include original data for tooltip or click events
        original: { ...row }
      });
    });
    
    return Object.entries(seriesGroups).map(([name, points]) => ({
      name,
      data: points
    }));
  } else {
    // Simple scatter without series grouping
    return data.map(row => ({
      x: row[dimension.field],
      y: row[measure.field],
      original: { ...row }
    }));
  }
}

/**
 * Transform data for heatmap charts
 */
function transformHeatmapChart(
  data: any[],
  dimensions: FieldConfig[],
  measures: FieldConfig[]
): any {
  if (dimensions.length < 2) {
    // Heatmaps need at least two dimensions
    return data;
  }
  
  const xField = dimensions[0].field;
  const yField = dimensions[1].field;
  const valueField = measures[0].field;
  
  // Extract unique x and y values to create the grid
  const xValues = [...new Set(data.map(item => item[xField]))];
  const yValues = [...new Set(data.map(item => item[yField]))];
  
  // Create lookup for data values
  const dataLookup: Record<string, number> = {};
  data.forEach(item => {
    const key = `${item[xField]}_${item[yField]}`;
    dataLookup[key] = item[valueField];
  });
  
  // Transform into heatmap format [x, y, value]
  const heatmapData = [];
  for (let i = 0; i < xValues.length; i++) {
    for (let j = 0; j < yValues.length; j++) {
      const x = xValues[i];
      const y = yValues[j];
      const key = `${x}_${y}`;
      const value = dataLookup[key] || 0;
      
      heatmapData.push([i, j, value]);
    }
  }
  
  return {
    data: heatmapData,
    xAxis: xValues,
    yAxis: yValues
  };
}

/**
 * Transform data for radar charts
 */
function transformRadarChart(
  data: any[],
  dimensions: FieldConfig[],
  measures: FieldConfig[],
  series?: FieldConfig
): any {
  // Radar charts need indicators (the "spokes") and series (the plotted shapes)
  const indicators = measures.map(measure => ({
    name: measure.name,
    max: Math.max(...data.map(item => item[measure.field])) * 1.2 // Add 20% padding
  }));
  
  if (series?.field) {
    // Group by series for different radar shapes
    const seriesGroups: Record<string, any> = {};
    
    data.forEach(row => {
      const seriesValue = String(row[series.field]);
      
      if (!seriesGroups[seriesValue]) {
        seriesGroups[seriesValue] = {
          name: seriesValue,
          value: measures.map(measure => row[measure.field])
        };
      }
    });
    
    return {
      indicators,
      series: Object.values(seriesGroups)
    };
  } else {
    // If no series provided, assume each row is a separate radar shape
    return {
      indicators,
      series: data.map(row => ({
        name: row[dimensions[0].field],
        value: measures.map(measure => row[measure.field])
      }))
    };
  }
}

/**
 * Transform data for funnel charts
 */
function transformFunnelChart(
  data: any[],
  dimension: FieldConfig,
  measure: FieldConfig
): any {
  // Sort data by measure value in descending order for typical funnel display
  return data
    .map(row => ({
      name: row[dimension.field],
      value: row[measure.field]
    }))
    .sort((a, b) => b.value - a.value);
}
