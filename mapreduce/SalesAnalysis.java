import java.io.IOException;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.mapreduce.lib.input.*;
import org.apache.hadoop.mapreduce.lib.output.*;

public class SalesAnalysis {
    public static class SalesMapper extends Mapper<LongWritable, Text, Text, DoubleWritable> {
        public void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String line = value.toString();
            if (line.startsWith("Date") || line.trim().isEmpty()) return;
            String[] cols = line.split(",");
            if (cols.length < 15) return;
            try {
                String category = cols[3].trim();
                double unitsSold = Double.parseDouble(cols[6].trim());
                double price = Double.parseDouble(cols[9].trim());
                double discount = Double.parseDouble(cols[10].trim());
                double revenue = unitsSold * price * (1 - discount / 100);
                context.write(new Text(category), new DoubleWritable(revenue));
            } catch (Exception e) {}
        }
    }

    public static class SalesReducer extends Reducer<Text, DoubleWritable, Text, Text> {
        public void reduce(Text key, Iterable<DoubleWritable> values, Context context)
                throws IOException, InterruptedException {
            double totalRevenue = 0;
            for (DoubleWritable val : values) {
                totalRevenue += val.get();
            }
            String result = String.format("Total Revenue = %.2f", totalRevenue);
            context.write(key, new Text(result));
        }
    }

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "Sales Analysis");
        job.setJarByClass(SalesAnalysis.class);
        job.setMapperClass(SalesMapper.class);
        job.setReducerClass(SalesReducer.class);
        job.setNumReduceTasks(3);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(DoubleWritable.class);
        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));
        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}
