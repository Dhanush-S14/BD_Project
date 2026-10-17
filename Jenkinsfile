pipeline {
    agent any
    triggers { pollSCM('H/2 * * * *') }

    stages {
        stage('Start Cluster') {
            steps {
                sh 'docker start namenode datanode1 datanode2 datanode3'
                sh 'sleep 5'
                sh 'docker exec namenode start-dfs.sh || true'
                sh 'docker exec namenode start-yarn.sh || true'
            }
        }
        stage('Prepare HDFS') {
            steps {
                sh 'sleep 15'
                sh 'docker exec namenode hdfs dfsadmin -safemode wait'
                sh 'docker exec namenode hdfs dfs -rm -r -f /user/sales/output'
                sh 'docker exec namenode hdfs dfs -mkdir -p /user/sales/input'
                sh 'docker cp sales_dataset.csv namenode:/opt/results/sales_dataset.csv'
                sh 'docker exec namenode hdfs dfs -put -f /opt/results/sales_dataset.csv /user/sales/input/'
            }
        }
        stage('Build') {
            steps {
                sh 'docker cp mapreduce/. namenode:/opt/mapreduce/'
                sh 'docker cp scripts/. namenode:/opt/results/'
                sh '''docker exec namenode bash -c 'cd /opt/mapreduce &&
                    javac -classpath $(hadoop classpath) SalesAnalysis.java && jar -cf SalesAnalysis.jar SalesAnalysis*.class &&
                    javac -classpath $(hadoop classpath) StockAnalysis.java && jar -cf StockAnalysis.jar StockAnalysis*.class' '''
            }
        }
        stage('Run MapReduce') {
            steps {
                sh 'docker exec namenode hadoop jar /opt/mapreduce/SalesAnalysis.jar SalesAnalysis /user/sales/input /user/sales/output/sales'
                sh 'docker exec namenode hadoop jar /opt/mapreduce/StockAnalysis.jar StockAnalysis /user/sales/input /user/sales/output/stock'
            }
        }
        stage('Generate Reports') {
            steps {
                sh '''docker exec namenode bash -c "hdfs dfs -cat '/user/sales/output/sales/part-r-*' > /opt/results/sales_final.txt"'''
                sh '''docker exec namenode bash -c "hdfs dfs -cat '/user/sales/output/stock/part-r-*' > /opt/results/stock_final.txt"'''
                sh 'docker exec namenode python3 /opt/results/generate_sales_stock_csv.py'
                sh 'docker exec namenode python3 /opt/results/generate_sales_report.py'
                sh 'docker exec namenode python3 /opt/results/send_sales_report.py'
            }
        }
        stage('Copy Results') {
            steps {
                sh '''mkdir -p Results
                for f in sales_final.txt stock_final.txt sales_analysis.csv stock_analysis.csv sales_report.pdf; do
                    docker cp namenode:/opt/results/$f Results/
                done'''
                archiveArtifacts artifacts: 'Results/*', allowEmptyArchive: true
            }
        }
    }
    post {
        always {
            sh 'docker exec namenode stop-yarn.sh || true'
            sh 'docker exec namenode stop-dfs.sh || true'
            sh 'docker stop namenode datanode1 datanode2 datanode3 || true'
        }
    }
}
