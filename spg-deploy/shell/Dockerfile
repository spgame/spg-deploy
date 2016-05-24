#FROM tomcat:8-jre8
FROM tomcat_with_oracle_jdk
RUN rm -rf /usr/local/tomcat/webapps/ROOT
ADD ROOT.war /usr/local/tomcat/webapps/ROOT.war
