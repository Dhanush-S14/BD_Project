import java.io.IOException;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.mapreduce.lib.input.*;
import org.apache.hadoop.mapreduce.lib.output.*;

public class StockAnalysis {
    public static class StockMapper extends Mapper<LongWritable, Text, Text, DoubleWritable> {
        public void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String line = value.toString();
            if (line.startsWith("Date") || line.trim().isEmpty()) return;
            String[] cols = line.split(",");
            if (cols.length < 15) return;
            try {
                String productId = cols[2].trim();
                double inventory = Double.parseDouble(cols[5].trim());
                double demand = Double.parseDouble(cols[8].trim());
                double gap = inventory - demand;
                context.write(new Text(productId), new DoubleWritable(gap));
            } catch (Exception e) {}
        }
    }

    public static class StockReducer extends Reducer<Text, DoubleWritable, Text, Text> {
        public void reduce(Text key, Iterable<DoubleWritable> values, Context context)
                throws IOException, InterruptedException {
            double totalGap = 0;
            int count = 0;
            for (DoubleWritable val : values) {
                totalGap += val.get();
                count++;
            }
            double avgGap = totalGap / count;
            String status;
            if (avgGap < 0) status = "Understock";
            else if (avgGap > 0) status = "Overstock";
            else status = "Balanced";
            String result = String.format("Avg Gap = %.2f (%s)", avgGap, status);
            context.write(key, new Text(result));
        }
    }

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "Stock Analysis");
        job.setJarByClass(StockAnalysis.class);
        job.setMapperClass(StockMapper.class);
        job.setReducerClass(StockReducer.class);
        job.setNumReduceTasks(3);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(DoubleWritable.class);
        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));
        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}
