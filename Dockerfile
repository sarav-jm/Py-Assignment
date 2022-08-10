FROM python:3.9-slim

USER root
RUN apt-get update && \
    apt-get install -y g++ unixodbc unixodbc-dev gnupg software-properties-common curl sudo tk


ARG UNAME=absolute
ARG UID=1001
ARG GID=1001
ENV HOME=/home/$UNAME
ENV PATH="$HOME/.local/bin:$PATH"
RUN groupadd -g $UID -o $UNAME
RUN useradd -m -u $UID -g $GID -o -s /bin/bash $UNAME
RUN usermod -aG sudo $UNAME
#RUN echo "$UNAME:$UNAME" | chpasswd
USER $UNAME

COPY requirements.txt $HOME/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r $HOME/requirements.txt --user

COPY config/jupyter_lab_config.json $HOME/.jupyter/jupyter_lab_config.json

#RUN echo "$UNAME" | sudo -S chown -R $UNAME:$UNAME $HOME
#
#RUN echo "$UNAME" | sudo -S apt-get clean autoclean && sudo apt-get autoremove --yes && rm -rf /var/lib/{apt,dpkg,cache,log}/
