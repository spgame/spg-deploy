FROM python:3.4-onbuild
ENV APP_CONFIG_FILE config/release.py
EXPOSE 8080
COPY app.sh /
RUN chmod +x /app.sh 
CMD /app.sh