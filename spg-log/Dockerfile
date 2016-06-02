FROM python:3.4-onbuild
ENV APP_CONFIG_FILE config/release.py
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
EXPOSE 8080
CMD [ "python", "./app.py" ]
