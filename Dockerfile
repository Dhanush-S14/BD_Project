FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
      openjdk-11-jdk openssh-server openssh-client wget vim procps python3 python3-pip \
    && pip3 install reportlab \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://archive.apache.org/dist/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz \
    && tar -xzf hadoop-3.3.6.tar.gz -C /opt && mv /opt/hadoop-3.3.6 /opt/hadoop \
    && rm hadoop-3.3.6.tar.gz

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV PATH=$PATH:/opt/hadoop/bin:/opt/hadoop/sbin

# Run daemons as root + cap daemon heaps
RUN echo "export JAVA_HOME=$JAVA_HOME" >> $HADOOP_CONF_DIR/hadoop-env.sh && \
    echo "export HDFS_NAMENODE_USER=root"          >> $HADOOP_CONF_DIR/hadoop-env.sh && \
    echo "export HDFS_DATANODE_USER=root"          >> $HADOOP_CONF_DIR/hadoop-env.sh && \
    echo "export HDFS_SECONDARYNAMENODE_USER=root" >> $HADOOP_CONF_DIR/hadoop-env.sh && \
    echo "export YARN_RESOURCEMANAGER_USER=root"   >> $HADOOP_CONF_DIR/hadoop-env.sh && \
    echo "export YARN_NODEMANAGER_USER=root"       >> $HADOOP_CONF_DIR/hadoop-env.sh && \
    echo "export HADOOP_HEAPSIZE_MAX=512m"         >> $HADOOP_CONF_DIR/hadoop-env.sh && \
    echo "export YARN_RESOURCEMANAGER_HEAPSIZE=512" >> $HADOOP_CONF_DIR/yarn-env.sh && \
    echo "export YARN_NODEMANAGER_HEAPSIZE=512"     >> $HADOOP_CONF_DIR/yarn-env.sh

# Passwordless SSH: same key baked into every node
RUN mkdir -p /var/run/sshd /root/.ssh /opt/results /opt/mapreduce && \
    ssh-keygen -t rsa -P '' -f /root/.ssh/id_rsa && \
    cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys && \
    chmod 600 /root/.ssh/authorized_keys && \
    echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

COPY conf/ /opt/hadoop/etc/hadoop/

CMD service ssh start && tail -f /dev/null
